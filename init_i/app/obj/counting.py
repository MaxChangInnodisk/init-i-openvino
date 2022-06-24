import enum
import cv2, logging
from init_i.app.helper import FONT, FONT_SCALE, FONT_THICKNESS, get_text_size, get_distance
from init_i.app.common import App

BORDER = 2
# COLOR = ( 0, 0, 255 )
FONT=cv2.LINE_AA
FONT_SCALE=1
FONT_THICKNESS=3


class Counting(App):
    
    def __init__(self, depend_labels:list) -> None:
        super().__init__(depend_labels)
        # logging.warning(depend_labels)
        # logging.warning(type(depend_labels))
        self.total_num = dict()

    def __call__(self, frame, info):
        """
        """
        # clear data
        for key in self.cnt_pts_cur_frame:
            self.cnt_pts_cur_frame[key] = []

        # get frame size
        size = frame.shape[:2]
        # update frame index
        self.frame_idx += 1

        # reset
        for label in self.total_num:
            self.total_num[label] = 0
        
        # capture all center point in current frame and draw the bounding box
        for detection in info["detections"]:

            label = detection['label']

            # check if the label is in the labels we select ( depend_on )
            if label in self.depend_labels:

                # if not in detected_labels, we append it
                if not ( label in self.detected_labels ):
                    self.detected_labels.append(label)

                # reset
                if not ( label in self.total_num ):
                    self.total_num[label] = 0

                self.total_num[label] += 1

                x1, y1 = max(int(detection['xmin']), 0), max(int(detection['ymin']), 0)
                x2, y2 = min(int(detection['xmax']), size[1]), min(int(detection['ymax']), size[0])
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                
                # draw the bbox, label text
                cv2.rectangle(frame, (x1, y1), (x2, y2), self.palette[label], BORDER)
            
        # draw the number text on frame
        for label_num, label in enumerate(self.detected_labels):

            cnt = "Detected {} {}".format(self.total_num[label], label)
            wid, hei = get_text_size(cnt)
            hei = hei+14
            cv2.putText(frame, cnt, (10, 10+(hei*(label_num+1)) ), FONT, FONT_SCALE, self.palette[label], FONT_THICKNESS)

        return frame
