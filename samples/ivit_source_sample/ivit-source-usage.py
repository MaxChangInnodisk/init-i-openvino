# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import cv2, os, sys, time, argparse

sys.path.append( '/workspace/' )
from ivit_i.io import get_source_object, Source
from ivit_i.common import Metric

def get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', default='ivit', help="The window name.")
    parser.add_argument('-i', '--input', required=True, help="The input data.")
    parser.add_argument('-r', '--resolution', type=str, default=None, help="The resolution you want to get from source object.")
    parser.add_argument('-f', '--fps', type=int, default=None, help="The fps you want.")
    
    args = parser.parse_args()
    if args.resolution:
        args.resolution = tuple(map(int, args.resolution.split('x')))
    
    return args

def basi_main():

    args = get_argparser()

    src = Source(
        input = args.input,
        resolution = args.resolution,
        fps = args.fps )
    
    metric = Metric()
    
    try:
        
        while(True):
              
            frame = src.read()

            metric.paint_metrics(frame)
            
            cv2.imshow(args.name, frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'): break

            print('FPS: {}'.format(1//metric.update()))
    
    except KeyboardInterrupt:
        pass

    finally:
        src.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    basi_main()
