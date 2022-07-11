#!/usr/bin/env python3
import cv2
import numpy as np
from time import perf_counter

import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/""))
sys.path.append(str(Path(__file__).resolve().parents[3]/"")) #ivinno_api

from openvino.inference_engine import IECore
import common
from common.model import Model
from common.pipelines import get_user_config, Realtime
# import common.monitors as monitors
# from common.performance_metrics import PerformanceMetrics
from utils import load_txt

import logging

class Segmentation():

    def __init__(self):
        self.next_frame_id = 0
        self.next_frame_id_to_show = 0
        # self.metrics = PerformanceMetrics()

    def load_model(self, config_path=""):
        # ---------------------------Step 1. Initialize inference engine core--------------------------------------------------
        logging.info('Initializing Inference Engine...')
        ie = IECore()

        # ---------------------------Step 2. Read a model in OpenVINO Intermediate Representation or ONNX format---------------
        model = get_model(ie, config_path)
        logging.info('Reading the network: {}'.format(config_path['openvino']['model_path']))
        
        logging.info('Loading network...')
        # Get device relative info for inference 
        plugin_config = get_user_config( config_path['openvino']['device'], config_path['openvino']["num_streams"], config_path['openvino']["num_threads"])
        # Initialize Pipeline(for inference)
        self.detector_pipeline = Realtime(ie, model, plugin_config,
                                        device=config_path['openvino']['device'])
        # ---------------------------Step 3. Create detection words of color---------------
        if config_path['openvino']['architecture_type'] == 'segmentation':
            palette = SegmentationVisualizer(config_path['openvino'])
        else:
            palette = SaliencyMapVisualizer()
        
        return model, palette

    def inference(self, model, frame, json):
        # Check pipeline is ready & setting output_shape & inference
        start_time = perf_counter()
        if frame is None:
            if self.next_frame_id == 0:
                raise ValueError("Can't read an image from the input")
            raise ValueError("Can't read an image")
            
        if self.next_frame_id == 0:
            # Compute rate from setting output shape and input images shape 
            self.output_transform = common.OutputTransform(frame.shape[:2], json['openvino']['output_resolution'])
            # if json['openvino']['output_resolution']:
            #     output_resolution = self.output_transform.new_resolution
            # else:
            #     output_resolution = (frame.shape[1], frame.shape[0])      
            # self.presenter = monitors.Presenter(json['openvino']['utilization_monitors'], 55,
            #                                 (round(output_resolution[0] / 4), round(output_resolution[1] / 8)))

        # Submit for inference
        res = self.detector_pipeline.submit_data(frame, {'frame': frame, 'start_time': start_time})
        self.next_frame_id += 1

        # Process all completed requests
        results = self.detector_pipeline.get_result(res)

        if results:
            objects, frame_meta = results
            frame = frame_meta['frame']
            start_time = frame_meta['start_time']

            # self.presenter.drawGraphs(frame)
            # self.metrics.update(start_time, frame)

            self.next_frame_id_to_show += 1
            info = {"frame":frame,
                    "output_transform":self.output_transform,
                    'only_masks':json['openvino']['only_masks'],
                    'detections':[{'objects':objects}]}
                    
            return info

def get_model(ie, model_config):
    if model_config['openvino']['architecture_type'] == 'segmentation':
        return SegmentationModel(ie, model_config['openvino']['model_path'])
    if model_config['openvino']['architecture_type'] == 'salient_object_detection':
        return SalientObjectDetectionModel(ie, model_config['openvino']['model_path'])

class SegmentationModel(Model):
    def __init__(self, ie, model_path):
        super().__init__(ie, model_path)

        self.input_blob_name = self.prepare_inputs()
        self.out_blob_name = self.prepare_outputs()
        self.labels = None
    
    def prepare_inputs(self):
        if len(self.net.input_info) != 1:
            raise RuntimeError("Demo supports topologies only with 1 input")
        blob_name = next(iter(self.net.input_info)) # get next iter to value
        blob = self.net.input_info[blob_name]
        blob.precision = "U8"
        blob.layout = "NCHW"

        input_size = blob.input_data.shape
        if len(input_size) == 4 and input_size[1] == 3:
            self.n, self.c, self.h, self.w = input_size
        else:
            raise RuntimeError("3-channel 4-dimensional model's input is expected")

        return blob_name

    def prepare_outputs(self):
        if len(self.net.outputs) != 1:
            raise RuntimeError("Demo supports topologies only with 1 output")

        blob_name = next(iter(self.net.outputs)) # get next iter to value
        blob = self.net.outputs[blob_name]

        out_size = blob.shape
        if len(out_size) == 3:
            self.out_channels = 0
        elif len(out_size) == 4:
            self.out_channels = out_size[1]
        else:
            raise Exception("Unexpected output blob shape {}. Only 4D and 3D output blobs are supported".format(out_size))

        return blob_name

    def preprocess(self, inputs):
        image = inputs
        resized_image = cv2.resize(image, (self.w, self.h))
        meta = {'original_shape': image.shape,
                'resized_shape': resized_image.shape}
        resized_image = resized_image.transpose((2, 0, 1))
        resized_image = resized_image.reshape((self.n, self.c, self.h, self.w))
        dict_inputs = {self.input_blob_name: resized_image}
        return dict_inputs, meta

    def postprocess(self, outputs, meta):
        predictions = outputs[self.out_blob_name].squeeze() # Remove axes of length one from a
        input_image_height = meta['original_shape'][0]
        input_image_width = meta['original_shape'][1]

        if self.out_channels < 2: # assume the output is already ArgMax'ed
            result = predictions.astype(np.uint8)
        else:
            result = np.argmax(predictions, axis=0).astype(np.uint8)

        result = cv2.resize(result, (input_image_width, input_image_height), 0, 0, interpolation=cv2.INTER_NEAREST)
        return result

class SalientObjectDetectionModel(SegmentationModel):

    def postprocess(self, outputs, meta):
        input_image_height = meta['original_shape'][0]
        input_image_width = meta['original_shape'][1]
        result = outputs[self.out_blob_name].squeeze()
        result = 1/(1 + np.exp(-result))
        result = cv2.resize(result, (input_image_width, input_image_height), 0, 0, interpolation=cv2.INTER_NEAREST)
        return result

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
