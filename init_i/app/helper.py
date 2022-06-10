import cv2, math
FONT=cv2.LINE_AA
FONT_SCALE=1
FONT_THICKNESS=2

def get_text_size(label:str) -> tuple:
    """ return width, height in tuple """
    return cv2.getTextSize(label, FONT, FONT_SCALE, FONT_THICKNESS)[0]

def get_distance(pt, pt2):
    return math.hypot( pt2[0]-pt[0], pt2[1]-pt[1])