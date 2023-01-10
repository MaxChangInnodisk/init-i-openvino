import numpy as np
import logging, cv2, os
import itertools as it
from ivit_i.utils.err_handler import handle_exception

from ivit_i.app.common import ( 
    App, 
    get_time, 
    Timer, 
    DETS, 
    LABEL,
    CV_WIN,
    DET_COLOR,
    WARN_COLOR,
    AREA_COLOR,
    APP_KEY_NAME,
    APP_KEY_DEPEND
)

from ivit_i.utils.draw_tools import ( 
    draw_text,
    draw_rect,
    draw_poly,
    in_poly )

ALPHA               = 0.85
BORDER              = 2
FULL_SCREEN         = True

APP_KEY_TRIGGER     = "trigger_type"
APP_KEY_AREA        = "area_points"

APP_KEY_STAY_TIME   = "stay_time"
APP_KEY_STAY_THRES  = "stay_frame_thres"

APP_KEY_SAVE_IMG    = "save_image"
APP_KEY_SAVE_FOLDER = "save_folder"

APP_KEY_ALARM       = "alarm"
APP_KEY_T_ALARM     = "alarm_time"

APP_KEY_SENS        = "sensitivity"
SENS_MED            = "medium"
SENS_HIGH           = "high"
SENS_LOW            = "low"

