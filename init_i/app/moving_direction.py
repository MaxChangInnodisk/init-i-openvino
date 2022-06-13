import cv2, logging
from init_i.app.helper import FONT, FONT_SCALE, FONT_THICKNESS, get_text_size, get_distance
from init_i.app.pattern import App

class MovingDirection(App):
    
    def __init__(self, depend_labels: list) -> None:
        super().__init__(depend_labels)

    def __call__(self, frame, info):
        """
        1. Get all the bounding box and calculate the center point.
        2. Saving the center point and copy a preview one in the last. ("cnt_pts_cur_frame", "cnt_pts_prev_frame").
        3. Calculate the distance between current and preview center point. ( via math.hypot ).
        4. If the distance smaller than the limit_distance than we updating it in "track_obj" and remove from the "cnt_pts_cur_frame".
        5. ...
        """
        # get frame size
        size = frame.shape[:2]
        self.cnt_pts_cur_frame = []
        self.frame_idx += 1

        # capture all center point in current frame and draw the bounding box
        for detection in info["detections"]:

            if detection['label'] in self.depend_labels:
                x1, y1 = max(int(detection['xmin']), 0), max(int(detection['ymin']), 0)
                x2, y2 = min(int(detection['xmax']), size[1]), min(int(detection['ymax']), size[0])
                cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                
                # saving the center point
                self.cnt_pts_cur_frame.append( (cx, cy) )
                
                # draw the bbox, label text
                color = self.palette[ detection['label'] ]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, detection['label'], (x1, y1-10), FONT, FONT_SCALE, color, FONT_THICKNESS)

        # if the first frame web have to saving all object here
        if self.frame_idx <= 1:  
                                
            for pt in self.cnt_pts_cur_frame:
                for pt2 in self.cnt_pts_prev_frame:
                    
                    if get_distance(pt, pt2) < self.limit_distance:
                        self.track_obj[ self.track_idx ]=pt
                        self.track_idx +=1
        else:
            track_obj_copy = self.track_obj.copy()
            cnt_pts_cur_frame_copy = self.cnt_pts_cur_frame.copy()
            for idx, pt2 in track_obj_copy.items():
                obj_exist = False
                for pt in cnt_pts_cur_frame_copy:                
                    
                    if get_distance(pt, pt2) < self.limit_distance:
                        self.track_obj[idx]=pt
                        if pt in self.cnt_pts_cur_frame:
                            self.cnt_pts_cur_frame.remove(pt)
                        obj_exist = True
                        continue

                if not obj_exist:
                    self.track_obj.pop(idx)
        # adding the remaining point to track_obj
        for pt in self.cnt_pts_cur_frame:
            self.track_obj[ self.track_idx ]=pt
            self.track_idx +=1
        
        # draw the arrow
        if self.prev_track_obj!=[]:

            for idx, pt in self.track_obj.items():
                # cv2.putText(frame, str(idx), (pt[0], pt[1]), 0, 1, (0,255,50), 3)
                if idx in self.prev_track_obj:
                    prev_pt = self.prev_track_obj[idx]
                    bias = 20
                    prev_x = prev_pt[0] + bias*(-1 if prev_pt[0]>pt[0] else 1)
                    prev_y = prev_pt[1] + bias*(-1 if prev_pt[1]>pt[1] else 1)
                    pt_x = pt[0] + bias*(-1 if prev_pt[0]<pt[0] else 1)
                    pt_y = pt[1] + bias*(-1 if prev_pt[0]<pt[0] else 1)
                    
                    cv2.arrowedLine(frame, (pt_x, pt_y) ,(prev_x, prev_y), (0, 255, 0), 5, tipLength=0.5)
        
        self.prev_track_obj = self.track_obj.copy()
        self.cnt_pts_prev_frame = self.cnt_pts_cur_frame.copy()
        
        return frame
