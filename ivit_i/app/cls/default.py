import cv2, logging
import itertools as it
from ivit_i.app.common import ( 
    App, 
    DETS, 
    DET_COLOR,
)

from ivit_i.utils.draw_tools import (
    CUSTOM_SCALE,
    PADDING,
    BASE_FONT_SIZE,
    BASE_FONT_THICK,
    get_text_size,
    get_scale,
    draw_text 
)

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

    def __call__(self, frame, info, draw=True):

        self.init_draw_param( frame )

        # Capture all center point in current frame and draw the bounding box
        for idx in it.count(0):
            
            # Check if interation over the length
            if idx >= (len(info[DETS])): break

            # Get Detection Object
            detection   = info[DETS][idx]
            class_id    = int(detection['id'])
            label       = detection['label']

            xmin        = max(int(detection['xmin']), 0)
            ymin        = max(int(detection['ymin']), 0)
            content     = '{} {:.1%}'.format(label, detection['score'])

            # Draw the bounding box
            trg_color   = DET_COLOR
            if label in self.palette:
                trg_color = self.palette[label]
            else:
                print("Could not find {} in palette".format(label))

            if draw:
                frame = draw_text(
                    frame, 
                    content, 
                    (xmin, ymin),  trg_color)

        return frame, self.text_draw
        