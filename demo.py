#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ast import parse
from copy import deepcopy
import cv2, sys, os, logging, time, argparse
from ivit_i.utils import Json, Draw
from ivit_i.utils.logger import config_logger
from ivit_i.web.ai.pipeline import Source
from ivit_i.app.handler import get_application
from ivit_i.web.tools.common import handle_exception
import math

FONT_FACE       = cv2.FONT_HERSHEY_COMPLEX_SMALL
BORDER_FACE     = cv2.LINE_AA
FONT_SCALE      = 2e-3  # Adjust for larger font size in all images
THICKNESS_SCALE = 1e-3  # Adjust for larger thickness in all images

CV_WIN          = "Detection Results"
FULL_SCREEN     = True

alpha_slider_max = 100
thres = 0

def on_trackbar(val):
    global thres
    thres = float(val/alpha_slider_max)

def main(args):
    global FULL_SCREEN

    # Instantiation
    json = Json()
    draw = Draw()

    # Get to relative parameter from first json
    custom_cfg = json.read_json(args.config)
    dev_cfg = [custom_cfg[key] for key in custom_cfg.keys() if "prim" in key]

    # Summarized previous dictionary and get to relative parameter from secondary json  
    for prim_ind in range(len(dev_cfg)):

        # source append to dev_cfg
        dev_cfg[prim_ind].update({"source":custom_cfg['source']})
        dev_cfg[prim_ind].update({"source_type":custom_cfg['source_type']})
        dev_cfg[prim_ind].update({"application":custom_cfg['application']})
        dev_cfg[prim_ind].update(json.read_json(dev_cfg[prim_ind]['model_json']))

        # Check is openvino and start processes
        if custom_cfg['framework'] == 'openvino':

            # Check model architecture
            if 'obj' in dev_cfg[prim_ind]['tag']:
                from ivit_i.obj import ObjectDetection as trg

                # Check secondary model and loading
                #   - Get secondary model relative parameter from first json
                seconlist = [dev_cfg[prim_ind][key] for key in dev_cfg[prim_ind].keys() if "sec" in key]
                
                if seconlist != []:
                    from ivit_i.cls import Classification as cls
                    for j in range(len(seconlist)):
                        # Append to secondary dictionary relative parameter from secondary model json  
                        seconlist[j].update({"sec-{}".format(j+1):json.read_json(seconlist[j]["model_json"]), "cls":cls()})
                        # Read every cls model
                        model, color_palette = seconlist[j]["cls"].load_model(seconlist[j]["sec-{}".format(j+1)])
                        # Add model and color to secondary dictionary
                        seconlist[j].update({"model":model,"color_palette":color_palette})

            if "cls" in dev_cfg[prim_ind]['tag']:
                from ivit_i.cls import Classification as trg

            if "seg" in dev_cfg[prim_ind]['tag']:
                from ivit_i.seg import Segmentation as trg

            if "pose" in dev_cfg[prim_ind]['tag']:
                from ivit_i.pose import Pose as trg
    
            # Check input is camera or image and initial frame id/show id
            src = Source(dev_cfg[prim_ind]['source'], dev_cfg[prim_ind]['source_type'])

            # Load model and initial pipeline
            trg = trg()  
            model, color_palette = trg.load_model(dev_cfg[prim_ind]) if not ("pose" in dev_cfg[prim_ind]['tag']) else trg.load_model(dev_cfg[prim_ind], src.get_frame()[1])

            # Setup Application
            has_app=False
            try:
                application = get_application(dev_cfg[prim_ind])
                has_app = False if application == None else True
                
                app_info = dev_cfg[prim_ind]["application"]
                
                # area_detection have to setup area
                if "area" in app_info["name"]:
                    key = "area_points"
                    if not key in app_info: application.set_area(pnts=None, frame=src.get_first_frame())
                    else: application.set_area(pnts=app_info[key])

            except Exception as e:
                handle_exception(error=e, title="Could not load application ... set app to None", exit=False)
                has_app=False

            # Setup CV Windows
            if not args.server:
                cv2.namedWindow( CV_WIN, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty( CV_WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN if FULL_SCREEN else cv2.WINDOW_NORMAL )

            # Inference
            logging.info('Starting inference...')
            logging.warning("To close the application, press 'CTRL+C' here or switch to the output window and press ESC key")
            
            while True:

                # Get current frame
                ret_frame, frame = src.get_frame()
                org_frame = frame.copy()
                t1 = time.time()

                # Check frame is exist
                if not ret_frame: 
                    if src.get_type().lower() in ["rtsp", "video"]:
                        src = Source(total_conf['source'], total_conf['source_type'])
                        continue
                    else:
                        break

                # Update thres
                if thres>0 and (dev_cfg[prim_ind]["openvino"]["thres"] != thres):
                    dev_cfg[prim_ind]["openvino"]["thres"] = thres

                # Do inference
                info = trg.inference(model, org_frame, dev_cfg[prim_ind])
                
                # Drawing detecter to information
                if not args.server:
                    
                    if info is None: continue

                    if not has_app:
                        frame = draw.draw_detections(info, color_palette, dev_cfg[prim_ind])
                    else:
                        frame = application(org_frame, info)            
                
                # Show the results

                # Calculate FPS
                t2              = time.time()
                fps             = f"FPS:{int(1/(t2-t1))}"
                height, width   = frame.shape[:2]
                
                font_scale      = min(width, height) * FONT_SCALE
                thickness       = math.ceil(min(width, height) * THICKNESS_SCALE)
                padding         = 10
                (text_width, text_height), baseLine = cv2.getTextSize(fps, FONT_FACE, font_scale, thickness)
                

                cv2.putText(frame, fps, (width - text_width - padding , text_height + baseLine ), FONT_FACE, font_scale, (0, 0, 0), thickness+2, BORDER_FACE)
                cv2.putText(frame, fps, (width - text_width - padding , text_height + baseLine ), FONT_FACE, font_scale, (0, 255, 255), thickness, BORDER_FACE)

                if not args.server:
                    
                    cv2.imshow(CV_WIN, frame)

                    key = cv2.waitKey(1)
                    if key in {ord('q'), ord('Q'), 27}:
                        break                 
                    elif key in { ord('a'), 201, 206, 210, 214 }:
                        FULL_SCREEN = not FULL_SCREEN
                        cv2.setWindowProperty(CV_WIN,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN if FULL_SCREEN else cv2.WINDOW_NORMAL )
                    elif key in { ord('c'), 32 }:
                        pass

                else:
                    logging.info( info["detections"])
                
            src.release()

if __name__ == '__main__':
    config_logger('./ivit-i.log', 'w', "info")
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help = "The path of application config")
    parser.add_argument('-s', '--server', action="store_true", help = "Server mode, not to display the opencv windows")
    args = parser.parse_args()

    sys.exit(main(args) or 0)