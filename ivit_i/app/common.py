import logging, random, time
from ivit_i.utils import handle_exception
from ivit_i.utils.draw_tools import TAG
import logging, random, json, os, math, time, cv2
from datetime import datetime

from ivit_i.utils.draw_tools import (
    PADDING,
    get_scale,
    get_text_size
)

# CV Draw
FONT            = cv2.LINE_AA
FONT_SCALE      = 1
FONT_THICKNESS  = 2

# Time 
TIME_FORMAT     = '%Y/%m/%d %H:%M:%S'

# Model Type
TAG             = 'tag'

# Inference
DETS            = "detections"
FRAME           = "frame"
LABEL           = "label"
OUT_RESOL       = "output_resolution"

# App - Basic
APP_KEY         = "application"
APP_KEY_NAME    = "name"
APP_KEY_DEPEND  = "depend_on"

DEFAULT_KEY     = "default"
TRACK_KEY       = "tracking"
DIRECTION_KEY   = "direction"
COUNTING_KEY    = "counting"
AREA_KEY        = "area"
HEAT_KEY        = "heatmap"

# App - Logic Judgment
APP_LOGIC       = "logic"
APP_LOGIC_THRES = "logic_thres"
APP_ALARM       = "alarm"
APP_ALARM_TIME  = "alarm_time"

# Draw
CV_WIN          = "Detection Results"
DET_COLOR       = ( 0, 255, 0 )
WARN_COLOR      = ( 0, 0, 255 )
AREA_COLOR      = ( 0, 0, 255 )

class LogicOperator():

    def __init__(self, logic, thres) -> None:
        
        self.executor   = None
        self.thres      = thres
        
        if   logic== ">"  : self.executor=self.greater
        elif logic== "="  : self.executor=self.equal
        elif logic== "<"  : self.executor=self.less
        elif logic== "!=" : self.executor=self.not_equal
        else:
            raise Exception("Unkown Logic ... ( {} )".format(logic))

        logging.info(f"Create Logic Operator: { logic} { thres }")
            
    def greater(self, value ):
        return (value>self.thres)
    
    def less(self, value):
        return (value<self.thres)
    
    def equal(self, value):
        return (value==self.thres)
    
    def not_equal(self, value):
        return (value!=self.thres)

    def __call__(self, value):
        return self.executor(value)

class Timer():

    def __init__(self) -> None:
        self.t_prev = None
        self.t_thres = None
        self.t_cur = None
        self.t_delta_prev = 0
        pass

    def set_time(self):
        self.t_prev = time.time()
        return self.t_prev
    
    def set_thres(self, t_thres):
        self.t_thres = t_thres
        return self.t_thres
    
    def check_time(self, t_cur=None, log=False):
        
        ret = False
        t_cur = time.time() if t_cur==None else t_cur

        t_delta = t_cur - self.t_prev
        if log:
            if int(self.t_delta_prev) != int(t_delta):
                logging.info("[ Timer ] Delta Time: {}".format(int(t_delta)))
                self.t_delta_prev = t_delta

        if ( t_delta) >= self.t_thres :
            ret = True
            
        return ret

    def get_delta_time(self, t_cur=None, log=False):
        
        t_cur = time.time() if t_cur==None else t_cur
        t_delta = int(t_cur - self.t_prev)
        if log: logging.info("[ Timer ] Delta Time: {}".format(t_delta))
        return t_delta
            
