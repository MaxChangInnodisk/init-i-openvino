# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import cv2, os, sys, time, argparse

sys.path.append( '/workspace/' )
from ivit_i.io import Source, Displayer
from ivit_i.common import Metric, put_highlighted_text

def get_argparser():
    parser = argparse.ArgumentParser()
    
    args = parser.add_argument_group('Options')
    args.add_argument('-i', '--input', required=True, help="The input data.")
    args.add_argument('--cv', action='store_true', help="Display OpenCV Window")
    args.add_argument('--rtsp', action='store_true', help="Display OpenCV Window")
    
    io_args = parser.add_argument_group('Input/Output options')
    io_args.add_argument('-n', '--name', default='ivit', help="The window name and rtsp namespace.")
    io_args.add_argument('-r', '--resolution', type=str, default=None, help="The resolution you want to get from source object.")
    io_args.add_argument('-f', '--fps', type=int, default=None, help="The fps you want.")
    
    args = parser.parse_args()
    if args.resolution:
        args.resolution = tuple(map(int, args.resolution.split('x')))
    
    assert args.cv or args.rtsp, "Please select at least one displayer: [CV, RTSP]"
    
    return args

def basic_usage():

    args = get_argparser()
    
    src = Source(
        input = args.input,
        resolution = args.resolution,
        fps = args.fps )

    dpr = Displayer(
        cv=args.cv,
        rtsp=args.rtsp,
        name=args.name, 
        width=src.get_shape()[1], 
        height=src.get_shape()[0], 
        fps=src.get_fps() )
    
    if args.rtsp:
        print(dpr.get_rtsp_url())

    metric = Metric()
    
    try:

        while(True):

            frame = src.read()

            metric.paint_metrics(frame)

            dpr.show(frame)

            if dpr.get_press_key() == ord('q'): break

            print('FPS: {}'.format(1//metric.update()))

    except KeyboardInterrupt:
        pass

    finally:
        src.release()
        dpr.release()

if __name__ == "__main__":
    sys.exit(basic_usage() or 0)

