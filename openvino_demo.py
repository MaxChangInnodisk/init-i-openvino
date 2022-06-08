#!/usr/bin/python3
# -*- coding: utf-8 -*-
from ast import parse
import cv2
import sys
import logging
from init_i.vino.utils import Json, Draw
# from init_i.vino.utils import config_logger as log
from init_i.vino.utils.logger import config_logger
import argparse

# Multi_classification_model_inference 
class Multimodel():
    def __init__(self) -> None:
        pass

    # Get to data of appoint from ObjectDetetion reslut list 
    def appoint_class(self, classes):
            return [ [i, element["xmin"],element["ymin"],element["xmax"],element["ymax"]] 
                                        for i, element in enumerate(self.info['detections']) if classes in element["det_label"] ] 

    # Inference main
    def cls_inference(self, frame, info, cls_list):
        self.info = info
        # Get model from model list 
        for index in range(len(cls_list)):
            # Get appoint list from reslut list
            appoint_list = self.appoint_class(cls_list[index]["class"])
            # Get obj to inference
            for obj in appoint_list:
                cls_info = cls_list[index]["cls"].inference(cls_list[index]["model"], 
                                frame[obj[2]:obj[4],obj[1]:obj[3]], cls_list[index]["sec-{}".format(index+1)])
                # Check info
                if cls_info is not None:
                    self.info['detections'][obj[0]]['det_label'] = cls_info['detections'][0]['det_label']

            return self.info

def main(args):
    # Instantiation
    json = Json()
    draw = Draw()

    # Get to relative parameter from first json
    custom_cfg = json.read_json(args.config)
    dev_cfg = [custom_cfg[key] for key in custom_cfg.keys() if "prim" in key]
    # Summarized previous dictionary and get to relative parameter from secondary json  
    for prim_ind in range(len(dev_cfg)):
        # Input_data append to dev_cfg
        dev_cfg[prim_ind].update({"input_data":custom_cfg['input_data']})
        dev_cfg[prim_ind].update(json.read_json(dev_cfg[prim_ind]['model_json']))
        # Check is openvino and start processes
        if custom_cfg['framework'] == 'openvino':
        # ---------------------------Check model architecture-------------------------------------------------------
            if 'obj' in dev_cfg[prim_ind]['tag']:
                from init_i.vino.obj import ObjectDetection as trg
                # ---------------------------Check secondary model and loading-------------------------
                # Get secondary model relative parameter from first json
                seconlist = [dev_cfg[prim_ind][key] for key in dev_cfg[prim_ind].keys() if "sec" in key]
                
                if seconlist != []:
                    from init_i.vino.cls import Classification as cls
                    for j in range(len(seconlist)):
                        # Append to secondary dictionary relative parameter from secondary model json  
                        seconlist[j].update({"sec-{}".format(j+1):json.read_json(seconlist[j]["model_json"]), "cls":cls()})
                        # Read every cls model
                        model, color_palette = seconlist[j]["cls"].load_model(seconlist[j]["sec-{}".format(j+1)])
                        # Add model and color to secondary dictionary
                        seconlist[j].update({"model":model,"color_palette":color_palette})

            if "cls" in dev_cfg[prim_ind]['tag']:
                from init_i.vino.cls import Classification as trg

            if "seg" in dev_cfg[prim_ind]['tag']:
                from init_i.vino.seg import Segmentation as trg

            if "pose" in dev_cfg[prim_ind]['tag']:
                from init_i.vino.pose import Pose as trg
                
        # ---------------------------Load model and initial pipeline--------------------------------------------------------------------
            trg = trg()
            model, color_palette = trg.load_model(dev_cfg[prim_ind])

        # ---------------------------Check input is camera or image and initial frame id/show id----------------------------------------
            from init_i.vino.common.images_capture import open_images_capture
            cap = open_images_capture(dev_cfg[prim_ind]['input_data'], dev_cfg[prim_ind]['openvino']['loop'])

        # ---------------------------Inference---------------------------------------------------------------------------------------------
            logging.info('Starting inference...')
            print("To close the application, press 'CTRL+C' here or switch to the output window and press ESC key")
            while True:
                frame = cap.read()
                info = trg.inference(model, frame, dev_cfg[prim_ind])
                
                # ---------------------------# Check ObjectDetection and two model inference-------------------------
                if 'obj' in dev_cfg[prim_ind]['tag'] and seconlist != [] and info is not None:
                    info = Multimodel().cls_inference(frame.copy(), info, seconlist)

        # ---------------------------Drawing detecter to information-----------------------------------------------------------------------
                if info is not None:
                    frame = draw.draw_detections(info, color_palette, dev_cfg[prim_ind])
                else:
                    continue
        # ---------------------------Show--------------------------------------------------------------------------------------------------              
                cv2.imshow('Detection Results', frame)
                key = cv2.waitKey(1)
                ESC_KEY = 27
                # Quit.
                if key in {ord('q'), ord('Q'), ESC_KEY}:
                    break

if __name__ == '__main__':
    config_logger('./VINO.log', 'w', "info")
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help = "The path of application config")
    args = parser.parse_args()

    sys.exit(main(args) or 0)