class App(object):

    def __init__(self, config:dict) -> None:

        if(config[TAG]!='pose'):
            self.depend_labels = get_depend_label(config)
            self.palette = self.get_palette(self.depend_labels)

        self.detected_labels = []

        self.frame_idx = 0
        self.frame_size = None
        self.trg_scale  = None
        self.trg_thick  = None
        self.padding    = None

        self.text_wid   = None
        self.text_hei   = None
        self.text_base  = None
        self.text_pos   = None
        self.text_draw  = ""
        self.text_color = ( 0, 0, 0)
    
        # About App
        self.config = config
        self.app_config = config[APP_KEY]
        self.app_info   = ""
        self.alarm      = ""

    def def_param(self, in_type, in_value, in_descr=""): 
        return { "type": in_type, "value": in_value, "describe": in_descr }

    def get_params(self):
        """
        Design the configuration of the application:

        - Example: Counting
        - Return:
            - Type: Dict()
            - Content: 
                {
                    "name": "counting",
                    "depend_on": [ "car" ],
                    "logic": "=",
                    "logic_thres": 3,
                    "alarm": "Three Car Here",
                    "alarm_time": 3
                }        
        """
        pass

    def get_output_text(self):
        return "Temp ..."

    def init_cv_win(self):
        cv2.namedWindow(CV_WIN,cv2.WINDOW_KEEPRATIO)
        cv2.setWindowProperty(CV_WIN,cv2.WND_PROP_ASPECT_RATIO,cv2.WINDOW_KEEPRATIO)

        cv2.setWindowProperty( CV_WIN, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN )

    def init_draw_param(self, frame):

        # if frame_size not None means it was already init 
        if( self.frame_size != None): 
            return None

        scale           = get_scale(frame)
        self.frame_size = frame.shape[:2]
        self.trg_scale  = scale
        self.trg_thick  = math.ceil(scale)
        self.padding    = int(PADDING*scale)
        
        ( w, h ), baseline = get_text_size( self.get_output_text(),                                    
                                            self.trg_scale, 
                                            self.trg_thick )

        self.text_wid, self.text_hei, self.text_base = w, h , baseline

    def check_digit_key(self, key):
        return int(key) if(key.isdigit()) else key
            
    def get_param_value(self, config, key, default=None):
        if key in config: 
            logging.info("Get Application Key/Value : {}: {}".format(key, config[key]))
            key = self.check_digit_key(key)   
            return config[key]
        else: return default

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
        
        from .palette import palette
        color_map = palette
        ret = {}
        
        for idx, label in enumerate(labels):
            idx = str(idx+1)
            ret[label]=color_map[idx]
        
            # update label
            # self.prev_track_obj[label]=list()
            # self.cnt_pts_cur_frame[label]=list()
            # self.cnt_pts_prev_frame[label]=list()
            # self.track_obj[label]=dict()
            # self.track_idx[label]=0

        return ret

    def get_random_color( self, format='bgr'):
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        return [r, g, b] if format=='rgb' else [b, g, r]

    def get_xxyy(self, detection, frame=None):
        
        if frame==None:
            h, w = self.frame_size[0], self.frame_size[1]
        else:
            h, w = frame.shape[:2]

        x1, y1 = max(int(detection['xmin']), 0), max(int(detection['ymin']), 0)
        x2, y2 = min(int(detection['xmax']), w), min(int(detection['ymax']), h)

        return ( x1, x2, y1, y2 )

    def set_area(self, frame=None):
        pass

    def reset(self):
        logging.warning('Reload Application')
        self.__init__(self.config)

    def __call__(self, frame, info, draw=True):
        pass

def get_obj_app(app_name):
    """
    Return Target Application
    """
    try:

        if DEFAULT_KEY == app_name:
            from .obj.default import Default as trg
            
        elif TRACK_KEY == app_name:
            from .obj.tracking import Tracking as trg

        elif DIRECTION_KEY in app_name:
            from .obj.moving_direction import MovingDirection as trg
            
        elif COUNTING_KEY == app_name:
            from .obj.counting import Counting as trg
        
        elif AREA_KEY in app_name:
            from .obj.area_detection import AeraDetection as trg
        
        elif HEAT_KEY in app_name:
            from .obj.heatmap import Heatmap as trg

        else:
            return None

        return trg

    except Exception as e:
        logging.error(handle_exception(e))
        raise Exception(e)
    
def get_cls_app(app_name):

    try:
        if DEFAULT_KEY == app_name:
            from .cls.default import Default as trg

        return trg

    except Exception as e:
        logging.error(handle_exception(e))
        raise Exception(e)

def get_seg_app(app_name):

    try:
        if DEFAULT_KEY == app_name:
            from .seg.default import Default as trg
            return trg
        else:
            msg = 'unexpected application name'
            logging.error(msg)
            raise Exception(msg)

    except Exception as e:
        logging.error(handle_exception(e))
        raise Exception(e)

def get_pose_app(app_name):
    try:
        if DEFAULT_KEY == app_name:
            from .pose.default import Default as trg
            return trg
        else:
            msg = 'unexpected application name'
            logging.error(msg)
            raise Exception(msg)

    except Exception as e:
        logging.error(handle_exception(e))
        raise Exception(e)

