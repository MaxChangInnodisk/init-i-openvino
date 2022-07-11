
import cv2
import numpy as np
import json

class Draw():

    def __init__(self) -> None:
        pass

    def draw_detections(self, info, palette, dict):
        frame = info['frame']
        output_transform = info['output_transform']
        model_name = dict['tag']
        if info["detections"] is not None and info["detections"] != []:
        # --------------------------Classificaiton
            if 'cls' in model_name:
                frame = output_transform.resize(frame)
                for detection in info["detections"]:
                    class_id = int(detection['id'])
                    label = detection['label']
                    xmin = max(int(detection['xmin']), 0)
                    ymin = max(int(detection['ymin']), 0)

                    cv2.putText(frame, '{} {:.1%}'.format(label, detection['score']),
                                (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, palette[0], 1)

        # --------------------------segmentation
            elif 'seg' in model_name:
                only_masks  =  info['only_masks']
                for detection in info["detections"]:
                    masks  = detection['objects']
                    frame = self.render_segmentation(frame, masks, palette, output_transform, only_masks)

        # --------------------------pose
            elif "pose" in model_name:
                point_score_threshold  =  info['prob_threshold']
                skeleton = info['skeleton']
                for detection in info["detections"]:
                    poses  = detection['poses']
                    frame = self.draw_poses(frame, poses, point_score_threshold, output_transform, skeleton, palette)

        # --------------------------Object detection
            elif "obj" in model_name:
                size = frame.shape[:2]
                frame = output_transform.resize(frame)
                for detection in info["detections"]:
                    class_id = int(detection['id'])
                    color = palette[class_id]
                    label = detection['label']
                    xmin = max(int(detection['xmin']), 0)
                    ymin = max(int(detection['ymin']), 0)
                    xmax = min(int(detection['xmax']), size[1])
                    ymax = min(int(detection['ymax']), size[0])
                    xmin, ymin, xmax, ymax = output_transform.scale([xmin, ymin, xmax, ymax])

                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    cv2.putText(frame, '{} {:.1%}'.format(label, detection['score']),
                                (xmin, ymin - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
            else:
                print("Tag name is wrong")
                
        return frame

    # Draw segmentaion detecotion reslut to frame
    def render_segmentation(self, frame, masks, visualiser, resizer, only_masks=False):
        # Catch apply color map
        output = visualiser.apply_color_map(masks)
        if not only_masks:
            # Position replace color
            output = np.floor_divide(frame, 2) + np.floor_divide(output, 2)
        return resizer.resize(output)

    # Draw pose detecotion reslut frame
    def draw_poses(self, img, poses, point_score_threshold, output_transform, skeleton, colors, draw_ellipses=False):
        # resize output shape
        img = output_transform.resize(img)
        if poses.size == 0:
            return img
        stick_width = 4

        img_limbs = np.copy(img)
        for pose in poses:
            # get every joints
            points = pose[:, :2].astype(np.int32)
            points = output_transform.scale(points)
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

class Json():

    def __init__(self) -> None:
        pass

    def read_json(self, path):
        with open(path) as f:
            return json.load(f)

def load_txt(path):
    cfg = open(path, "r")
    labels = []
    for line in cfg:
        labels.append(line.strip())

    return labels