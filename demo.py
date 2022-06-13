#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ast import parse
import cv2, sys, os, logging, time, argparse
from init_i.utils import Json, Draw
from init_i.utils.logger import config_logger
from init_i.web.ai.pipeline import Source
from init_i.app.handler import get_application

def main(args):
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
        # ---------------------------Check model architecture-------------------------------------------------------
            if 'obj' in dev_cfg[prim_ind]['tag']:
                from init_i.obj import ObjectDetection as trg
                # ---------------------------Check secondary model and loading-------------------------
                # Get secondary model relative parameter from first json
                seconlist = [dev_cfg[prim_ind][key] for key in dev_cfg[prim_ind].keys() if "sec" in key]
                
                if seconlist != []:
                    from init_i.cls import Classification as cls
                    for j in range(len(seconlist)):
                        # Append to secondary dictionary relative parameter from secondary model json  
                        seconlist[j].update({"sec-{}".format(j+1):json.read_json(seconlist[j]["model_json"]), "cls":cls()})
                        # Read every cls model
                        model, color_palette = seconlist[j]["cls"].load_model(seconlist[j]["sec-{}".format(j+1)])
                        # Add model and color to secondary dictionary
                        seconlist[j].update({"model":model,"color_palette":color_palette})

            if "cls" in dev_cfg[prim_ind]['tag']:
                from init_i.cls import Classification as trg

            if "seg" in dev_cfg[prim_ind]['tag']:
                from init_i.seg import Segmentation as trg

            if "pose" in dev_cfg[prim_ind]['tag']:
                from init_i.pose import Pose as trg
                
        # ---------------------------Check input is camera or image and initial frame id/show id----------------------------------------
            src = Source(dev_cfg[prim_ind]['source'], dev_cfg[prim_ind]['source_type'])

        # ---------------------------Load model and initial pipeline--------------------------------------------------------------------
            trg = trg()  
            model, color_palette = trg.load_model(dev_cfg[prim_ind]) if not ("pose" in dev_cfg[prim_ind]['tag']) else trg.load_model(dev_cfg[prim_ind], src.get_frame()[1])

            has_application=True
            try:
                application = get_application(dev_cfg[prim_ind])
            except Exception as e:
                logging.error(e)
                has_application=False
        # ---------------------------Inference---------------------------------------------------------------------------------------------
            logging.info('Starting inference...')
            print("To close the application, press 'CTRL+C' here or switch to the output window and press ESC key")
            
            while True:
                ret_frame, frame = src.get_frame()
                info = trg.inference(model, frame, dev_cfg[prim_ind])
                
        # ---------------------------Drawing detecter to information-----------------------------------------------------------------------
                if info is not None:
                    if not has_application:
                        frame = draw.draw_detections(info, color_palette, dev_cfg[prim_ind])
                    else:
                        frame = application(frame, info)
                else:
                    continue
        # ---------------------------Show--------------------------------------------------------------------------------------------------              
                if not args.server:
                    cv2.imshow('Detection Results', frame)
                
                    if cv2.waitKey(1) in {ord('q'), ord('Q'), '27'}:
                        break
                else:
                    if input('Enter q to leave:') in ['Q', 'q']:
                        break
            src.release()

if __name__ == '__main__':
    config_logger('./VINO.log', 'w', "info")
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help = "The path of application config")
    parser.add_argument('-s', '--server', action="store_true", help = "Server mode, not to display the opencv windows")
    args = parser.parse_args()

    sys.exit(main(args) or 0)