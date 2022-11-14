import numpy as np
import cv2, logging
import itertools as it
from ivit_i.app.common import (
    App,
    DETS,
    APP_KEY_NAME,
)

PROB        = "prob_threshold"
SKELETON    = "skeleton"
DET_POSE    = "poses"

class Default(App):

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.palette = PoseParam().colors

        logging.info("Get Pose Estimation Defualt Application")
    
    def get_params(self) -> dict:
        """ Define Counting Parameter Format """
        
        # Define Dictionary
        ret = {
            APP_KEY_NAME: self.def_param("string", "tracking", "define application name"),
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    
        return ret
    
    # Draw pose detecotion reslut frame
    def draw_poses(self, img, poses, point_score_threshold, skeleton, colors, draw_ellipses=False):
        # resize output shape
        if poses.size == 0:
            return img
        stick_width = 4

        img_limbs = np.copy(img)
        for pose in poses:
            # get every joints
            points = pose[:, :2].astype(np.int32)
            points_scores = pose[:, 2]

            # Draw joints.
            for i, (p, v) in enumerate(zip(points, points_scores)):
                if v > point_score_threshold:
                    cv2.circle(img, tuple(p), 1, colors[i], 2)

            # Draw limbs.
            for i, j in skeleton:
                if points_scores[i] > point_score_threshold and points_scores[j] > point_score_threshold:
                    if draw_ellipses:
                        middle = (points[i] + points[j]) // 2
                        vec = points[i] - points[j]
                        length = np.sqrt((vec * vec).sum())
                        angle = int(np.arctan2(vec[1], vec[0]) * 180 / np.pi)
                        polygon = cv2.ellipse2Poly(tuple(middle), (int(length / 2), min(int(length / 50), stick_width)),
                                                angle, 0, 360, 1)
                        cv2.fillConvexPoly(img_limbs, polygon, colors[j])
                    else:
                        cv2.line(img_limbs, tuple(points[i]), tuple(points[j]), color=colors[j], thickness=stick_width)
        # add to image
        cv2.addWeighted(img, 0.4, img_limbs, 0.6, 0, dst=img)

        return img

    def __call__(self, frame, info, draw=True):

        point_score_threshold   = info[PROB]
        skeleton                = info[SKELETON]

        for detection in info[DETS]:
            poses  = detection[DET_POSE]
            frame = self.draw_poses(frame, poses, point_score_threshold, skeleton, self.palette)

        return frame, "null"

class PoseParam():
    def __init__(self) -> None:
        # 17 color for joint
        self.colors = ( (255, 0, 0), (255, 0, 255), (170, 0, 255), (255, 0, 85),
                    (255, 0, 170), (85, 255, 0), (255, 170, 0), (0, 255, 0),
                    (255, 255, 0), (0, 255, 85), (170, 255, 0), (0, 85, 255),
                    (0, 255, 170), (0, 0, 255), (0, 255, 255), (85, 0, 255),
                    (0, 170, 255))
        # skeleton point
        self.default_skeleton = ((15, 13), (13, 11), (16, 14), (14, 12), (11, 12), (5, 11), 
                                (6, 12), (5, 6), (5, 7), (6, 8), (7, 9), (8, 10), 
                                (1, 2), (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6))