class AeraDetection(App):

    def __init__(self, config: dict) -> None:
        
        # Basic
        super().__init__(config)
        # Check Param
        self.get_params()

        self.at_least_one_in_area = False
        self.alpha      = ALPHA

        self.warn_color = WARN_COLOR
        self.area_color = AREA_COLOR
        self.det_color = DET_COLOR
        self.bbox_color = self.det_color

        self.temp_frame = None
        self.temp_draw = None
        self.temp_pnts = []

        self.which_area = -1
        self.app_info = ""
        self.detect_nums = dict()

        self.area_cnt = {}
        self.area_has_obj = []

        # Get Configuration Parameters
        (self.area_pts_idx, self.area_pts)       = self.init_area()
        
        self.save_img       = self.get_param_value(self.app_config, APP_KEY_SAVE_IMG, False)
        self.save_folder    = self.get_param_value(self.app_config, APP_KEY_SAVE_FOLDER, "./data")
    
        self.alarm          = self.get_param_value(self.app_config, APP_KEY_ALARM)
        self.alarm_time     = self.get_param_value(self.app_config, APP_KEY_T_ALARM)
    
        self.stay_time      = int(self.get_param_value(self.app_config, APP_KEY_STAY_TIME, 0))
        self.stay_thres     = float(self.get_param_value(self.app_config, APP_KEY_STAY_THRES, 0.9))
        
        self.sensitivity    = self.get_param_value(self.app_config, APP_KEY_SENS, "medium")

        # Judgment
        self.stay_frame = 0         # stay frame
        self.timer_frame = 0        
        self.stay_score = 0

        # Define Time
        self.timer = Timer()
        self.timer.set_thres(self.stay_time)
        self.timer_is_started = False

        self.app_info_pattern = "Total: "
        self.app_info   = ""
        self.app_time   = get_time( False )

    def get_params(self):
        ret = {
            APP_KEY_NAME    : self.def_param("string", "counting", "define application name"),
            APP_KEY_DEPEND  : self.def_param("list", "[ \"car\" ]", "launch application on target label"),
            APP_KEY_AREA    : self.def_param("list", "[ [20, 30], [30, 40], [50, 60] ]", "define the area"),
            APP_KEY_TRIGGER : self.def_param("str", "bottom-center", "define the trigger type of object, options like [ 'bottom-center' , 'center' , 'average-5', 'top-3' ] "),
            APP_KEY_STAY_TIME  : self.def_param("int", "3", "the staying time to detect"),
            APP_KEY_STAY_THRES  : self.def_param("float", "0.9", "the threshold of the staying object to determine the object is actually enter the area."),
            APP_KEY_SAVE_IMG: self.def_param("bool", "true", "bool option for save image"),
            APP_KEY_SAVE_FOLDER: self.def_param("str", "./data", "define the saved image folder"),
            APP_KEY_ALARM   : self.def_param("string", "Three Car Here", "define alarm content"),
            APP_KEY_T_ALARM: self.def_param("int", 3, "display alarm time")
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    

        return ret

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

        # Initialize CV Windows
        self.init_cv_win()

        # Prepare Image to Draw
        logging.info("Detected frame, open the cv windows to collect area coordinate")

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

    def define_trigger(self, xxyy):
        """
        argument:
            - low       : centor
            - medium    : average-4 (exclude border)
            - high      : average-9 (include border) 
        """

        # define function
        def get_steps(start, end, step, on_box=True):
            if on_box: 
                whole_steps = list(np.linspace( start, end, step ))
                return whole_steps
            else: 
                # Exclude the corner point
                whole_steps = list(np.linspace( start, end, step+2 ))
                return whole_steps[1:-1]

        # define parameters
        ret_trigger = None
        trigger_num = None
        on_bbox     = True
        (x1, x2, y1, y2) = xxyy
        
        # define trigger
        sens = self.sensitivity.lower()
        if(sens==SENS_LOW):
            return [ ((x1+x2)//2, (y1+y2)//2) ]
            # trigger_num, on_bbox = 1, False
        elif(sens==SENS_MED):
            trigger_num, on_bbox = 2, False
        elif(sens==SENS_HIGH):
            trigger_num, on_bbox = 3, True
        
        # Start to calculate Trigger
        x_list, y_list = get_steps( x1, x2, trigger_num, on_bbox ), get_steps( y1, y2, trigger_num, on_bbox )
        ret_trigger = [ [ int(x), int(y) ] for x in x_list for y in y_list ]

        return ret_trigger

    def check_obj_in_area(self, triggers):
        for pnt_idx in it.count(0):
            if pnt_idx >= len(triggers): break

            for idx, pts in self.area_pts.items():
                if in_poly(pts, triggers[pnt_idx]): 
                    return idx
        return -1

    def area_event(self, label):

        # Setup Start Time
        if not self.timer_is_started:
            self.timer.set_time()
            self.timer_is_started = True
            # logging.info("Timer is setup ... {}".format(self.timer.t_prev))

        # Change Bounding Box Color
        self.bbox_color = self.warn_color
        
        # Update Label Number
        if not (label in self.detect_nums): 
            self.detect_nums[label] = 0
        self.detect_nums[label] += 1

    def get_output_text( self, nums_label=" ", label=" "):
        return "Detected {:>3} {}".format(nums_label, label) 

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

    def draw_area(self, frame):
        
        # if not self.double_check_pnt(): return frame

        overlay = frame.copy()

        # Draw Point
        list_pnts = list()
        
        # Parse All Area
        for area_idx, area_pts in self.area_pts.items():

            list_pnts = list()
            # Collect data && Draw circle
            for pts in area_pts:
                list_pnts.append(list(pts))       
                cv2.circle(overlay, tuple(pts), 3, AREA_COLOR, -1)

            # File poly and make it transparant
            cv2.fillPoly(overlay, pts=[ np.array(area_pts, np.int32) ], color=AREA_COLOR)

            if len(self.area_cnt) < len(self.area_pts):
                x_max, y_max = np.max(list_pnts, axis=0)
                x_min, y_min = np.min(list_pnts, axis=0)
                self.area_cnt[area_idx] = ( (x_max+x_min)//2, (y_max+y_min)//2 )
        
            # draw_text(frame, str(area_idx), self.area_cnt[area_idx], (0, 0, 0), self.trg_scale, self.trg_thick, background=True, background_color=(0, 0, 255))
        
        frame = cv2.addWeighted( frame, ALPHA, overlay, 1-ALPHA, 0 )

        return frame

    def __call__(self, frame, info, draw=True):

        # Init
        self.init_draw_param( frame )
        self.double_check_pnt()
        self.detect_nums = dict()

        frame = self.draw_area(frame)

        self.at_least_one_in_area = False

        # Get all detected object and check if in area
        self.area_has_obj = []
        for det_idx in it.count(0):
            if det_idx >= len(info[DETS]): break

            self.bbox_color = self.det_color

            # Get Label
            detection = info[DETS][det_idx]
            label = detection[LABEL]
            if not (label in self.depend_labels): continue

            # Set up trigger points
            cur_in_area = False

            # Get correct position
            (x1, x2, y1, y2) = self.get_xxyy( detection )
                        
            # Generate trigger
            triggers = self.define_trigger( xxyy=(x1,x2,y1,y2) )

            # Check current object is in area
            # if self.double_check_pnt():
            cur_in_area = self.check_obj_in_area(triggers)
            if cur_in_area != (-1): 
                self.which_area = cur_in_area
                self.at_least_one_in_area = True
                self.area_event( label )
                self.area_has_obj.append( cur_in_area )

            if not draw: continue

            # Draw Trigger
            # [ cv2.circle(frame, tuple(trg), 3, self.bbox_color, -1) for trg in triggers ]
            # Draw Bounding Box
            # frame = draw_rect(
            #     frame, (x1, y1), (x2, y2), self.bbox_color, BORDER
            # )

        for area_idx, area_cnt in self.area_cnt.items():
            
            draw_text(  frame, 
                        str(area_idx), 
                        area_cnt, 
                        (0, 0, 0), 
                        self.trg_scale, 
                        self.trg_thick, 
                        background=True, 
                        background_color=WARN_COLOR if area_idx in self.area_has_obj else DET_COLOR )

        # Concate Detected Label
        if self.timer_is_started:

            self.timer_frame += 1
            if self.at_least_one_in_area: 
                self.stay_frame += 1
            
            if self.timer.check_time(log=True):

                self.stay_score = self.stay_frame/self.timer_frame
                
                if self.stay_score >= self.stay_thres:
                    
                    detect_content = ""
                    for key, val in self.detect_nums.items():
                        div = "" if detect_content == "" else ", "
                        detect_content += "{}{} {}".format(div, val, key)
                    
                    self.app_info = "Detected {} in area".format(detect_content)
                
                    if ( self.save_img ):
                        
                        cur_time = get_time(fmt='%Y%m%d_%H:%M')
                        img_name = "{}.jpg".format(cur_time)
                        img_path = os.path.join(self.save_folder, img_name)
                        if not os.path.exists(self.save_folder):
                            os.makedirs(img_path)

                        cv2.imwrite( img_path, frame )

                self.timer_is_started = False
                self.timer_frame, self.stay_frame = 0, 0

        else:
            detect_content = ""
            for key, val in self.detect_nums.items():
                        div = "" if detect_content == "" else ", "
                        detect_content += "{}{} {}".format(div, val, key)

            self.app_info = "Detected {} in area ({})".format(detect_content, self.which_area)

        # Draw Application Information
        if draw:

            frame = draw_text(
                    frame       = frame, 
                    text        = self.app_info, 
                    left_top    = ( self.padding, self.padding ),
                    color       = (255, 255, 255),
                    size        = self.trg_scale,
                    thick       = self.trg_thick,
                    outline     = True,
                    background  = True,
                    background_color = (0, 0, 255)
            )


        return frame, self.app_info
