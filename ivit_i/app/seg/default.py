from ivit_i.app.obj.area_detection import DET_COLOR
from ivit_i.utils.draw_tools import CUSTOM_SCALE
import numpy as np
import cv2, colorsys, json, logging, sys, os
import itertools as it

from ivit_i.utils import handle_exception, load_txt
from ivit_i.app.common import (
    App,
    FRAME,
    OUT_RESOL,
    TAG,
    DETS
)

DET_OBJ     = "objects"
ONLY_MASK   = "only_masks"

class Default(App):

    def __init__(self, config: dict) -> None:
        super().__init__(config)

        # Get Visualizer
        logging.info('Get Visualizer')
        if config['openvino']['architecture_type'] == 'segmentation':
            self.visualizer = SegmentationVisualizer(config['openvino'])
        else:
            self.visualizer = SaliencyMapVisualizer()

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

    # Draw segmentaion detecotion reslut to frame
    def render_segmentation(self, frame, masks, visualiser, resizer, only_masks=False):
        # Catch apply color map
        output = self.visualizer.apply_color_map(masks)
        if not only_masks:
            # Position replace color
            output = np.floor_divide(frame, 2) + np.floor_divide(output, 2)
        return resizer.resize(output)

    def __call__(self, frame, info, draw=True):
        
        only_masks          =  info[ONLY_MASK]
        output_transform    = info[OUT_RESOL]
        for detection in info[DETS]:
            masks  = detection[DET_OBJ]
            frame = self.render_segmentation(frame, masks, self.palette, output_transform, only_masks)

        return frame, "null"

class SegmentationVisualizer():
    pascal_voc_palette = [
        (0,   0,   0),
        (128, 0,   0),
        (0,   128, 0),
        (128, 128, 0),
        (0,   0,   128),
        (128, 0,   128),
        (0,   128, 128),
        (128, 128, 128),
        (64,  0,   0),
        (192, 0,   0),
        (64,  128, 0),
        (192, 128, 0),
        (64,  0,   128),
        (192, 0,   128),
        (64,  128, 128),
        (192, 128, 128),
        (0,   64,  0),
        (128, 64,  0),
        (0,   192, 0),
        (128, 192, 0),
        (0,   64,  128)
    ]

    def __init__(self, Dict, colors_path=None):
        if colors_path:
            self.color_palette = self.get_palette_from_file(colors_path)
        else:
            self.color_palette = self.pascal_voc_palette
        self.color_map = self.create_color_map()
        self.get_palette(Dict)

    def get_palette_from_file(self, colors_path):
        with open(colors_path, 'r') as file:
            colors = []
            for line in file.readlines():
                values = line[line.index('(')+1:line.index(')')].split(',')
                colors.append([int(v.strip()) for v in values])
            return colors

    def create_color_map(self):
        classes = np.array(self.color_palette, dtype=np.uint8)[:, ::-1] # RGB to BGR
        color_map = np.zeros((256, 1, 3), dtype=np.uint8)
        classes_num = len(classes)
        color_map[:classes_num, 0, :] = classes
        color_map[classes_num:, 0, :] = np.random.uniform(0, 255, size=(256-classes_num, 3))
        return color_map

    def apply_color_map(self, input):
        input_3d = cv2.merge([input, input, input])
        return cv2.LUT(input_3d, self.color_map) # 使用查找表中的值填充输出数组

    def get_palette(self, Dict):
        # init
        palette, content = list(), list()
        # get labels
        if not ('label_path' in Dict.keys()):
            mas = "Error configuration file, can't find `label_path`"
            logging.error(mas)
            raise Exception(mas)
        label_path = Dict['label_path']
        labels = load_txt(label_path)
        # parse the path
        name, ext = os.path.splitext(label_path)
        output_palette_path = "{}_colormap{}".format(name, ext)
        # update palette and the content of colormap
        logging.info("Get colormap ...")
        for index, label in enumerate(labels):
            color = self.color_map[index][0]                                       # get random color
            palette.append(color)                                               # get palette's color list
            content.append('{label}: {color}'.format(label=label, color=tuple(color)))  # setup content
        # write map table into colormap
        logging.info("Write colormap into `{}`".format(output_palette_path))
        with open(output_palette_path, 'w') as f:
            f.write('\n'.join(content))

class SaliencyMapVisualizer():
    def apply_color_map(self, input):
        saliency_map = (input * 255.0).astype(np.uint8)
        saliency_map = cv2.merge([saliency_map, saliency_map, saliency_map])
        return saliency_map
