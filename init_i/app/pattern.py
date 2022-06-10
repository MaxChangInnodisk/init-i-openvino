import random

class App(object):
    def __init__(self, depend_labels:list) -> None:
        self.frame_idx = 0
        self.track_obj = {}
        self.track_idx = 0
        self.limit_distance = 30
        self.prev_track_obj = []
        self.cnt_pts_cur_frame = []
        self.cnt_pts_prev_frame = []

        self.depend_labels = depend_labels
        self.palette = self.get_palette(depend_labels)

    @staticmethod
    def get_palette( self, labels:list ):
        ret = {}
        for label in labels:
            color = self.get_random_color()
            ret[label]=color
        return ret

    @staticmethod
    def get_random_color( self, format='bgr'):
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        return [r, g, b] if format=='rgb' else [b, g, r]