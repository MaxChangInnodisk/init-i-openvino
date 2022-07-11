#!/usr/bin/env python3
from time import perf_counter

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/""))
sys.path.append(str(Path(__file__).resolve().parents[3]/"")) #ivinno_api

from openvino.inference_engine import IECore 
import common
from common.pipelines import get_user_config, Realtime
# import common.monitors as monitors
# from ivinno.vino.common.performance_metrics import PerformanceMetrics
from ivit_i.common.images_capture import open_images_capture

from .hpe_associative_embedding import HpeAssociativeEmbedding
from .open_pose import OpenPose

import logging


class Pose():
    def __init__(self):
        self.next_frame_id = 0
        self.next_frame_id_to_show = 0
        # self.metrics = PerformanceMetrics()


    def load_model(self, config_path="", frame=[]):
        # ---------------------------Step 1. Initialize inference engine core--------------------------------------------------
        logging.info('Initializing Inference Engine...')
        ie = IECore()

        # Intialize parameter need iamge shape fpr model setting
        if frame==[]:
            logging.warning('no frame provide , capture a new one.')
            cap = open_images_capture(config_path['input_data'], config_path['openvino']['loop'])
            frame = cap.read()

        # ---------------------------Step 2. Read a model in OpenVINO Intermediate Representation or ONNX format---------------
        model = get_model(ie, config_path, frame.shape[1]/frame.shape[0])
        logging.info('Reading the network: {}'.format(config_path['openvino']['model_path']))

        logging.info('Loading network...')
        # Get device relative info for inference 
        plugin_config = get_user_config( config_path['openvino']['device'], config_path['openvino']["num_streams"], config_path['openvino']["num_threads"])
        # Initialize Pipeline(for inference)
        self.detector_pipeline = Realtime(ie, model, plugin_config,
                                device=config_path['openvino']['device'])
        # ---------------------------Step 3. Create detection words of color---------------
        palette = PoseParam().colors
        
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
            (poses, scores), frame_meta = results
            frame = frame_meta['frame']
            start_time = frame_meta['start_time']

            if len(poses) and json['openvino']['raw_output_message']:
                print_raw_results(poses, scores)

            # self.presenter.drawGraphs(frame)
            # self.metrics.update(start_time, frame)

            self.next_frame_id_to_show += 1
            
            info = {"frame":frame,
                    "output_transform":self.output_transform,
                    'skeleton':PoseParam().default_skeleton,
                    'prob_threshold':json['openvino']['thres'],
                    'detections':[{'poses':poses}]}

            return info


def get_model(ie, model_config, aspect_ratio):
    if model_config['openvino']['architecture_type'] == 'ae':
        return HpeAssociativeEmbedding(ie, model_config['openvino']['model_path'], target_size=model_config['openvino']['tsize'], aspect_ratio=aspect_ratio, 
                                                prob_threshold=model_config['openvino']['thres'])
    if model_config['openvino']['architecture_type'] == 'higherhrnet':
        return HpeAssociativeEmbedding(ie, model_config['openvino']['model_path'], target_size=model_config['openvino']['tsize'], aspect_ratio=aspect_ratio, 
                                                prob_threshold=model_config['openvino']['thres'], delta=0.5, padding_mode='center')
    if model_config['openvino']['architecture_type'] == 'openpose':
        return OpenPose(ie, model_config['openvino']['model_path'], target_size=model_config['openvino']['tsize'], aspect_ratio=aspect_ratio, 
                                                prob_threshold=model_config['openvino']['thres'])

def print_raw_results(poses, scores):
    logging.info('Poses:')
    for pose, pose_score in zip(poses, scores):
        pose_str = ' '.join('({:.2f}, {:.2f}, {:.2f})'.format(p[0], p[1], p[2]) for p in pose)
        logging.info('{} | {:.2f}'.format(pose_str, pose_score))

class PoseParam():
    def __init__(self) -> None:
        # 17 color for joint
        self.colors = ( (255, 0, 0), (255, 0, 255), (170, 0, 255), (255, 0, 85),
                    (255, 0, 170), (85, 255, 0), (255, 170, 0), (0, 255, 0),
                    (255, 255, 0), (0, 255, 85), (170, 255, 0), (0, 85, 255),
                    (0, 255, 170), (0, 0, 255), (0, 255, 255), (85, 0, 255),
                    (0, 170, 255))
        # skeleton point
        self.default_skeleton = ((15, 13), (13, 11), (16, 14), (14, 12), (11, 12), (5, 11), 
                                (6, 12), (5, 6), (5, 7), (6, 8), (7, 9), (8, 10), 
                                (1, 2), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6))