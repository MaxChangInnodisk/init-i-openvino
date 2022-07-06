
import cv2, logging, copy, math
from init_i.app.helper import FONT, FONT_SCALE, FONT_THICKNESS, get_text_size, get_distance
from init_i.app.common import App

def get_coord_distance(p1 , p2):

    coordinate_distance = math.sqrt( ((int(p1[0])-int(p2[0]))**2)+((int(p1[1])-int(p2[1]))**2) )

    return coordinate_distance

class MovingDirection(App):
    
    def __init__(self, depend_labels:list) -> None:
        super().__init__(depend_labels)
        # logging.warning(depend_labels)
        # logging.warning(type(depend_labels))
        self.total_num = dict()
        self.prev_track_obj = {}

    def __call__(self, frame, info):
        """
        1. Get all the bounding box and calculate the center point.
        2. Saving the center point and copy a preview one in the last. ("self.cnt_pts_cur_frame", "self.cnt_pts_prev_frame").
        3. Calculate the distance between current and preview center point. ( via math.hypot ).
        4. If the distance smaller than the limit_distance than we updating it in "track_obj" and remove from the "self.cnt_pts_cur_frame".
        5. The remaining items in "self.cnt_pts_cur_frame" is the new one, add to "track_obj".
        6. Draw the information in it.
        """
        # clear data
        for key in self.cnt_pts_cur_frame:
            self.cnt_pts_cur_frame[key] = []

        # get frame size
        size = frame.shape[:2]
        # update frame index
        self.frame_idx += 1

        # capture all center point in current frame and draw the bounding box
        for detection in info["detections"]:

            label = detection['label']

            # check if the label is in the labels we select ( depend_on )
            if label in self.depend_labels:

                # if not in detected_labels, we append it
                if not ( label in self.detected_labels ):
                    self.detected_labels.append(label)

                x1, y1 = max(int(detection['xmin']), 0), max(int(detection['ymin']), 0)
                x2, y2 = min(int(detection['xmax']), size[1]), min(int(detection['ymax']), size[0])
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                
                # saving the center point
                self.cnt_pts_cur_frame[label].append( (cx, cy) )
                
                # draw the bbox, label text
                cv2.rectangle(frame, (x1, y1), (x2, y2), self.palette[label], 2)
                # cv2.putText(frame, label, (x1, y1-10), FONT, FONT_SCALE, self.palette[label], FONT_THICKNESS)

        # if the first frame web have to saving all object here
        if self.frame_idx <= 1:  
            for label in self.detected_labels:
                for pt in self.cnt_pts_cur_frame[label]:
                    for pt2 in self.cnt_pts_prev_frame[label]:
                        
                        # calculate the distance, if smaller then limit_distance, then it might the same one
                        if get_distance(pt, pt2) < self.limit_distance:
                            self.track_obj[label][ self.track_idx[label] ]=pt
                            self.track_idx[label] +=1

        # if not the firt frame, we update the center point and separate the new one
        else:
            for label in self.detected_labels:

                track_obj_copy = self.track_obj[label].copy()
                self.cnt_pts_cur_frame_copy = self.cnt_pts_cur_frame[label].copy()
                
                for idx, pt2 in track_obj_copy.items():
                    
                    # if object not exist we have to remove the the disappear one
                    obj_exist = False

                    for pt in self.cnt_pts_cur_frame_copy:                
                        
                        # calculate the distance, if the some one we have to update the center point
                        if get_distance(pt, pt2) < self.limit_distance:
                            self.track_obj[label][idx]=pt
                            
                            if pt in self.cnt_pts_cur_frame[label]:
                                self.cnt_pts_cur_frame[label].remove(pt)
                            obj_exist = True

                    if not obj_exist:
                        self.track_obj[label].pop(idx)

        # adding the remaining point to track_obj
        for label_num, label in enumerate(self.detected_labels):

            for pt in self.cnt_pts_cur_frame[label]:
                self.track_obj[label][ self.track_idx[label] ]=pt
                self.track_idx[label] +=1

            # draw the arrow text on frame   
            if label in self.prev_track_obj:

                if self.frame_idx > 1:

                    for idx, cur_pt in self.track_obj[label].items():
                    
                        if not (idx in self.prev_track_obj[label]):
                            continue

                        # get previous points
                        prev_pt = self.prev_track_obj[label][idx]
                        
                        # define the lenth of arrow
                        arrowLength = 50

                        # split x and y
                        (cur_x, cur_y), (prev_x, prev_y) = cur_pt, prev_pt
                        
                        # calculate momentum
                        distance = get_coord_distance( prev_pt, cur_pt )
                        scale = arrowLength/(1 if distance==0 else distance)
                        momentum_x, momentum_y = ( cur_x - prev_x), ( cur_y - prev_y)
                        bias_x , bias_y = int(scale * momentum_x), int(scale * momentum_y)

                        # add bias
                        cur_x, prev_x = (cur_x + bias_x), (prev_x - bias_x)
                        cur_y, prev_y = (cur_y + bias_y), (prev_y - bias_y)
                        
                        # cv2.circle(frame, (prev_x, prev_y), 3, (0, 0, 255), 3)
                        # cv2.circle(frame, (cur_x, cur_y), 3, (0, 255, 255), 3)

                        cv2.arrowedLine(frame, (prev_x, prev_y), (cur_x, cur_y), self.palette[label], 5, tipLength=0.5)
        
                # update the preview information    
                self.cnt_pts_prev_frame[label] = self.cnt_pts_cur_frame[label].copy()
                
            else:
                self.prev_track_obj.update( {label: list()})

            self.prev_track_obj[label] = self.track_obj[label].copy()

        return frame
