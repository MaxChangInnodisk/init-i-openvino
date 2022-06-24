import cv2, logging
from init_i.app.helper import FONT, FONT_SCALE, FONT_THICKNESS, get_text_size, get_distance
from init_i.app.common import App
import numpy as np

BORDER = 1
CNT_COLOR = ( 0, 0, 255)
DISTANCE = 200


class Heatmap(App):
    
    def __init__(self, depend_labels:list) -> None:
        super().__init__(depend_labels)
        self.alpha = 0.5

    def __call__(self, frame, info):

        # get frame size
        size = frame.shape[:2]
        cnts = []

        # capture all center point in current frame and draw the bounding box
        for detection in info["detections"]:

            label = detection['label']

            # check if the label is in the labels we select ( depend_on )
            if label in self.depend_labels:

                x1, y1 = max(int(detection['xmin']), 0), max(int(detection['ymin']), 0)
                x2, y2 = min(int(detection['xmax']), size[1]), min(int(detection['ymax']), size[0])
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                
                # draw the bbox, label text
                # cv2.circle(frame, (cx,cy), 3, CNT_COLOR, -1)

                # store cneter points
                cnts.append( (cx, cy) )
        
        # create density map
        density_map = np.zeros( (size[0], size[1]) )
        color_map = np.empty([size[0], size[1], 3], dtype=int)


        # calculate distance and density
        # logging.warning("H: {}, W:{}".format(size[0], size[1]))
        for i in range(size[0]):
            for j in range(size[1]):
                for cnt in cnts:
                    dis = get_distance(cnt, (j,i))

                    dis = 1 if dis==0 else dis
                    
                    if dis <= DISTANCE*0.25:
                        density_map[i][j] += 50
                    elif dis <= DISTANCE:
                        density_map[i][j] +=  (DISTANCE-dis)/(DISTANCE*0.75) * 50

                    if density_map[i][j]>=255:
                        density_map[i][j] = 255

                for k in range(3):
                    color_map[i][j][k] = density_map[i][j]
        
        # convert to heamap
        heatmap = cv2.applyColorMap(color_map.astype(np.uint8), cv2.COLORMAP_JET)
        
        # add weights

        frame = cv2.addWeighted(frame, self.alpha, heatmap, 1-self.alpha, 0) 

        # return frame
        return frame
