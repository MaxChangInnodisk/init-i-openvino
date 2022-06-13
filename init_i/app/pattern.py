import logging
import random, json, os

def read_json(path):
    with open(path) as f:
        return json.load(f)

class App(object):
    def __init__(self, depend_labels:list) -> None:
        self.frame_idx = 0
        self.track_obj = {}
        self.track_idx = {}
        self.limit_distance = 30
        self.prev_track_obj = {}
        self.cnt_pts_cur_frame = {}
        self.cnt_pts_prev_frame = {}
        
        self.depend_labels = depend_labels
        self.palette = self.get_palette(depend_labels)

    def get_random_palette( self, labels:list ):
        ret = {}
        for label in labels:
            color = self.get_random_color()
            ret[label]=color

            # update label
            self.prev_track_obj[label]=list()
            self.cnt_pts_cur_frame[label]=list()
            self.cnt_pts_prev_frame[label]=list()
            self.track_obj[label]=dict()
            self.track_idx[label]=0
            
        return ret

    def get_palette( self, labels):
        ret = {}
        path = "init_i/app/palette.json"
        if not os.path.exists(path):
            path = "./palette.json"
        if not os.path.exists(path):
            raise Exception("Couldn't find palette")
        
        color_map = read_json(path)
        
        for idx, label in enumerate(labels):
            idx = str(idx+1)
            ret[label]=color_map[idx]

            # update label
            self.prev_track_obj[label]=list()
            self.cnt_pts_cur_frame[label]=list()
            self.cnt_pts_prev_frame[label]=list()
            self.track_obj[label]=dict()
            self.track_idx[label]=0

        return ret

    def get_random_color( self, format='bgr'):
        
        r, g, b = 0, 0, 0

        r = random.randint(0,255)

        g = random.randint(0,255)

        b = random.randint(0,255)

        return [r, g, b] if format=='rgb' else [b, g, r]