def get_application(config:dict):
    """
    Get Available Application
    """
    if not APP_KEY in config:
        raise Exception("Could not find the {}".format(APP_KEY))
    
    app_name    = config[APP_KEY][APP_KEY_NAME]
    app_tag     = config[TAG]

    trg = None

    if app_tag=='cls': trg=get_cls_app(app_name)
    elif app_tag=='obj': trg=get_obj_app(app_name)
    elif app_tag=='seg': trg=get_seg_app(app_name)
    elif app_tag=='pose': trg=get_pose_app(app_name)
    else: raise Exception('Unexpected TAG: {}'.format(app_tag))
    
    return trg(config)

def get_logic(config:dict):
    
    app_conf    = config[APP_KEY]
    logic_op    = None
    def_alarm   = "WARNING"
    def_alarm_time = 3

    if APP_LOGIC in app_conf and APP_LOGIC_THRES in app_conf:
        logic_op = LogicOperator(  
            app_conf[APP_LOGIC],
            app_conf[APP_LOGIC_THRES] )
    else:
        logging.error("App Setting Error, Make Sure Have {}, {}, Use Default Counting".format(APP_LOGIC, APP_LOGIC_THRES))

    app_alarm = app_conf[APP_ALARM] if APP_ALARM in app_conf else def_alarm
    app_alarm_time = app_conf[APP_ALARM_TIME] if APP_ALARM_TIME in app_conf else def_alarm_time

    return logic_op, app_alarm, app_alarm_time

def get_framework():
    try:
        import vart
        return "vitis-ai"
    except Exception as e:
        pass
    try:
        import openvino
        return "openvino"
    except Exception as e:
        pass
    try:
        import tensorrt
        return "tensorrt"
    except Exception as e:
        pass
    
def get_distance(pt, pt2):
    pt = ( float(pt[0]), float(pt[1]) )
    pt2 = ( float(pt2[0]), float(pt2[1]) )
    return math.hypot( pt2[0]-pt[0], pt2[1]-pt[1])

def get_coord_distance(p1 , p2):
    coordinate_distance = math.sqrt( ((int(p1[0])-int(p2[0]))**2)+((int(p1[1])-int(p2[1]))**2) )
    return coordinate_distance

def get_angle_for_cv(pos1, pos2):
    """
    Calculate Vector's Angle for OpenCV Pixel

    (0, 0) . . (X, 0)
    .
    .
    (Y, 0) . . (X, Y)

    Because the pixel position is reversed, Angle will be reversed, too
    """

    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    theta = int(math.atan2(dy, dx)*180/math.pi) 
    return theta*(-1)

def get_depend_label(config:dict, trg_key="depend_on") -> list:

    ret_depends    = None
    app_config     = config[APP_KEY]

    if trg_key in app_config:
        ret_depends = app_config[trg_key]
    else:
        ret_depends = get_labels(config)
                
    return ret_depends
            
def get_labels(config:dict) -> list:
    """ get the label file and capture all category in it """

    content = []

    # Avoid Level Error
    label_path_key = "label_path"
    try:
        if label_path_key in config:
            label_path = config[label_path_key]  
        else:
            framework = get_framework()
            label_path = config[framework][label_path_key]
    except Exception as e:
        msg = handle_exception(e, title="Config Level Error")
        logging.error(msg)
        raise Exception(msg)

    # Open Label File to Get Content
    with open(label_path, 'r') as f:
        for line in f.readlines():
            content.append(line.strip('\n'))

    return content

def get_time(need_fmt=True, fmt=None):
    cur_time = datetime.now()
    if need_fmt:
        trg_fmt     = fmt if fmt!=None else TIME_FORMAT
        cur_time    = format_time(cur_time, trg_fmt)

    return cur_time

def format_time(in_time, fmt=None):
    fmt = TIME_FORMAT if fmt==None else fmt
    return in_time.strftime(fmt)

def parse_delta_time(delta_time):
    return {    "day"   : delta_time.days,
                "hour"  : delta_time.seconds//3600,
                "minute": delta_time.seconds//60%60,
                "second": delta_time.seconds%60     }


