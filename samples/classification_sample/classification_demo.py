#!/usr/bin/env python3
# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import logging as log
import cv2, sys
from typing import Union, List, Tuple, Dict
from numpy import ndarray
from argparse import ArgumentParser, SUPPRESS

from ivit_i.common import ivit_logger
from ivit_i.io import Source, Displayer
from ivit_i.core.models import iClassification
from ivit_i.common import Metric
from ivit_i.utils import Palette

def build_argparser():

    parser = ArgumentParser(add_help=False)

    basic_args = parser.add_argument_group('Basic options')
    basic_args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    basic_args.add_argument('-m', '--model', required=True, help='the path to model')
    basic_args.add_argument('-i', '--input', required=True,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    basic_args.add_argument('-l', '--label', help='Optional. Labels mapping file.', default=None, type=str)
    basic_args.add_argument('-d', '--device', type=str,
                      help='Optional. `Intel` support [ `CPU`, `GPU` ] \
                            `Hailo` is support [ `HAILO` ]; \
                            `Xilinx` support [ `DPU` ]; \
                            `dGPU` support [ 0, ... ] which depends on the device index of your GPUs; \
                            `Jetson` support [ 0 ].' )
    
    model_args = parser.add_argument_group('Model options')
    model_args.add_argument('-t', '--confidence_threshold', default=0.1, type=float,
                                   help='Optional. Confidence threshold for detections.')
    model_args.add_argument('-topk', help='Optional. Number of top results. Default value is 5. Must be from 1 to 10.', default=5,
                                   type=int, choices=range(1, 11))

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

def put_highlighted_text(   frame: ndarray, 
                            message: str, 
                            position: Union[list, tuple], 
                            font_face: int, 
                            font_scale: Union[float, int], 
                            color: Union[list, tuple], 
                            thickness: int ):
    """Draw a text with highlight """
    cv2.putText(frame, message, position, font_face, font_scale, (255, 255, 255), thickness + 1) # white border
    cv2.putText(frame, message, position, font_face, font_scale, color, thickness)

def print_results(  detections:List[Tuple[int, str, float]], 
                    frame_id:int=-1, 
                    fps:float=None) -> None:
    """Print results on console

    Args:
        detections (List[Tuple[int, str, float]]): the iClassification output
        frame_id (int, optional): the current frame index. Defaults to -1.
        fps (float, optional): the current fps. Defaults to None.
    """

    label_max_len = 0
    title = ' --------- Frame # {} ; FPS {} --------- '.format(frame_id, fps )
    sub_title = ' Class ID | Confidence '

    # Get the maxmum label length
    if detections:
        label_max_len = max( map( lambda x: len(x[1]), detections ))
        if label_max_len != 0:
            sub_title = ' Class ID | {:^{width}s}| Confidence '.format('Label', width=label_max_len)

    # Print Information
    log.info(title)
    log.info(sub_title)
    for label_idx, label_name, label_score in detections:
        if label_name != "":
            log.info('{:^9} | {:^{width}s}| {:^10f}'.format(label_idx, label_name, label_score, width=label_max_len))
        else:
            log.info('{:^9} | {:^10f}'.format(label_idx, label_score))
    

def draw_results(   frame:ndarray, 
                    detections: List[Tuple[int, str, float]], 
                    palette: Dict[int, tuple] = None,
                    font_scale: float = 0.7,
                    font_face: int = cv2.FONT_HERSHEY_COMPLEX,
                    font_thick: int = 2,
                    default_color: tuple = (255, 0, 0) ) -> None:
    """Draw results

    Args:
        frame (ndarray): frame
        detections (List[Tuple[int, str, float]]): the iClassification output
        palette (Dict[int, tuple], optional): the custom platte. Defaults to None.
        font_scale (float, optional): opencv font scale. Defaults to 0.7.
        font_face (int, optional): opencv font face. Defaults to cv2.FONT_HERSHEY_COMPLEX.
        font_thick (int, optional): opencv font thick. Defaults to 2.
        default_color (tuple, optional): if palette not set then the color will be the default color. Defaults to (255, 0, 0).
    """

    # Initialize Position
    first_label_name = detections[0][1] if detections else ""
    label_height = cv2.getTextSize(first_label_name, font_face, font_scale, 2)[0][1]
    initial_labels_pos =  frame.shape[0] - label_height * (int(1.5 * len(detections)) + 1)

    if (initial_labels_pos < 0):
        initial_labels_pos = label_height
        log.warning('Too much labels to display on this frame, some will be omitted')
    offset_y = initial_labels_pos

    # Draw Header
    header = "Label:     Score:"
    label_width = cv2.getTextSize(header, font_face, font_scale, font_thick)[0][0]
    put_highlighted_text(frame, header, (frame.shape[1] - label_width, offset_y),
        font_face, font_scale, default_color, font_thick)

    # Draw Detections
    for label_idx, label_name, label_score in detections:
        
        # Get Color
        color = palette[label_idx] if palette else default_color
        
        # Get Label Content
        label = '{}. {}    {:.2f}'.format(label_idx, label_name, label_score)
        label_width = cv2.getTextSize(label, font_face, font_scale, font_thick)[0][0]

        # Draw Label Content
        offset_y += int(label_height * 1.5)
        put_highlighted_text(frame, label, (frame.shape[1] - label_width, offset_y),
            font_face, font_scale, color, font_thick)
    
    return frame

def main():

    # 1. Argparse
    args = build_argparser()

    # 2. Basic Parameters
    infer_metrx = Metric()
    
    # 3. Init Model
    model = iClassification(
        model_path = args.model,
        label_path = args.label,
        confidence_threshold = args.confidence_threshold,
        device=args.device,
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
    frame_idx = 0
    try:
        while(True):
            # Get frame & Do infernece
            frame = src.read()       
            detections = model.inference( frame )

            if args.no_show:
                # Just logout
                frame_idx += 1
                print_results(
                    detections, frame_idx, 
                    infer_metrx.get_fps() )
            else:
                # Draw results
                draw_results(
                    frame, detections, Palette() )
                
                # Draw FPS: default is left-top                     
                infer_metrx.paint_metrics(frame)
                
                # Display
                dpr.show(frame=frame)                   
                if dpr.get_press_key()==ord('q'):
                    break

            # Update Metrix
            infer_metrx.update()

    except KeyboardInterrupt: 
        log.info('Detected Key Interrupt !')

    finally:
        model.release()     # Release Model
        src.release()       # Release Source
        if not args.no_show: 
            dpr.release()   # Release Display

if __name__ == '__main__':
    sys.exit(main() or 0)