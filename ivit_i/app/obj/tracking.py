import cv2, logging, os, time
import itertools as it
import numpy as np
from ivit_i.utils.err_handler import handle_exception

from ivit_i.app.common import (
    App, 
    DETS,
    LABEL,
    CV_WIN,
    AREA_COLOR,
    APP_KEY_DEPEND,
    APP_KEY_NAME,
    get_time,
    format_time, 
    parse_delta_time, 
    get_distance, 
)

from ivit_i.utils.draw_tools import ( 
    get_text_size,
    draw_text,
    draw_rect,
    draw_poly,
    in_poly )

ALPHA           = 0.85
BORDER          = 2
FULL_SCREEN     = True

APP_RET_NUM     = "num"
APP_RET_ALARM   = "alarm"
APP_KEY_AREA    = "area_points"

class Tracking(App):
    
    def __init__(self, config:list) -> None:
        super().__init__(config)
        
        self.get_params()

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

        self.app_info_pattern = "Total: "
        self.app_info   = ""
        self.app_time   = get_time( False )

        self.frame_idx = 0
        self.limit_distance = 50

        self.cur_pts    = {}
        self.pre_pts    = {}
        self.cur_bbox   = {}

        self.track_obj      = {}
        self.track_idx      = {}
        self.track_obj_bbox = {}
        
        
        self.total_num  = dict()
        self.alarm      = ""

        (self.area_pts_idx, self.area_pts)       = self.init_area()

    def get_params(self) -> dict:
        """
        Define Counting Parameter Format
        """
        
        # Define Dictionary
        ret = {
            APP_KEY_NAME    : self.def_param("string", "tracking", "define application name"),
            APP_KEY_DEPEND  : self.def_param("list", "[ \"car\" ]", "launch application on target label")
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    
        return ret

    def init_track_param(self, label):
        self.cur_pts[label]=list()
        self.pre_pts[label]=list()
        self.track_obj[label]=dict()
        self.track_idx[label]=0

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

    def clear_current_point(self):
        [ self.cur_pts[key].clear() for key in self.cur_pts ]

    def check_distance(self, distance):
        return (distance <= self.limit_distance)

    def save_pts_at_first(self):

        if self.frame_idx > 1: return None

        for detected_idx in it.count(0):
            if detected_idx >= len(self.detected_labels): break
            label = self.detected_labels[detected_idx]

            for cur_pt_idx in it.count(0):
                if cur_pt_idx >= len(self.cur_pts[label]): break
                cur_pt = self.cur_pts[label][cur_pt_idx]

                for prev_pt_idx in it.count(0):
                    if prev_pt_idx >= len(self.pre_pts[label]): break
                    prev_pt = self.pre_pts[label][prev_pt_idx]
                
                    # calculate the distance, if smaller then limit_distance, then it might the same one
                    if self.check_distance(get_distance(cur_pt, prev_pt)):
                        self.track_obj[label][ self.track_idx[label] ] = cur_pt
                        self.track_idx[label] +=1

    def update_point_and_draw(self, info, frame):

        for idx in it.count(0):
            
            # Check if interation over the length
            if idx >= (len(info[DETS])): break

            # Get Detection Object
            detection   = info[DETS][idx]
            label       = detection[LABEL]
            
            if not (label in self.depend_labels): continue
            
            # if not in detected_labels, we append it
            if not ( label in self.detected_labels ):
                self.detected_labels.append(label)
                self.init_track_param( label )

            (x1, x2, y1, y2) = self.get_xxyy( detection )
            cx, cy = (x1 + x2)//2, (y1 + y2)//2
            
            # check if in area
            cur_in_area = self.check_obj_in_area( [ (cx, cy) ] )
            if cur_in_area == (-1): continue

            # saving the center point
            self.cur_pts[label].append( (cx, cy) )
            
            # draw the bbox, label text
            # frame = draw_rect(
            #     frame = frame, 
            #     left_top = ( x1, y1 ), 
            #     right_bottom = ( x2, y2 ), 
            #     color = self.palette[label]
            # )

    def track_prev_object(self):

        for label_idx in it.count(0):

            if label_idx >= len(self.detected_labels): break

            label = self.detected_labels[label_idx]

            __track_obj  = self.track_obj[label].copy()
            __cnt_pts_cur_frame = self.cur_pts[label].copy()
            
            for track_idx, prev_pt in __track_obj.items():
                
                # if object not exist we have to remove the the disappear one
                obj_exist = False

                for cur_pt in __cnt_pts_cur_frame:                
                    
                    # calculate the distance, if the some one 
                    # we have to update the center point
                    if self.check_distance( get_distance(cur_pt, prev_pt) ):

                        self.track_obj[label][track_idx] = cur_pt
                        
                        if cur_pt in self.cur_pts[label]:
                            self.cur_pts[label].remove(cur_pt)

                        obj_exist = True

                if not obj_exist:
                    self.track_obj[label].pop(track_idx)

    def track_new_object_and_draw(self, frame, draw=True):

        self.alarm = self.app_info_pattern

        overlay = frame.copy()
        for label_idx in it.count(0):
            
            if label_idx >= len(self.detected_labels): break

            label = self.detected_labels[label_idx]

            # update track object: the remain object in cnt_pts_cur_frame is the new object
            for pt in self.cur_pts[label]:
                self.track_obj[label][ self.track_idx[label] ] = pt
                self.track_idx[label] +=1
            
            # draw the track number on object
            if draw:
                
                for idx, pt in self.track_obj[label].items():

                    ( wid, hei ), base = get_text_size( str(idx), self.trg_scale, self.trg_thick)
                    (x, y) = (pt[0]-(wid)//2, pt[1]-(hei+base)//2)
                    
                    
                    overlay = draw_text(
                        frame       = overlay, 
                        text        = str(idx), 
                        left_top    = ( x, y ), 
                        color       = (0, 0, 0), 
                        size        = self.trg_scale,  
                        thick       = self.trg_thick, 
                        outline     = True,
                        background  = True,
                        background_color    = self.palette[label]
                    )

            cur_total_num = list(self.track_obj[label].keys())
            
            # update key
            if not label in self.total_num: 
                self.total_num.update( { label: 1 } )

            # update total number
            self.total_num[label] = cur_total_num[-1] if cur_total_num != [] else self.total_num[label]
                
            self.alarm += "{} {}, ".format(
                self.total_num[label]+1, label )

            # update the preview information
            self.pre_pts[label] = self.cur_pts[label].copy()

        frame = cv2.addWeighted( frame, 0.5, overlay, 1-0.5, 0 )    
        # frame = overlay
        return frame

    def get_app_info(self, frame, draw=True):

        # Get Current Time
        self.app_cur_time = get_time( False )
        self.live_time = parse_delta_time((self.app_cur_time-self.app_time))
        
        # Live Time for Display
        ret_live_time = "{}:{}:{}:{}".format(
            self.live_time["day"], 
            self.live_time["hour"], 
            self.live_time["minute"], 
            self.live_time["second"] )

        # Combine the result
        self.app_info = {
            "start"     : format_time(self.app_time),
            "current"   : format_time(self.app_cur_time),
            "duration"  : ret_live_time,
            "alarm"     : self.alarm
        }

        draw_text(
            frame       = frame, 
            text        = "Live Time: {} {}".format(ret_live_time, self.alarm), 
            left_top    = ( self.padding, self.padding ), 
            color       = ( 255, 255, 255), 
            size        = self.trg_scale, 
            thick       = self.trg_thick, 
            outline     = True,
            background  = True,
            background_color = ( 0, 0, 255)
        )


    def __call__(self, frame, info):
        """
        1. Get all the bounding box and calculate the center point.
        2. Saving the center point and copy a preview one in the last. ("self.cur_pts", "self.pre_pts").
        3. Calculate the distance between current and preview center point. ( via math.hypot ).
        4. If the distance smaller than the limit_distance than we updating it in "track_obj" and remove from the "self.cur_pts".
        5. The remaining items in "self.cur_pts" is the new one, add to "track_obj".
        6. Draw the information in it.
        """
        
        # Init
        self.frame_idx += 1
        self.clear_current_point()
        self.double_check_pnt()
        self.init_draw_param( frame )
        frame = self.draw_area(frame)

        # Capture all center point in current frame and draw the bounding box
        self.update_point_and_draw( info, frame )

        # if the first frame web have to saving all object here
        self.save_pts_at_first()

        # if not first frame: start to calculate distance to check the object is the same one
        self.track_prev_object()

        # adding the remaining point to track_obj
        frame = self.track_new_object_and_draw( frame, draw=True )

        # get tracking information which will be stored in `self.app_info`
        self.get_app_info( frame, draw=True )

        # return frame
        return frame, self.app_info