import cv2, logging, time
import itertools as it
import numpy as np
from ivit_i.utils.err_handler import handle_exception

from ivit_i.app.common import (
    App, 
    get_logic,
    DETS,
    LABEL,
    CV_WIN,
    APP_LOGIC,
    AREA_COLOR,
    APP_KEY_DEPEND,
    APP_KEY_NAME,
    APP_LOGIC_THRES,
    APP_ALARM,
    APP_ALARM_TIME
)
from ivit_i.utils.draw_tools import ( 
    draw_text,
    draw_rect,
    draw_poly,
    in_poly )

ALPHA               = 0.8
BORDER              = 2
FULL_SCREEN         = True

APP_RET_NUM     = "num"
APP_RET_ALARM   = "alarm"
APP_KEY_AREA    = "area_points"

class Counting(App):
    
    def __init__(self, config:list) -> None:
        super().__init__(config)
        
        self.get_params()
        self.detect_nums    = dict()
        self.detect_labels  = list()
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

        self.t_alarm    = time.time()

        # Get Logic
        self.logic, self.alarm, self.app_alarm_time = get_logic(config)
        # Get Configuration Parameters
        (self.area_pts_idx, self.area_pts)       = self.init_area()

    def get_params(self) -> dict:
        """
        Define Counting Parameter Format
        """
        
        # Define Dictionary
        ret = {
            APP_KEY_NAME    : self.def_param("string", "counting", "define application name"),
            APP_KEY_DEPEND  : self.def_param("list", "[ \"car\" ]", "launch application on target label"),
            APP_LOGIC       : self.def_param("string", "=", "use logic to define situation"),
            APP_LOGIC_THRES : self.def_param("int", 3, "define logic threshold"),
            APP_ALARM       : self.def_param("string", "Three Car Here", "define alarm content"),
            APP_ALARM_TIME  : self.def_param("int", 3, "alarm display time")
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    
        return ret

    def get_output_text( self, nums_label=" ", label=" "):
        return "Detected {:>3} {}".format(nums_label, label) 

    # For Area
    def init_area(self):

        # Get Content
        _area_points = self.get_param_value(self.app_config, APP_KEY_AREA, dict())

        # Convert String Key to Int
        area_points = { int(key):[ [ int(float(v[0])), int(float(v[1])) ] for v in val ] for key, val in _area_points.items() }

        # Update Relatived Parameters
        area_points_key = list(area_points.keys())


        if [] in [ area_points_key ]:
            return (0, dict())

        area_points_key.sort()
        idx_area_points = area_points_key[-1]

        logging.info("Detected {} area points".format( len(area_points_key)))
        logging.info("Area Index: {}".format(idx_area_points))
        logging.info(area_points)
        return (idx_area_points, area_points)

    def draw_area(self, frame):
        
        # if not self.double_check_pnt(): return frame

        overlay = frame.copy()

        # Draw Point
        list_pnts = list()
        
        # Parse All Area
        for area_idx, area_pts in self.area_pts.items():

            # Collect data && Draw circle
            for pts in area_pts:
                list_pnts.append(list(pts))       
                cv2.circle(overlay, tuple(pts), 3, AREA_COLOR, -1)

            # File poly and make it transparant
            cv2.fillPoly(overlay, pts=[ np.array(area_pts, np.int32) ], color=AREA_COLOR)

            x_max, y_max = np.max(list_pnts, axis=0)
            x_min, y_min = np.min(list_pnts, axis=0)
            self.poly_cx = (x_max+x_min)//2
            self.poly_cy = (y_max+y_min)//2

        frame = cv2.addWeighted( frame, ALPHA, overlay, 1-ALPHA, 0 )

        return frame

    def draw_poly_inarea(self, frame):
        if len(self.area_pts)==0: return frame
        
        background = frame.copy()
        for idx, pnts in self.area_pts.items():
            if pnts==[]: continue
            for pnt in pnts:
                cv2.circle(frame, tuple(pnt), 3, AREA_COLOR, -1)

            # Fill poly and make it transparant
            background = draw_poly(background, pnts, AREA_COLOR)
        frame = cv2.addWeighted( frame, ALPHA, background, 1-ALPHA, 0 )
        return frame

    def add_area_handler( self, event, x, y, flags, param):
        
        # if click down
        if event == cv2.EVENT_LBUTTONDOWN:
            # Init
            org_img     = param['img']
            
            # Add Index in area_points
            
            self.area_pts[self.area_pts_idx].append( [ x, y ] )

            # Draw poly point
            org_img = self.draw_poly_inarea(org_img)

            cv2.imshow(CV_WIN, org_img)

    def set_area(self, frame=None):
        
        if frame.all()==None:
            if self.area_pts != {}: return True
            msg = "Could not capture polygon coordinate and there is not provide frame to draw"
            raise Exception(msg)

        if self.area_pts != {}:
            logging.info("Detected area point is already exist")
            
        # Prepare Image to Draw
        logging.info("Detected frame, open the cv windows to collect area coordinate")
        
        # Initialize CV Windows
        self.init_cv_win()

        # Setup Mouse Event and Display
        try:

            while(True):
                
                # Draw Old One
                temp_frame = frame.copy()
                temp_frame = self.draw_poly_inarea( temp_frame )
                
                # Init: Update Index
                self.area_pts_idx += 1     
                self.area_pts[self.area_pts_idx] = list()

                cv2.setMouseCallback(CV_WIN, self.add_area_handler, {"img": temp_frame})
                cv2.putText(temp_frame, "Click to define detected area, press any key to leave", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.imshow(CV_WIN, temp_frame)
                key = cv2.waitKey(0)

                if key == ord('q'): break
                
        except Exception as e:
            logging.error(handle_exception(e))

        finally:
            cv2.setMouseCallback(CV_WIN, lambda *args : None)
            cv2.destroyAllWindows()

        
        logging.info("Set up area point: {}".format(self.area_pts))

    def double_check_pnt(self, need_break = False):
        ret = True

        # Log
        # [ print('{}({})'.format(key, type(key)), val) for key ,val in self.area_pts.items() ]

        area_pts = self.area_pts.copy()
        for idx, pts in area_pts.items():
            if ( pts == None ) or ( len(pts) == 0 ):
                self.area_pts.pop(idx)

            if ret and need_break:
                msg = "Could not capture polygon coordinate and there is not provide frame to draw"
                logging.warning(msg)
                raise Exception(msg)    

        return ret

    def check_obj_in_area(self, triggers:list):

        if self.area_pts == {} or self.area_pts==None: 
            logging.warning("Not set area yet ...")
            return 0

        for pnt_idx in it.count(0):
            if pnt_idx >= len(triggers): break

            for idx, pts in self.area_pts.items():
                if in_poly(pts, triggers[pnt_idx]): 
                    return idx
        return -1

    # For counting detect number
    def init_detect_param(self):
        self.text_pos           = [ self.padding, self.padding ]
        self.detect_nums        = dict()
        self.detect_labels      = list()

    def update_detect_label(self, label):
        if not ( label in self.detect_labels ):
            self.detect_labels.append(label)

    def update_detect_label_nums(self, label):
        if not ( label in self.detect_nums ):
            self.detect_nums[label] = 0
        self.detect_nums[label] += 1

    # Logic Event
    def logic_event(self, value):

        if self.text_draw=="":

            # If logic judgment failed then return
            if not (self.logic(value)): return None

            self.text_draw = "{}".format(self.alarm)
            self.text_color = ( 255, 255, 255 )
            self.t_alarm = time.time()
            logging.warning(self.text_draw)

        else:
            t_cur = time.time()
            if (t_cur - self.t_alarm)>=self.app_alarm_time:
                self.text_draw  = ""
                self.t_alarm    = t_cur
    
    def get_app_info(self, frame, draw=True):
        
        self.detect_labels.sort()

        app_info = list()

        # Start Iteration for draw application information
        for idx in it.count(0):
            
            # If greater than detected label numbers then break
            if idx >= len(self.detect_labels): break

            # Get label
            label = self.detect_labels[idx]
            
            # Logic Operator Event
            if self.logic != None:
                self.logic_event( self.detect_nums[label] )
            
            # Not run logical event
            else:
                self.text_draw = self.get_output_text(self.detect_nums[label], label)
                self.text_color = ( 255, 255, 255)
            
            # Define Application Information
            app_info.append({
                LABEL           : label,
                APP_RET_NUM     : self.detect_nums[label],
            })

            if draw:
                frame = draw_text(
                    frame       = frame, 
                    text        = self.text_draw, 
                    left_top    = self.text_pos, 
                    color       = self.text_color, 
                    size        = self.trg_scale, 
                    thick       = self.trg_thick, 
                    outline     = True,
                    background  = True,
                    background_color = ( 0, 0, 255 ) )

            self.text_pos[1] += ( self.padding + self.text_hei + self.text_base )        

        info = {
            'log': app_info,
            'alarm': ""
        }

        return frame, info

    def __call__(self, frame, info, draw=True):

        # Init 
        self.init_draw_param(frame)
        self.init_detect_param()
        self.double_check_pnt()
        
        frame = self.draw_area(frame)

        # Capture all center point in current frame and draw the bounding box
        for idx in it.count(0):
            
            # Check if interation over the length
            if idx >= (len(info[DETS])): break

            # Get Detection Object
            detection   = info[DETS][idx]
            label       = detection['label']

            # if not in depend_label then pass
            if not (label in self.depend_labels): continue

            # Get available position
            (x1, x2, y1, y2) = self.get_xxyy( detection )
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
            
            # check if in area
            cur_in_area = self.check_obj_in_area( [ (cx, cy) ] )
            if cur_in_area == (-1): continue

            # if not in detected_labels, we append it
            self.update_detect_label(label)
            self.update_detect_label_nums(label)

            # Draw the bounding box
            if not draw: continue
            frame = draw_rect(
                frame           = frame, 
                left_top        = ( x1, y1 ), 
                right_bottom    = ( x2, y2 ), 
                color           = self.palette[label]
            )


        return self.get_app_info(frame, draw=draw)