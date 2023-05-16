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

sys.path.append( '/workspace' )
from ivit_i.io import Source, Displayer
from ivit_i.core.models import iDetection
from ivit_i.common import Metric
from ivit_i.utils import Palette

def build_argparser():

    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument('-m', '--model', required=True,
                      help='Required. Path to an .xml file with a trained model '
                           'or address of model inference service if using ovms adapter.')
    available_model_wrappers = [name.lower() for name in iDetection.available_wrappers()]
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
    common_model_args.add_argument('-l', '--label', help='Optional. Labels mapping file.', default=None, type=str)
    common_model_args.add_argument('-t', '--confidence_threshold', default=0.6, type=float,
                                   help='Optional. Confidence threshold for detections.')
    common_model_args.add_argument('--anchors', default=None, type=float, nargs='+',
                                   help='Optional. A space separated list of anchors. '
                                        'By default used default anchors for model. Only for YOLOV4 architecture type.')
    # common_model_args.add_argument('--input_size', default=(600, 600), type=int, nargs=2,
    #                                help='Optional. The first image size used for CTPN model reshaping. '
    #                                     'Default: 600 600. Note that submitted images should have the same resolution, '
    #                                     'otherwise predictions might be incorrect.')
    # common_model_args.add_argument('--masks', default=None, type=int, nargs='+',
    #                                help='Optional. A space separated list of mask for anchors. '
    #                                     'By default used default masks for model. Only for YOLOV4 architecture type.')
    # common_model_args.add_argument('--layout', type=str, default=None,
    #                                help='Optional. Model inputs layouts. '
    #                                     'Ex. NCHW or input0:NCHW,input1:NC in case of more than one input.')
    # common_model_args.add_argument('--num_classes', default=None, type=int,
    #                                help='Optional. Number of detected classes. Only for NanoDet, NanoDetPlus '
    #                                     'architecture types.')

    io_args = parser.add_argument_group('Input/output options')
    io_args.add_argument('-r', '--resolution', type=str, default='', help="The size you want to get from source object. e.g. 1920x1080")
    io_args.add_argument('-f', '--fps', type=int, default=None, help="The size you want to get from source object.")
    io_args.add_argument('--no_show', help="Don't display.", action='store_true')

    return parser

def print_results(detections, frame_id, fps):

    print(' ------------------- iVIT Frame # {} ; FPS {} ------------------ '.format(frame_id, fps))
    print(' Class ID | Confidence | XMIN | YMIN | XMAX | YMAX ')
    for detection in detections:
        xmin, ymin, xmax, ymax = detection.get_coords()
        print('{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} '
                    .format(detection.label, detection.score, xmin, ymin, xmax, ymax))
    return detections

def draw_results(frame, detections, palette):

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
    args = build_argparser().parse_args()
    if args.architecture_type != 'yolov4' and args.anchors:
        log.warning('The "--anchors" option works only for "-at==yolov4". Option will be omitted')
    if args.resolution:
        args.resolution = tuple(map(int, args.resolution.split('x')))

    # 2. Basic Parameters
    frame_idx = 0
    infer_metrx = Metric()

    # 3. Init Model
    model = iDetection(
        model_path = args.model,
        label_path = args.label,
        device = args.device,
        architecture_type = args.architecture_type,
        anchors = args.anchors,
        confidence_threshold = args.confidence_threshold
    )

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

            frame = src.read()
            frame_idx += 1

            results = model.inference(frame=frame)

            print_results(results, frame_idx, infer_metrx.get_fps())
            draw_results(frame, results, Palette())
            infer_metrx.paint_metrics(frame)

            if not args.no_show:
                dpr.show(frame=frame)

                if dpr.get_press_key() == ord('+'):
                    model.set_thres( model.get_thres() + 0.05 )
                elif dpr.get_press_key() == ord('-'):
                    model.set_thres( model.get_thres() - 0.05 )
                elif dpr.get_press_key() == ord('q'):
                    break
            
            infer_metrx.update()

    except KeyboardInterrupt:
        pass

    finally:
        print('\n')
        model.release()
        src.release()

        if not args.no_show: 
            dpr.release()


if __name__ == '__main__':
    sys.exit(main() or 0)
