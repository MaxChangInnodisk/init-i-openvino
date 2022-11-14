#!/usr/bin/python3
# -*- coding: utf-8 -*-
import cv2, sys, os, logging, time, argparse, math
from collections import deque

from ivit_i.utils import Draw, draw_text, read_json
from ivit_i.utils.draw_tools import draw_fps
from ivit_i.utils.logger import config_logger
from ivit_i.common.pipeline import Source, Pipeline
from ivit_i.app.handler import get_application
from ivit_i.utils import handle_exception, get_display

from ivit_i.app.common import CV_WIN

FULL_SCREEN     = False
FRMAEWORK       = "framework"
TAG             = "tag"
FRAMEWORK       = "openvino"
WAIT_KEY_TIME   = 1

SERV    = 'server'
RTSP    = 'rtsp'
GUI     = 'gui'

def init_cv_win():
    logging.info('Init Display Window')
    cv2.namedWindow( CV_WIN, cv2.WND_PROP_FULLSCREEN )
    cv2.setWindowProperty( CV_WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN )

def fullscreen_toggle():
    global FULL_SCREEN
    cv2.setWindowProperty( 
        CV_WIN, cv2.WND_PROP_FULLSCREEN, 
        cv2.WINDOW_FULLSCREEN if FULL_SCREEN else cv2.WINDOW_NORMAL )
    FULL_SCREEN = not FULL_SCREEN

def display(frame, t_wait_key):

    exit_flag = False

    cv2.imshow(CV_WIN, frame)            
    
    key = cv2.waitKey(t_wait_key)
    if key in {ord('q'), ord('Q'), 27}:
        exit_flag = True
    elif key in { ord('a'), 201, 206, 210, 214 }:
        fullscreen_toggle()

    return exit_flag

def get_api(key):
    # Check model architecture
    if 'obj' in key:
        from ivit_i.obj import ObjectDetection as trg

    if "cls" in key:
        from ivit_i.cls import Classification as trg

    if "seg" in key:
        from ivit_i.seg import Segmentation as trg

    if "pose" in key:
        from ivit_i.pose import Pose as trg

    return trg()

def get_running_mode(args):
    if(args.server): return SERV
    elif(args.rtsp): return RTSP
    else: return GUI

def main(args):

    # Get Mode
    mode = get_running_mode(args)

    t_wait_key  = 0 if args.debug else WAIT_KEY_TIME

    # Get to relative parameter from first json
    app_cfg = read_json(args.config)
    dev_cfg = app_cfg['prim']
    app_cfg.update( read_json(dev_cfg['model_json']) )

    # Check is openvino and start processes
    trg = get_api(app_cfg[TAG])
        
    # Check input is camera or image and initial frame id/show id
    src = Pipeline(app_cfg['source'], app_cfg['source_type'])
    src.start()

    (src_hei, src_wid), src_fps = src.get_shape(), src.get_fps()
    # Concate RTSP pipeline

    if mode==RTSP:
        gst_pipeline = 'appsrc is-live=true block=true ' + \
            ' ! videoconvert ' + \
            ' ! video/x-raw,format=I420 ' + \
            ' ! x264enc speed-preset=ultrafast bitrate=2048 key-int-max=25' + \
            f' ! rtspclientsink location=rtsp://{args.ip}:{args.port}{args.name}'
        out = cv2.VideoWriter(  gst_pipeline, cv2.CAP_GSTREAMER, 0, 
                                src_fps, (src_wid, src_hei), True )

        logging.info(f'Define Gstreamer Pipeline: {gst_pipeline}')
        if not out.isOpened():
            raise Exception("can't open video writer")

    # Load model and initial pipeline
    trg.load_model(app_cfg, src.read()[1])

    # Setup Application
    try:
        application = get_application(app_cfg)
        
        # area_detection have to setup area
        if get_display():
            application.set_area(frame=src.read()[1])

    except Exception as e:
        raise Exception(handle_exception(error=e, title="Could not load application ... set app to None"))

    # Inference
    logging.info('Starting inference...')
    cur_info, temp_info    = None, None
    cur_fps , temp_fps     = 30, 30

    try:    
        # Setup CV Windows
        if mode==GUI: init_cv_win()

        while(True):
            
            t_start = time.time()
            
            # Get current frame
            success, frame = src.read()
            
            # Check frame
            if not success:
                if src.get_type() == 'v4l2':
                    break
                else:
                    application.reset()
                    src.reload()
                    continue

            # Do inference
            temp_info = trg.inference(frame, args.mode)
            
            # Drawing result using application
            if(temp_info):
                cur_info, cur_fps = temp_info, temp_fps

            if(cur_info):
                frame, app_info = application(frame, cur_info)
            
            # Draw fps
            frame = draw_fps( frame, cur_fps )

            # Display Frame
            if mode==GUI:
                exit_win = display(frame, t_wait_key)
                if exit_win: break

            elif mode==RTSP:
                out.write(frame)

            # Log
            # if(app_info): logging.cur_info(app_info)

            # Delay to fix in 30 fps
            t_cost, t_expect = (time.time()-t_start), (1/src.get_fps())
            if(t_cost<t_expect):
                time.sleep(t_expect-t_cost)

            # Calculate FPS
            if(temp_info):
                temp_fps = int(1/(time.time()-t_start))
        
        src.release()

    except Exception as e:
        logging.error(handle_exception(e))
    
    finally:
        sys.exit(0)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help = "The path of application config")
    parser.add_argument('-s', '--server', action="store_true", help = "Server mode, not to display the opencv windows")
    parser.add_argument('-r', '--rtsp', action="store_true", help = "RTSP mode, not to display the opencv windows")
    parser.add_argument('-d', '--debug', action="store_true", help = "Debug mode")
    parser.add_argument('-m', '--mode', type=int, default = 1, help = "Select sync mode or async mode{ 0: sync, 1: async }")
    parser.add_argument('-i', '--ip', type=str, default = '127.0.0.1', help = "The ip address of RTSP uri")
    parser.add_argument('-p', '--port', type=str, default = '8554', help = "The port number of RTSP uri")
    parser.add_argument('-n', '--name', type=str, default = '/mystream', help = "The name of RTSP uri")

    args = parser.parse_args()

    sys.exit(main(args) or 0)