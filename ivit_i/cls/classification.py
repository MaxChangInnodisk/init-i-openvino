#!/usr/bin/env python3
import numpy as np
from time import perf_counter
from openvino.inference_engine import IECore

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/""))
sys.path.append(str(Path(__file__).resolve().parents[3]/"")) #ivinno_api

import common
from common.model import Model
from common.pipelines import get_user_config, Realtime
# import common.monitors as monitors
# from common.performance_metrics import PerformanceMetrics
from common.utils import load_labels, resize_image

import logging

class Classification():

    def __init__(self):
        self.next_frame_id = 0
        self.next_frame_id_to_show = 0
        # self.metrics = PerformanceMetrics()

    def load_model(self, config_path=""):
        # ---------------------------Step 1. Initialize inference engine core--------------------------------------------------
        logging.info('Initializing Inference Engine...')
        ie = IECore()
        
        # ---------------------------Step 2. Read a model in OpenVINO Intermediate Representation or ONNX format---------------
        logging.info('Reading the network: {}'.format(config_path['openvino']['model_path']))

        model = ClassificationModel(ie, config_path['openvino']['model_path'], 
                            labels=config_path['openvino']['label_path'])
        
        logging.info('Loading network...')
        # Get device relative info for inference 
        plugin_config = get_user_config( config_path['openvino']['device'], config_path['openvino']["num_streams"], config_path['openvino']["num_threads"])
        # Initialize Pipeline(for inference)
        self.detector_pipeline = Realtime(ie, model, plugin_config,
                                        device=config_path['openvino']['device'])
        # ---------------------------Step 3. Create detection words of color---------------
        color = tuple(np.random.choice(range(256), size=3).tolist())
        palette = [color]

        return model, palette

    def inference(self, model, frame, json):
        # Label length
        num_of_classes = len(model.labels)
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
                        "output_transform":self.output_transform}
        
            total_bbox = []
            for detection in objects:
                # Change a shape of a numpy.ndarray with results to get another one with one dimension
                probs = objects[detection].reshape(num_of_classes)
                # Get an array of args.number_top class IDs in descending order of probability
                top_n_idexes = np.argsort(probs)[-json['openvino']['number_top']:][::-1][0]
                total_bbox.append({'xmin':15, 
                                    'ymin':40, 
                                    'xmax':30, 
                                    'ymax':30, 
                                    'label':model.labels[top_n_idexes], 
                                    'score': probs[top_n_idexes],
                                    'id': top_n_idexes})
                                    
                logging.info('{:^9} | {:10f} '
                            .format(model.labels[top_n_idexes], probs[top_n_idexes]))
            info.update({'detections':total_bbox})
            
            return info

class ClassificationModel(Model):
    
    def __init__(self, ie, model_path, labels=None):
        super().__init__(ie, model_path)

        if isinstance(labels, (list, tuple)):
            self.labels = labels
        else:
            self.labels = load_labels(labels) if labels else None

        self.resize_image = resize_image
        
        assert len(self.net.input_info) == 1, "Expected 1 input blob"
        self.image_blob_name = next(iter(self.net.input_info))
        if self.net.input_info[self.image_blob_name].input_data.shape[1] == 3:
            self.n, self.c, self.h, self.w = self.net.input_info[self.image_blob_name].input_data.shape
            self.nchw_shape = True
        else:
            self.n, self.h, self.w, self.c = self.net.input_info[self.image_blob_name].input_data.shape
            self.nchw_shape = False

    def preprocess(self, inputs):
        image = inputs
        # logging.warning('Image is resized from {} to {}'.format(image.shape[:-1],(self.h,self.w)))

        resized_image = self.resize_image(image, (self.w, self.h))
        meta = {'original_shape': image.shape,
                'resized_shape': resized_image.shape}
        if self.nchw_shape:
            resized_image = resized_image.transpose((2, 0, 1))  # Change data layout from HWC to CHW
            resized_image = resized_image.reshape((self.n, self.c, self.h, self.w))

        else:
            resized_image = resized_image.reshape((self.n, self.h, self.w, self.c))

        dict_inputs = {self.image_blob_name: resized_image}

        return dict_inputs, meta