import numpy as np
import random, os, sys, colorsys, logging
from time import perf_counter
# sys.path.append(f'{os.getcwd()}')

from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/""))

from openvino.inference_engine import IECore
import common
from common.pipelines import get_user_config, Realtime
from .yolo import YOLO, YoloV4

class ObjectDetection():

    def __init__(self):
        self.next_frame_id = 0
        self.next_frame_id_to_show = 0
        
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
        palette = ColorPalette(len(model.labels) if model.labels else 100)
        
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

        # Submit for inference
        res = self.detector_pipeline.submit_data(frame, {'frame': frame, 'start_time': start_time})
        self.next_frame_id += 1

        # Process all completed requests
        results = self.detector_pipeline.get_result(res)

        if results:
            objects, frame_meta = results
            frame = frame_meta['frame']
            start_time = frame_meta['start_time']

            if len(objects) and json['openvino']['raw_output_message']:
                print_raw_results(frame.shape[:2], objects, model.labels, json['openvino']['thres'])

            # self.presenter.drawGraphs(frame)
            # self.metrics.update(start_time, frame)

            self.next_frame_id_to_show += 1
            info = {"frame":frame,
                        "output_transform":self.output_transform}

            total_bbox = []
            for detection in objects:
                threshold = json['openvino']['thres']
                if detection.score > threshold:
                    xmin = max(int(detection.xmin), 0)
                    ymin = max(int(detection.ymin), 0)
                    xmax = min(int(detection.xmax), frame.shape[1])
                    ymax = min(int(detection.ymax), frame.shape[0])
                    class_id = int(detection.id)
                    label = model.labels[class_id] if model.labels and len(model.labels) >= class_id else '#{}'.format(class_id)
                    logging.info('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                                .format(label, detection.score, xmin, ymin, xmax, ymax))

                    total_bbox.append({ 'xmin':xmin, 
                                        'ymin':ymin, 
                                        'xmax':xmax, 
                                        'ymax':ymax, 
                                        'label':label, 
                                        'score': detection.score,
                                        'id': class_id})

            info.update({'detections':total_bbox})

            return info

def get_model(ie, model_config):
    input_transform = common.InputTransform(model_config['openvino']['reverse_input_channels'], 
                                            model_config['openvino']['mean_values'], 
                                            model_config['openvino']['scale_values'])

    if model_config['openvino']['architecture_type'] in ('ctpn', 'yolo', 'yolov4', 'retinaface',
                                'retinaface-pytorch') and not input_transform.is_trivial:
        raise ValueError("{} model doesn't support input transforms.".format(model_config['architecture_type']))
    if model_config['openvino']['architecture_type'] == 'yolo':
        return YOLO(ie, model_config['openvino']['model_path'], 
                        labels=model_config['openvino']['label_path'],
                        threshold=model_config['openvino']['thres'],
                        keep_aspect_ratio=model_config['openvino']['keep_aspect_ratio'],
                        anchors=model_config['openvino']['anchors'])
    elif model_config['openvino']['architecture_type'] == 'yolov4':
        return YoloV4(ie, model_config['openvino']['model_path'], 
                            labels=model_config['openvino']['label_path'],
                            threshold=model_config['openvino']['thres'],
                            keep_aspect_ratio=model_config['openvino']['keep_aspect_ratio'],
                            anchors=model_config['openvino']['anchors'], 
                            masks=model_config['openvino']['masks'])
    else:
        raise RuntimeError('No model type or invalid model type (-at) provided: {}'.format(model_config['architecture_type']))

def print_raw_results(size, detections, labels, threshold):
    logging.info(' Class ID | Confidence | XMIN | YMIN | XMAX | YMAX ')
    for detection in detections:
        if detection.score > threshold:
            xmin = max(int(detection.xmin), 0)
            ymin = max(int(detection.ymin), 0)
            xmax = min(int(detection.xmax), size[1])
            ymax = min(int(detection.ymax), size[0])
            class_id = int(detection.id)
            label = labels[class_id] if labels and len(labels) >= class_id else '#{}'.format(class_id)
            logging.info('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                     .format(label, detection.score, xmin, ymin, xmax, ymax))

class ColorPalette():
    def __init__(self, n, rng=None):
        assert n > 0

        if rng is None:
            rng = random.Random(0xACE)

        candidates_num = 100
        hsv_colors = [(1.0, 1.0, 1.0)]
        for _ in range(1, n):
            colors_candidates = [(rng.random(), rng.uniform(0.8, 1.0), rng.uniform(0.5, 1.0))
                                 for _ in range(candidates_num)]
            min_distances = [self.min_distance(hsv_colors, c) for c in colors_candidates]
            arg_max = np.argmax(min_distances)
            hsv_colors.append(colors_candidates[arg_max])

        self.palette = [self.hsv2rgb(*hsv) for hsv in hsv_colors]

    @staticmethod
    def dist(c1, c2):
        dh = min(abs(c1[0] - c2[0]), 1 - abs(c1[0] - c2[0])) * 2
        ds = abs(c1[1] - c2[1])
        dv = abs(c1[2] - c2[2])
        return dh * dh + ds * ds + dv * dv

    @classmethod
    def min_distance(cls, colors_set, color_candidate):
        distances = [cls.dist(o, color_candidate) for o in colors_set]
        return np.min(distances)

    @staticmethod
    def hsv2rgb(h, s, v):
        return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

    def __getitem__(self, n):
        return self.palette[n % len(self.palette)]

    def __len__(self):
        return len(self.palette)