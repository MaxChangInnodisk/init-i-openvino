from ivit_i.utils.draw_tools import CUSTOM_SCALE
import numpy as np
import cv2, colorsys, json, logging, sys
import itertools as it

from ivit_i.app.common import App, DETS

from ivit_i.utils import (     PADDING,
    BASE_FONT_SIZE,
    BASE_FONT_THICK,
    get_text_size,
    get_scale,
    draw_text,
    draw_rect )


class Default(App):

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        logging.info("Get Defualt Application")
    
    def get_params(self) -> dict:
        """ Define Counting Parameter Format """
        
        # Define Dictionary
        ret = {
            "name": self.def_param("string", "tracking", "define application name"),
            "depend_on": self.def_param("list", "[ \"car\" ]", "launch application on target label")
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    
        return ret
    
    def init_detect_param(self):
        self.text_pos           = [ self.padding, self.padding ]

    def __call__(self, frame, info, draw=True):

        self.init_draw_param( frame )
        self.init_detect_param()

        # Capture all center point in current frame and draw the bounding box
        for idx in it.count(0):
            
            # Check if interation over the length
            if idx >= (len(info[DETS])): break

            # Get Detection Object
            detection   = info[DETS][idx]
            label       = detection['label']
            
            # if not in depend_label then pass
            if not (label in self.depend_labels): continue

            # Get Draw Parameters
            (x1, x2, y1, y2) = self.get_xxyy( detection )
            score = detection['score']
            self.text_draw = "{} {:.3f}".format(label, score)
            self.text_pos[0] = x1
            self.text_pos[1] = y1 - (self.text_hei + self.text_base)
            self.text_color = self.palette[label]
            
            # Draw the bounding box
            if draw:
                frame = draw_rect(
                    frame           = frame, 
                    left_top        = ( x1, y1 ), 
                    right_bottom    = ( x2, y2 ), 
                    color           = self.palette[label]
                )
                frame = draw_text(
                    frame       = frame, 
                    text        = self.text_draw, 
                    left_top    = self.text_pos, 
                    color       = self.text_color, 
                    size        = self.trg_scale, 
                    thick       = self.trg_thick, 
                    outline     = True )
        
        return frame, self.text_draw
        