#!/usr/bin/env python3
# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

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
import sys, cv2
from argparse import ArgumentParser, SUPPRESS
from typing import Union, Dict
from numpy import ndarray

from ivit_i.io import Source, Displayer
from ivit_i.core.models import iDetection
from ivit_i.common import Metric
from ivit_i.utils import Palette

def build_argparser():

    parser = ArgumentParser(add_help=False)
    basic_args = parser.add_argument_group('Basic options')
    basic_args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    basic_args.add_argument('-m', '--model', required=True,
                      help='Required. Path to an .xml file with a trained model '
                           'or address of model inference service if using ovms adapter.')
    basic_args.add_argument('-i', '--input', required=True,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    available_model_wrappers = [name.lower() for name in iDetection.available_wrappers()]
    basic_args.add_argument('-at', '--architecture_type', help='Required. Specify model\' architecture type.',
                      type=str, required=True, choices=available_model_wrappers)
    basic_args.add_argument('-d', '--device', type=str,
                      help='Optional. `Intel` support [ `CPU`, `GPU` ] \
                            `Hailo` is support [ `HAILO` ]; \
                            `Xilinx` support [ `DPU` ]; \
                            `dGPU` support [ 0, ... ] which depends on the device index of your GPUs; \
                            `Jetson` support [ 0 ].' )

    model_args = parser.add_argument_group('Model options')
    model_args.add_argument('-l', '--label', help='Optional. Labels mapping file.', default=None, type=str)
    model_args.add_argument('-t', '--confidence_threshold', default=0.6, type=float,
                                   help='Optional. Confidence threshold for detections.')
    model_args.add_argument('--anchors', default=None, type=float, nargs='+',
                                   help='Optional. A space separated list of anchors. '
                                        'By default used default anchors for model. \
                                            Only for `Intel`, `Xilinx`, `Hailo` platform.')

    io_args = parser.add_argument_group('Input/output options')
    io_args.add_argument('-n', '--name', default='ivit', 
                         help="Optional. The window name and rtsp namespace.")
    io_args.add_argument('-r', '--resolution', type=str, default=None, 
                         help="Optional. Only support usb camera. The resolution you want to get from source object.")
    io_args.add_argument('-f', '--fps', type=int, default=None,
                         help="Optional. Only support usb camera. The fps you want to setup.")
    io_args.add_argument('--no_show', action='store_true',
                         help="Optional. Don't display any stream.")

    args = parser.parse_args()
    # Parse Resoltion
    if args.resolution:
        args.resolution = tuple(map(int, args.resolution.split('x')))

    return args

def print_results(  detections:list, 
                    frame_id:int=-1, 
                    fps:Union[float, int]=-1 ):

    print(' ------------------- iVIT Frame # {} ; FPS {} ------------------ '.format(frame_id, fps))
    print(' Class ID | Confidence | XMIN | YMIN | XMAX | YMAX ')
    for detection in detections:
        xmin, ymin, xmax, ymax = detection.get_coords()
        print('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                    .format(detection.label, detection.score, xmin, ymin, xmax, ymax))
    return detections

def draw_results(   frame:ndarray, 
                    detections:list, 
                    palette: Dict[int, tuple]):

    for detection in detections:
        class_id = int(detection.id)
        color = palette[class_id]
        xmin, ymin, xmax, ymax = detection.get_coords()
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(frame, '{} {:.1%}'.format(detection.label, detection.score),
                    (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
    return frame

def main():

    # 1. Argparse
    args = build_argparser()

    # 2. Basic Parameters
    infer_metrx = Metric()

    # 3. Init Model
    model = iDetection(
        model_path = args.model,
        label_path = args.label,
        device = args.device,
        architecture_type = args.architecture_type,
        anchors = args.anchors,
        confidence_threshold = args.confidence_threshold )

    # 4. Init Source
    src = Source( 
        input = args.input, 
        resolution = (640, 480), 
        fps = 30 )

    # 5. Init Display
    if not args.no_show:
        dpr = Displayer( cv = True )

    # 6. Start Inference
    try:
        while True:
            # Get frame & Do infernece
            frame = src.read()
            
            results = model.inference(frame=frame)

            if args.no_show:
                # Just logout
                print_results(results, model.current_frame_id, infer_metrx.get_fps())
            
            else:
                # Draw results
                draw_results(frame, results, Palette())
                infer_metrx.paint_metrics(frame)

                # Draw FPS: default is left-top                     
                dpr.show(frame=frame)

                # Display
                if dpr.get_press_key() == ord('+'):
                    model.set_thres( model.get_thres() + 0.05 )
                elif dpr.get_press_key() == ord('-'):
                    model.set_thres( model.get_thres() - 0.05 )
                elif dpr.get_press_key() == ord('q'):
                    break

            # Update Metrix
            infer_metrx.update()

    except KeyboardInterrupt:
        log.info('Detected Key Interrupt !')

    finally:
        model.release()
        src.release()
        if not args.no_show: 
            dpr.release()


if __name__ == '__main__':
    sys.exit(main() or 0)
