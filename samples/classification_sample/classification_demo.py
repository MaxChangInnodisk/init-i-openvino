#!/usr/bin/env python3
# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import logging as log
import cv2, sys
from argparse import ArgumentParser, SUPPRESS

sys.path.append( '/workspace' )
from ivit_i.io import Source, Displayer
from ivit_i.core.models import iClassification
from ivit_i.common import Metric, put_highlighted_text
from ivit_i.utils import Palette

def build_argparser():

    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    
    args.add_argument('-m', '--model', required=True,
                      help='Required. Path to an .xml file with a trained model '
                           'or address of model inference service if using OVMS adapter.')
    args.add_argument('-i', '--input', required=True,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    args.add_argument('-d', '--device', default='CPU', type=str,
                      help='Optional. Specify the target device to infer on; CPU, GPU, HDDL or MYRIAD is '
                           'acceptable. The demo will look for a suitable plugin for device specified. '
                           'Default value is CPU.')

    common_model_args = parser.add_argument_group('Common model options')
    common_model_args = parser.add_argument_group('Common model options')
    common_model_args.add_argument('-l', '--label', help='Optional. Labels mapping file.', default=None, type=str)
    common_model_args.add_argument('-t', '--confidence_threshold', default=0.1, type=float,
                                   help='Optional. Confidence threshold for detections.')
    common_model_args.add_argument('-topk', help='Optional. Number of top results. Default value is 5. Must be from 1 to 10.', default=5,
                                   type=int, choices=range(1, 11))

    io_args = parser.add_argument_group('Input/output options')
    io_args.add_argument('-n', '--name', default='ivit', help="The window name and rtsp namespace.")
    io_args.add_argument('-r', '--resolution', type=str, default=None, help="The resolution you want to get from source object.")
    io_args.add_argument('-f', '--fps', type=int, default=None, help="The fps you want.")
    io_args.add_argument('--no_show', help="Don't display.", action='store_true')

    return parser

def print_results(detections, frame_id, fps=None):

    label_max_len = 0
    if detections:
        labels = [ cl[1] for cl in detections]
        label_max_len = len(max(labels, key=len))

    print(' ------------------- Frame # {} ; FPS {} ------------------- '.format(frame_id, fps ))

    if label_max_len != 0:
        print(' Class ID | {:^{width}s}| Confidence '.format('Label', width=label_max_len))
    else:
        print(' Class ID | Confidence ')

    for class_id, class_label, score in detections:
        if class_label != "":
            print('{:^9} | {:^{width}s}| {:^10f}'.format(class_id, class_label, score, width=label_max_len))
        else:
            print('{:^9} | {:^10f}'.format(class_id, score))
    
    return detections

def draw_results(frame, detections, palette=None):

    class_label = ""
    if detections:
        class_label = detections[0][1]
    font_scale = 0.7
    label_height = cv2.getTextSize(class_label, cv2.FONT_HERSHEY_COMPLEX, font_scale, 2)[0][1]
    initial_labels_pos =  frame.shape[0] - label_height * (int(1.5 * len(detections)) + 1)

    if (initial_labels_pos < 0):
        initial_labels_pos = label_height
        log.warning('Too much labels to display on this frame, some will be omitted')
    offset_y = initial_labels_pos

    header = "Label:     Score:"
    label_width = cv2.getTextSize(header, cv2.FONT_HERSHEY_COMPLEX, font_scale, 2)[0][0]
    put_highlighted_text(frame, header, (frame.shape[1] - label_width, offset_y),
        cv2.FONT_HERSHEY_COMPLEX, font_scale, (255, 0, 0), 2)

    for idx, class_label, score in detections:
        color = palette[idx] if palette else (255, 0, 0)
        label = '{}. {}    {:.2f}'.format(idx, class_label, score)
        label_width = cv2.getTextSize(label, cv2.FONT_HERSHEY_COMPLEX, font_scale, 2)[0][0]

        offset_y += int(label_height * 1.5)
        put_highlighted_text(frame, label, (frame.shape[1] - label_width, offset_y),
            cv2.FONT_HERSHEY_COMPLEX, font_scale, color, 2)
    
    return frame

def main():

    # 1. Argparse
    args = build_argparser().parse_args()
    if args.resolution:
        args.resolution = tuple(map(int, args.resolution.split('x')))
    
    # 2. Basic Parameters
    frame_idx = 0
    infer_metrx = Metric()
    
    # 3. Init Model
    model = iClassification(
        model_path = args.model,
        label_path = args.label,
        device = args.device,
        confidence_threshold = args.confidence_threshold,
        topk = args.topk )
    
    # 4. Init Source
    src = Source(   
        input = args.input, 
        resolution = args.resolution, 
        fps = args.fps )
    
    # 5. Init Display
    if not args.no_show:
        dpr = Displayer( cv = True )
    
    # 6. Start Inference
    try:
        while(True):
            
            frame = src.read()                                              # Get frame
            frame_idx += 1                                                  # Update Frame ID
            results = model.inference( frame = frame )                      # Do Inference

            # print_results(results, frame_idx, infer_metrx.get_fps() )       # Log
            draw_results(frame, results, Palette())                         # Draw Labels
            infer_metrx.paint_metrics(frame)                                # Draw FPS: default is left-top

            if not args.no_show:               
                dpr.show(frame=frame)                                       # Display
                if dpr.get_press_key()==ord('q'):                           # Get Press Key
                    break

            infer_metrx.update()                                            # Update Metrix

    except KeyboardInterrupt: 
        pass

    finally:
        print('\n')
        model.release()     # Release Model
        src.release()       # Release Source

        if not args.no_show: 
            dpr.release()   # Release Display

if __name__ == '__main__':
    sys.exit(main() or 0)