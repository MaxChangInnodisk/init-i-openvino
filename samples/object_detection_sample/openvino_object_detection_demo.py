#!/usr/bin/env python3
"""
 Copyright (C) 2018-2023 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import logging as log
import sys, os
from argparse import ArgumentParser, SUPPRESS
from pathlib import Path
from time import perf_counter

import cv2

sys.path.append( '/workspace' )
from ivit_i.io import Source, Displayer

from ivit_i.core.models import iDetection

from ivit_i.common.performance_metrics import put_highlighted_text, PerformanceMetrics
from ivit_i.core.models import DetectionModel, DetectionWithLandmarks, RESIZE_TYPES, OutputTransform
from ivit_i.core.pipelines import get_user_config, AsyncPipeline
from ivit_i.core.adapters import create_core, OpenvinoAdapter
from ivit_i.core.helpers import resolution, log_latency_per_stage

import random
import colorsys
import numpy as np

class ColorPalette:
    def __init__(self, n, rng=None):
        if n == 0:
            raise ValueError('ColorPalette accepts only the positive number of colors')
        if rng is None:
            rng = random.Random(0xACE)  # nosec - disable B311:random check

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

class OutputTransform:
    def __init__(self, input_size, output_resolution):
        self.output_resolution = output_resolution
        if self.output_resolution:
            self.new_resolution = self.compute_resolution(input_size)

    def compute_resolution(self, input_size):
        self.input_size = input_size
        size = self.input_size[::-1]
        self.scale_factor = min(self.output_resolution[0] / size[0],
                                self.output_resolution[1] / size[1])
        return self.scale(size)

    def resize(self, image):
        if not self.output_resolution:
            return image
        curr_size = image.shape[:2]
        if curr_size != self.input_size:
            self.new_resolution = self.compute_resolution(curr_size)
        if self.scale_factor == 1:
            return image
        return cv2.resize(image, self.new_resolution)

    def scale(self, inputs):
        if not self.output_resolution or self.scale_factor == 1:
            return inputs
        return (np.array(inputs) * self.scale_factor).astype(np.int32)

def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument('-m', '--model', required=True,
                      help='Required. Path to an .xml file with a trained model '
                           'or address of model inference service if using ovms adapter.')
    available_model_wrappers = [name.lower() for name in DetectionModel.available_wrappers()]
    args.add_argument('-at', '--architecture_type', help='Required. Specify model\' architecture type.',
                      type=str, required=True, choices=available_model_wrappers)
    args.add_argument('--adapter', help='Optional. Specify the model adapter. Default is openvino.',
                      default='openvino', type=str, choices=('openvino', 'ovms'))
    args.add_argument('-i', '--input', required=True,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    args.add_argument('-d', '--device', default='CPU', type=str,
                      help='Optional. Specify the target device to infer on; CPU, GPU, HDDL or MYRIAD is '
                           'acceptable. The demo will look for a suitable plugin for device specified. '
                           'Default value is CPU.')

    common_model_args = parser.add_argument_group('Common model options')
    common_model_args.add_argument('--labels', help='Optional. Labels mapping file.', default=None, type=str)
    common_model_args.add_argument('-t', '--prob_threshold', default=0.5, type=float,
                                   help='Optional. Probability threshold for detections filtering.')
    common_model_args.add_argument('--resize_type', default=None, choices=RESIZE_TYPES.keys(),
                                   help='Optional. A resize type for model preprocess. By default used model predefined type.')
    common_model_args.add_argument('--input_size', default=(600, 600), type=int, nargs=2,
                                   help='Optional. The first image size used for CTPN model reshaping. '
                                        'Default: 600 600. Note that submitted images should have the same resolution, '
                                        'otherwise predictions might be incorrect.')
    common_model_args.add_argument('--anchors', default=None, type=float, nargs='+',
                                   help='Optional. A space separated list of anchors. '
                                        'By default used default anchors for model. Only for YOLOV4 architecture type.')
    common_model_args.add_argument('--masks', default=None, type=int, nargs='+',
                                   help='Optional. A space separated list of mask for anchors. '
                                        'By default used default masks for model. Only for YOLOV4 architecture type.')
    common_model_args.add_argument('--layout', type=str, default=None,
                                   help='Optional. Model inputs layouts. '
                                        'Ex. NCHW or input0:NCHW,input1:NC in case of more than one input.')
    common_model_args.add_argument('--num_classes', default=None, type=int,
                                   help='Optional. Number of detected classes. Only for NanoDet, NanoDetPlus '
                                        'architecture types.')

    infer_args = parser.add_argument_group('Inference options')
    infer_args.add_argument('-nireq', '--num_infer_requests', help='Optional. Number of infer requests',
                            default=0, type=int)
    infer_args.add_argument('-nstreams', '--num_streams',
                            help='Optional. Number of streams to use for inference on the CPU or/and GPU in throughput '
                                 'mode (for HETERO and MULTI device cases use format '
                                 '<device1>:<nstreams1>,<device2>:<nstreams2> or just <nstreams>).',
                            default='', type=str)
    infer_args.add_argument('-nthreads', '--num_threads', default=None, type=int,
                            help='Optional. Number of threads to use for inference on CPU (including HETERO cases).')
    infer_args.add_argument('--async_mode', action='store_true', help='')
    io_args = parser.add_argument_group('Input/output options')
    io_args.add_argument('--loop', default=False, action='store_true',
                         help='Optional. Enable reading the input in a loop.')
    io_args.add_argument('-o', '--output', required=False,
                         help='Optional. Name of the output file(s) to save.')
    io_args.add_argument('-limit', '--output_limit', required=False, default=1000, type=int,
                         help='Optional. Number of frames to store in output. '
                              'If 0 is set, all frames are stored.')
    io_args.add_argument('--no_show', help="Optional. Don't show output.", action='store_true')
    io_args.add_argument('-u', '--utilization_monitors', default='', type=str,
                         help='Optional. List of monitors to show initially.')

    input_transform_args = parser.add_argument_group('Input transform options')
    input_transform_args.add_argument('--reverse_input_channels', default=False, action='store_true',
                                      help='Optional. Switch the input channels order from '
                                           'BGR to RGB.')
    input_transform_args.add_argument('--mean_values', default=None, type=float, nargs=3,
                                      help='Optional. Normalize input by subtracting the mean '
                                           'values per channel. Example: 255.0 255.0 255.0')
    input_transform_args.add_argument('--scale_values', default=None, type=float, nargs=3,
                                      help='Optional. Divide input by scale values per channel. '
                                           'Division is applied after mean values subtraction. '
                                           'Example: 255.0 255.0 255.0')

    debug_args = parser.add_argument_group('Debug options')
    debug_args.add_argument('-r', '--raw_output_message', help='Optional. Output inference results raw values showing.',
                            default=False, action='store_true')
    return parser

""" ######################################### """
""" #      Intel Object Detection Sample    # """
""" ######################################### """

