import cv2, logging
from helper import FONT, FONT_SCALE, FONT_THICKNESS, get_text_size, get_distance
from pattern import App
class Counting(App):
    
    def __init__(self, depend_labels: list) -> None:
        super().__init__(depend_labels)

    def __call__(self, frame, info):
        """
        1. Get all the bounding box and calculate the center point.
        2. Saving the center point and copy a preview one in the last. ("self.cnt_pts_cur_frame", "self.cnt_pts_prev_frame").
        3. Calculate the distance between current and preview center point. ( via math.hypot ).
        4. If the distance smaller than the limit_distance than we updating it in "track_obj" and remove from the "self.cnt_pts_cur_frame".
        5. The remaining items in "self.cnt_pts_cur_frame" is the new one, add to "track_obj".
        6. Draw the information in it.
        """
        # get frame size
        self.cnt_pts_cur_frame = []
        size = frame.shape[:2]

        # update frame index
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
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255,0), 2)
                cv2.putText(frame, detection['label'], (x1, y1-10), FONT, FONT_SCALE, (0, 255, 0), FONT_THICKNESS)

        # if the first frame web have to saving all object here
        if self.frame_idx <= 1:  
            for pt in self.cnt_pts_cur_frame:
                for pt2 in self.cnt_pts_prev_frame:
                    
                    # calculate the distance, if smaller then limit_distance, then it might the same one
                    if get_distance(pt, pt2) < self.limit_distance:
                        self.track_obj[self.track_idx]=pt
                        self.track_idx +=1

        # if not the firt frame, we update the center point and separate the new one
        else:
            track_obj_copy = self.track_obj.copy()
            self.cnt_pts_cur_frame_copy = self.cnt_pts_cur_frame.copy()
            
            for idx, pt2 in track_obj_copy.items():
                
                # if object not exist we have to remove the the disappear one
                obj_exist = False

                for pt in self.cnt_pts_cur_frame_copy:                
                    
                    # calculate the distance, if the some one we have to update the center point
                    if get_distance(pt, pt2) < self.limit_distance:
                        self.track_obj[idx]=pt
                        
                        if pt in self.cnt_pts_cur_frame:
                            self.cnt_pts_cur_frame.remove(pt)
                        obj_exist = True

                if not obj_exist:
                    self.track_obj.pop(idx)

        # adding the remaining point to track_obj
        for pt in self.cnt_pts_cur_frame:
            self.track_obj[self.track_idx]=pt
            self.track_idx +=1
        
        # draw the number text on frame
        for idx, pt in self.track_obj.items():
            wid, hei = get_text_size(str(idx))
            cv2.putText(frame, str(idx), (pt[0]-(wid//2), pt[1]+(hei//2)), 0, 1, (0,255,50), 3)
        # draw the total number on left-top corner
        total_num = list(self.track_obj.keys())[-1]
        content = f"Detected {total_num} {label}"
        wid, hei = get_text_size(content)
        cv2.putText(frame, content, (10, 10+(hei)), 0, 1, (0,255,50), 3)

        # update the preview information
        self.cnt_pts_prev_frame = self.cnt_pts_cur_frame.copy()

        # return frame and total number
        return frame, total_num