def draw_detections(frame, detections, palette, labels, output_transform):
    frame = output_transform.resize(frame)
    for detection in detections:
        class_id = int(detection.id)
        color = palette[class_id]
        det_label = labels[class_id] if labels and len(labels) >= class_id else '#{}'.format(class_id)
        xmin, ymin, xmax, ymax = detection.get_coords()
        xmin, ymin, xmax, ymax = output_transform.scale([xmin, ymin, xmax, ymax])
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(frame, '{} {:.1%}'.format(det_label, detection.score),
                    (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
        if isinstance(detection, DetectionWithLandmarks):
            for landmark in detection.landmarks:
                landmark = output_transform.scale(landmark)
                cv2.circle(frame, (int(landmark[0]), int(landmark[1])), 2, (0, 255, 255), 2)
    return frame


def print_raw_results(detections, labels, frame_id):
    log.debug(' ------------------- Frame # {} ------------------ '.format(frame_id))
    log.debug(' Class ID | Confidence | XMIN | YMIN | XMAX | YMAX ')
    for detection in detections:
        xmin, ymin, xmax, ymax = detection.get_coords()
        class_id = int(detection.id)
        det_label = labels[class_id] if labels and len(labels) >= class_id else '#{}'.format(class_id)
        log.debug('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                  .format(det_label, detection.score, xmin, ymin, xmax, ymax))


def main():
    args = build_argparser().parse_args()
    if args.architecture_type != 'yolov4' and args.anchors:
        log.warning('The "--anchors" option works only for "-at==yolov4". Option will be omitted')
    if args.architecture_type != 'yolov4' and args.masks:
        log.warning('The "--masks" option works only for "-at==yolov4". Option will be omitted')
    if args.architecture_type not in ['nanodet', 'nanodet-plus'] and args.num_classes:
        log.warning('The "--num_classes" option works only for "-at==nanodet" and "-at==nanodet-plus". Option will be omitted')

    src = Source( input=args.input, resolution=(640, 480), fps=30, start=True)
    dpr = Displayer(cv=True)

    plugin_config = get_user_config(args.device, args.num_streams, args.num_threads)
    model_adapter = OpenvinoAdapter(create_core(), args.model, device=args.device, plugin_config=plugin_config,
                                    max_num_requests=args.num_infer_requests, model_parameters = {'input_layouts': args.layout})

    configuration = {
        'resize_type': args.resize_type,
        'mean_values': args.mean_values,
        'scale_values': args.scale_values,
        'reverse_input_channels': args.reverse_input_channels,
        'path_to_labels': args.labels,
        'confidence_threshold': args.prob_threshold,
        'input_size': args.input_size, # The CTPN specific
        'num_classes': args.num_classes, # The NanoDet and NanoDetPlus specific
    }
    model = DetectionModel.create_model(args.architecture_type, model_adapter, configuration)
    model.log_layers_info()

    detector_pipeline = AsyncPipeline(model)

    next_frame_id = 0
    next_frame_id_to_show = 0

    palette = ColorPalette(len(model.labels) if model.labels else 100)
    metrics = PerformanceMetrics()
    render_metrics = PerformanceMetrics()
    presenter = None
    output_transform = None

    while True:
        
        if detector_pipeline.callback_exceptions:
            raise detector_pipeline.callback_exceptions[0]
        
        # Process all completed requests
        results = detector_pipeline.get_result(next_frame_id_to_show)
        if results:
            objects, frame_meta = results
            frame = frame_meta['frame']
            start_time = frame_meta['start_time']

            if len(objects) and args.raw_output_message:
                print_raw_results(objects, model.labels, next_frame_id_to_show)

            rendering_start_time = perf_counter()
            frame = draw_detections(frame, objects, palette, model.labels, output_transform)
            render_metrics.update(rendering_start_time)
            metrics.update(start_time, frame)

            next_frame_id_to_show += 1

            dpr.show(frame=frame)
            continue

        if detector_pipeline.is_ready():
            # Get new image/frame
            start_time = perf_counter()
            frame = src.read()

            if frame is None:
                if next_frame_id == 0:
                    raise ValueError("Can not read an image from the input")
                break
                
            if next_frame_id == 0:
                output_transform = OutputTransform(frame.shape[:2], (640, 480))

            # Submit for inference
            detector_pipeline.submit_data(frame, next_frame_id, {'frame': frame, 'start_time': start_time})
            next_frame_id += 1
        else:
            # Wait for empty request
            detector_pipeline.await_any()

    detector_pipeline.await_all()
    if detector_pipeline.callback_exceptions:
        raise detector_pipeline.callback_exceptions[0]
    
    # Process completed requests
    for next_frame_id_to_show in range(next_frame_id_to_show, next_frame_id):
        results = detector_pipeline.get_result(next_frame_id_to_show)
        objects, frame_meta = results
        frame = frame_meta['frame']
        start_time = frame_meta['start_time']

        if len(objects) and args.raw_output_message:
            print_raw_results(objects, model.labels, next_frame_id_to_show)

        rendering_start_time = perf_counter()
        frame = draw_detections(frame, objects, palette, model.labels, output_transform)
        render_metrics.update(rendering_start_time)
        metrics.update(start_time, frame)

        dpr.show(frame=frame)

    metrics.log_total()
    # log_latency_per_stage(cap.reader_metrics.get_latency(),
    #                       detector_pipeline.preprocess_metrics.get_latency(),
    #                       detector_pipeline.inference_metrics.get_latency(),
    #                       detector_pipeline.postprocess_metrics.get_latency(),
    #                       render_metrics.get_latency())

""" ######################################### """
""" #      Intel Object Detection Sample    # """
""" ######################################### """

def ivit_print_results(detections, frame_id):
    log.debug(' ------------------- iVIT Frame # {} ------------------ '.format(frame_id))
    log.debug(' Class ID | Confidence | XMIN | YMIN | XMAX | YMAX ')
    for detection in detections:
        xmin, ymin, xmax, ymax = detection.get_coords()
        log.debug('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                    .format(detection.label, detection.score, xmin, ymin, xmax, ymax))

    return detections


def ivit_draw_results(frame, detections, palette):
    for detection in detections:
        class_id = int(detection.id)
        color = palette[class_id]
        xmin, ymin, xmax, ymax = detection.get_coords()
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(frame, '{} {:.1%}'.format(detection.label, detection.score),
                    (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
        if isinstance(detection, DetectionWithLandmarks):
            for landmark in detection.landmarks:
                cv2.circle(frame, (int(landmark[0]), int(landmark[1])), 2, (0, 255, 255), 2)
    return frame


def ivit_main():

    args = build_argparser().parse_args()
    if args.architecture_type != 'yolov4' and args.anchors:
        log.warning('The "--anchors" option works only for "-at==yolov4". Option will be omitted')
    if args.architecture_type != 'yolov4' and args.masks:
        log.warning('The "--masks" option works only for "-at==yolov4". Option will be omitted')
    if args.architecture_type not in ['nanodet', 'nanodet-plus'] and args.num_classes:
        log.warning('The "--num_classes" option works only for "-at==nanodet" and "-at==nanodet-plus". Option will be omitted')

    src = Source( input=args.input, resolution=(640, 480), fps=30, start=True)
    dpr = Displayer(cv=True)

    model = iDetection(
        model_path = args.model,
        label_path = args.labels,
        device = args.device,
        architecture_type = args.architecture_type,
        async_mode=args.async_mode,
        anchors = args.anchors
    )

    palette = ColorPalette(len(model.get_labels()) if model.get_labels() else 100)

    try:
        while True:
            frame = src.read()

            frame_show, results = model.inference(frame=frame)

            if results:
                # ivit_print_results(results, model.get_frame_id())
                frame_show = ivit_draw_results(frame_show, results, palette)
                print('\rFPS: {}'.format(model.get_avg_fps()), end='')

            if frame_show is not None:
                dpr.show(frame=frame_show)
    except KeyboardInterrupt:
        pass

    finally:
        print('\n')
        model.release()
        src.release()
        dpr.release()

    log_latency_per_stage(
        model.infer_pipeline.preprocess_metrics.get_latency(),
        model.infer_pipeline.inference_metrics.get_latency(),
        model.infer_pipeline.postprocess_metrics.get_latency(),
    )

if __name__ == '__main__':
    # sys.exit(main() or 0)
    sys.exit(ivit_main() or 0)

""" Usage
* Sync 

python3 samples/object_detection_demo.py \
-d CPU \
-i /dev/video0 \
-m model/yolo-v4-tiny-tf/yolo-v4-tiny-tf.xml \
-at yolov4 \
--labels model/yolo-v4-tiny-tf/coco.names

* Async

python3 samples/object_detection_demo.py \
-d CPU \
-i /dev/video0 \
-m model/yolo-v4-tiny-tf/yolo-v4-tiny-tf.xml \
-at yolov4 \
--labels model/yolo-v4-tiny-tf/coco.names \
--async_mode

python3 samples/object_detection_demo.py \
-d CPU \
-i /dev/video0 \
-m model/safety_helmet/safety_helmet.xml \
-at yolov4 --labels model/safety_helmet/classes.txt \
--anchors 20.0 24.0 46.0 18.0 31.0 38.0 45.0 54.0 86.0 38.0 41.0 106.0 67.0 77.0 111.0 110.0 170.0 196.0

"""
