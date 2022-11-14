
import cv2, logging
from ivit_i.utils.err_handler import handle_exception
import numpy as np
import itertools as it
from ivit_i.app.common import (
    App, 
    get_distance, 
    get_coord_distance, 
    get_angle_for_cv,
    CV_WIN,
    DETS,
    LABEL,
    APP_KEY_NAME,
    APP_KEY_DEPEND,
    APP_ALARM
)

from ivit_i.utils import (     PADDING,
    BASE_FONT_SIZE,
    BASE_FONT_THICK,
    get_text_size,
    get_scale,
    draw_text,
    draw_rect,
    draw_poly,
    in_poly,
    add_weight )

FULL_SCREEN         = True

APP_KEY_TRIGGER     = "trigger_type"
APP_KEY_AREA        = "area_points"
APP_KEY_DIRECTION   = "area_vector"
APP_KEY_BUFFER      = "buffer"
APP_KEY_THRES       = "thres"

PASS_COLOR  = ( 0, 255, 0 )
ERRO_COLOR  = ( 0, 0, 255 )
WARN_COLOR  = ( 0, 255, 255)
AREA_COLOR  = ( 0, 0, 255 )
ALPHA       = 0.9
BORDER      = 2

class MovingDirection(App):

    """
    Setting:
        1. Set Area-N
        2. Set the Direction of Area-N 

    Inference:
        1. Tracking
        2. Detect direction
        3. Check In Which Area and Check the moving direction is correct
        4. Display different color base on step 3
    """

    def __init__(self, config) -> None:
        # Basic Parameters
        super().__init__(config)

        self.get_params()

        self.target_color   = None

        # About Tracking
        self.track_limit    = 30
        
        self.track_idx      = {}
        self.track_obj      = {}
        self.track_obj_bbox = {}

        self.cur_pts        = {}
        self.pre_pts        = {}
        self.cur_bbox       = {}
        
        # Area
        self.area_pts       = dict()
        self.area_pts_idx   = 0

        # Vector
        self.vec_pts        = dict()
        self.vec_pts_idx    = 0
        self.vec_draw_flag  = False
        
        # About Direction Checking and Draw Arrow
        self.track_obj_rec  = dict()
        self.track_obj_vec  = dict()
        self.arrow_length   = 20

        # Judgment via track_obj_thres
        self.track_obj_score        = dict()

        # Get Config Param
        self.track_buf              = int(self.get_param_value(self.app_config, APP_KEY_BUFFER, 15))
        self.track_obj_thres        = float(self.get_param_value(self.app_config, APP_KEY_THRES, 5))
        (self.vec_pts_idx, self.vec_pts) , (self.area_pts_idx, self.area_pts) = self.init_area_vector()

        self.alarm                  = self.get_param_value(self.app_config, APP_ALARM, "Detected Direction Error ") 
        
        self.check_area_vector()

    # Init Function

    def get_params(self) -> dict:
        """
        Define Counting Parameter Format
        """
        
        # Define Dictionary
        ret = {
            APP_KEY_NAME    : self.def_param("string", "counting", "define application name"),
            APP_KEY_DEPEND  : self.def_param("list", "[ \"car\" ]", "launch application on target label"),
            APP_KEY_AREA    : self.def_param("list", "[[506, 229], [646, 254], [636, 709], [202, 718], [360, 415], [433, 319]]", "define the area"),
            APP_KEY_DIRECTION:  self.def_param("list", "[ [429, 699], [540, 256]]", "define the direction vector via two point"),
            APP_KEY_BUFFER  : self.def_param("int", "15", "collect N frame to detect object moving direction, the larger the stable"),
            APP_KEY_THRES   : self.def_param("int", "5", "define threshold ( number of frame ) to ensure the error direction is exist"),
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    
        return ret

    def check_area_vector_exist(self):
        if None in [ self.vec_pts_idx, self.vec_pts, self.area_pts_idx, self.area_pts ]:
            return False
        return True

    def init_area_vector(self):

        # Get Content
        _directions  = self.get_param_value(self.app_config, APP_KEY_DIRECTION, dict())
        _area_points = self.get_param_value(self.app_config, APP_KEY_AREA, dict())

        # Convert String Key to Int
        directions = { int(key):val for key, val in _directions.items() }
        area_points = { int(key):val for key, val in _area_points.items() }    

        # Update Relatived Parameters
        
        directions_key   = list(directions.keys())
        area_points_key = list(area_points.keys())

        if [] in [ area_points_key, directions_key ]:
            return (0, dict()), (0, dict())

        directions_key.sort()
        area_points_key.sort()
        idx_directions = directions_key[-1]
        idx_area_points = area_points_key[-1]
        
        logging.info("Got {} directions , {} area points".format( len(directions_key), len(area_points_key)))
        logging.info("Area Index: {}".format(idx_area_points))
        logging.info("Direction Index: {}".format(idx_directions))
        
        return (idx_directions, directions), (idx_area_points, area_points)

    def check_area_vector(self):

        def show_content(dictionary, title="Object", tab='\t'):
            _tab = '\t'
            print(tab, title)
            for key, val in dictionary.items():
                print("{} [{}] : {}".format(tab+_tab, key, val))
        
        def show_both(title="This is title", tab=""):
            _tab = '\t'
            print(tab, title)
            show_content(self.area_pts, "Area Point", tab+_tab)
            show_content(self.vec_pts, "Area Vector", tab+_tab)

        if not self.check_area_vector_exist(): return None

        show_both("Origin: ")

        # Real Data Length
        diff_list       = []
        arrow_list      = list(self.vec_pts.keys())
        area_point_list = list(self.area_pts.keys())
        
        # Get Diff Value in Two List
        for key in area_point_list:
            if not(key in arrow_list):
                diff_list.append(key)
            else:
                arrow_list.remove(key)
        [ diff_list.append(key) for key in arrow_list ]
        
        # Try to remove
        for key in diff_list:
            try: self.area_pts.pop(key)
            except Exception as e: pass
            try: self.vec_pts.pop(key)
            except Exception as e: pass

        show_both("Get paired data: ")

        # -----------------------------------------
        
        # Clear Pair but Empty Content
        area_point_copy = self.area_pts.copy()
        for key in area_point_copy.keys():
            
            if ( [] in [ self.area_pts[key], self.vec_pts[key] ] ):
                self.area_pts.pop(key)
                self.vec_pts.pop(key)
        
        self.area_pts_idx =  len(self.area_pts)-1
        self.vec_pts_idx      = len(self.vec_pts) -1
        
        show_both("Get available data: ")

    # Helper Function

    def draw_all_area_vector(self, frame, color=(0,0,255), alpha=0.8):
        background = frame.copy()
        
        for key in self.area_pts.keys():
            background = draw_poly( background, self.area_pts[key], color )
            background = cv2.arrowedLine(background, tuple(self.vec_pts[key][0]), tuple(self.vec_pts[key][1]), (0,0,0), 20)

        return add_weight( frame, background, alpha)

    # Setup Area and Direction Function

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

    def draw_vector_inarea(self, frame):
        if len(self.vec_pts)==0: return frame

        for idx, pnts in self.vec_pts.items():
            if pnts==[]: continue
            cv2.arrowedLine(frame, tuple(pnts[0]), tuple(pnts[1]), AREA_COLOR, 2)
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

    def add_vector_handler(self, event, x, y, flags, param):
        
        org_img = param['img'].copy()   
        out = False

        if event == cv2.EVENT_LBUTTONDOWN and not self.vec_draw_flag and not out:
            # add first point if indext not exist
             
            # self.vec_pts[self.vec_pts_idx].append( (x,y) )
            # if self.vec_pts[self.vec_pts_idx]==[]:
            #      [ self.vec_pts[self.vec_pts_idx].append([]) for i in range(2) ]
            # self.vec_pts[self.vec_pts_idx][0] = [x,y]
            if len(self.vec_pts[self.vec_pts_idx])>=2:
                self.vec_pts[self.vec_pts_idx].clear()

            self.vec_pts[self.vec_pts_idx].append( [x,y] )

            self.vec_draw_flag = True
            cv2.circle(org_img, (x, y), 3, (0, 0, 255),5)
            cv2.imshow(CV_WIN, org_img)
            
        elif event == cv2.EVENT_LBUTTONUP and self.vec_draw_flag and not out:
            
            # Add Arrow
            self.vec_pts[self.vec_pts_idx].append( [x,y] ) 
            
            # Draw
            cv2.arrowedLine(org_img, tuple(self.vec_pts[self.vec_pts_idx][0]), tuple(self.vec_pts[self.vec_pts_idx][1]), (0,0,255), 2)
            cv2.imshow(CV_WIN, org_img)

            # Update Information
            # self.vec_pts_idx      += 1
            self.vec_draw_flag   = False
            out = True

        elif event == cv2.EVENT_MOUSEMOVE and self.vec_draw_flag and not out:

            image = org_img.copy()
            cv2.line(image, tuple(self.vec_pts[ self.vec_pts_idx][0]), (x, y), (0,0,0), 1)
            cv2.imshow(CV_WIN, image)

    def set_area(self, frame=None):
        
        if frame.all()==None:

            if self.area_pts != {} and self.vec_pts != {}:
                return True

            msg = "Could not capture polygon coordinate and there is not provide frame to draw"
            raise Exception(msg)


        if self.area_pts != {} and self.vec_pts != {}:
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
                temp_frame = self.draw_vector_inarea( temp_frame )

                # Init: Update Index
                self.area_pts_idx += 1                
                self.vec_pts_idx      += 1
                self.area_pts[self.area_pts_idx] = list()
                self.vec_pts[self.vec_pts_idx] = list()
                
                cv2.setMouseCallback(CV_WIN, self.add_area_handler, {"img": temp_frame})
                cv2.putText(temp_frame, "Click to define detected area, press any key to leave", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.imshow(CV_WIN, temp_frame)
                key = cv2.waitKey(0)

                # For Direction
                temp_frame = frame.copy()
                temp_frame = self.draw_poly_inarea( temp_frame )
                temp_frame = self.draw_vector_inarea( temp_frame )
                cv2.setMouseCallback(CV_WIN, self.add_vector_handler, {"img": temp_frame})
                cv2.putText(temp_frame, "Click to define direction, press q to leave, other to continue", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.imshow(CV_WIN, temp_frame)
                key2 = cv2.waitKey(0) 
                
                if key2 == ord('q'): break
                else: continue

        except Exception as e:
            logging.error(handle_exception(e))

        finally:
            cv2.setMouseCallback(CV_WIN, lambda *args : None)
            cv2.destroyAllWindows()

        self.check_area_vector()

    # Judgment

    def scale_arrow(self, label, idx):
        """
        Calculate N directions average vector to reduce the noise
        """
        # Get All Direction
        self.track_obj_rec[label][idx].append( self.track_obj[label][idx] )

        total_direction = self.track_obj_rec[label][idx]
        len_direction   = len(total_direction)
        first_point     = np.array( total_direction[0] )
        total_vector    = np.array([0, 0])
        num_vector      = 0

        # Detected is the Minimum Direction
        # Collecting Moving Direction Buffer
        if len_direction < self.track_buf: return None, None

        for i in it.count(0):
            if i >= (len_direction): break
            pre_point = np.array(total_direction[i])
            cur_point = np.array(total_direction[i+1] if i!=(len_direction-1) else pre_point)
            cur_vector = (cur_point - pre_point)
            total_vector += cur_vector
            num_vector += 1
        
        # average vector and get average end point
        avg_vector  = np.around(total_vector/num_vector*10).astype(int)
        end_point   = first_point + avg_vector

        (prev_x, prev_y), (cur_x , cur_y ) = first_point, end_point
        
        # Get Arrow Pixel and Re-scale
        distance    = max(get_coord_distance( (prev_x, prev_y), (cur_x, cur_y) ), 0.1)
        scale       = self.arrow_length/distance
        momentum_x, momentum_y = ( cur_x - prev_x), ( cur_y - prev_y)
        bias_x , bias_y = int(scale * momentum_x), int(scale * momentum_y)
        cur_x, prev_x = (cur_x + bias_x), (prev_x - bias_x)
        cur_y, prev_y = (cur_y + bias_y), (prev_y - bias_y)

        # Clear Old directions to keep the information is newest
        if(len_direction > self.track_buf):
            self.track_obj_rec[label][idx].pop(0)

        return (cur_x, cur_y), (prev_x, prev_y)

    def check_in_area(self, cur_pt):
        ret = -1
        for idx, pts in self.area_pts.items():
            if in_poly(pts, cur_pt): 
                ret = idx; break
        return ret

    # Tracking Function

    def clear_tracking_data(self):
        [ self.cur_pts[key].clear() for key in self.cur_pts ]
        [ self.cur_bbox[key].clear() for key in self.cur_bbox ]

    def init_track_parameters(self, label):
        
        if ( label in self.detected_labels ): return None

        # for track object
        self.detected_labels.append(label)
        self.cur_pts[label] = list()
        self.pre_pts[label] = list()
        self.track_obj[label] = dict()
        self.track_idx[label] = 0

        # for direction checking
        self.track_obj_rec[label] = dict()

        # for bounding box
        self.cur_bbox[label] = list()
        self.track_obj_bbox[label] = dict()

        self.track_obj_score[label] = dict()

    def update_point_and_draw(self, info, frame):

        for idx in it.count(0):
            
            # Check if interation over the length
            if idx >= (len(info[DETS])): break

            # Get Detection Object
            detection   = info[DETS][idx]
            label       = detection['label']
            
            if not (label in self.depend_labels): continue
            self.init_track_parameters(label)

            (x1, x2, y1, y2) = self.get_xxyy( detection )
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            
            # saving the center point
            self.cur_pts[label].append( (cx, cy) )
            
            self.cur_bbox[label].append( (x1,x2,y1,y2) )

    def check_distance(self, distance):
        return (distance <= self.track_limit)

    def save_pts_at_first(self):

        if self.frame_idx > 1: return None

        for detected_idx in it.count(0):
            if detected_idx >= len(self.detected_labels): break
            
            label = self.detected_labels[detected_idx]

            for cur_pt_idx in it.count(0):
                if cur_pt_idx >= len(self.cur_pts[label]): break

                cur_pt      = self.cur_pts[label][cur_pt_idx]
                cur_bbox    = self.cur_bbox[label][cur_pt_idx]

                for prev_pt_idx in it.count(0):
                    if prev_pt_idx >= len(self.pre_pts[label]): break

                    prev_pt = self.pre_pts[label][prev_pt_idx]
                
                    # calculate the distance, if smaller then limit_distance, then it might the same one
                    if self.check_distance(get_distance(cur_pt, prev_pt)):
                        
                        self.track_obj[label][ self.track_idx[label] ] = cur_pt

                        self.track_obj_bbox[label][ self.track_idx[label] ] = cur_bbox

                        self.track_idx[label] +=1

    def track_prev_object(self):
        """
        track_obj           : store the preview center point
        cnt_pts_cur_frame   : store the center point of current points
        
        1. If distance is less than self.track_limit means the same object
            a. Update center_point in track_obj
            b. Clear center_point in cnt_pts_cur_frame

        2. If distance not less than limit, means the new object
            a. The remain object means the new one, so clear the new object in track_obj[label] ( not track yet )
        
        """

        # For loop
        for label_idx in it.count(0):
            if label_idx >= len(self.detected_labels): break

            # Get Label
            label = self.detected_labels[label_idx]

            # Start to track preview object
            track_obj_copy         = self.track_obj[label].copy()
            cnt_pts_cur_frame_copy = self.cur_pts[label].copy()
            cnt_bbox_copy           = self.cur_bbox[label].copy()

            for track_idx in track_obj_copy.keys():
                
                # Get preview object
                prev_pt = track_obj_copy[track_idx]

                # if object not exist we have to remove the the disappear one
                obj_exist = False

                for cur_pt_idx in it.count(0):
                    
                    if cur_pt_idx >= len(cnt_pts_cur_frame_copy): break

                    # Get current
                    cur_pt = cnt_pts_cur_frame_copy[ cur_pt_idx ]
                    cur_bbox = cnt_bbox_copy[cur_pt_idx]

                    # Calculate the distance to check if it is the same object
                    if self.check_distance( get_distance(cur_pt, prev_pt) ):
                        
                        # Same object, update center point
                        self.track_obj[label][track_idx] = cur_pt
                        self.track_obj_bbox[label][track_idx] = cur_bbox
                        
                        # Remove center point after update it
                        if cur_pt in self.cur_pts[label]:

                            self.cur_pts[label].remove( cur_pt )
                            self.cur_bbox[label].remove( cur_bbox )

                        obj_exist = True

                # Clean Not Exist Object
                if not obj_exist:
                    self.track_obj[label].pop(track_idx)
                    self.track_obj_bbox[label].pop(track_idx)    
    
    def track_new_and_draw(self, frame, draw=True):

        for label_idx in it.count(0):
            if label_idx >= len(self.detected_labels): break
            
            # Get Label
            label = self.detected_labels[ label_idx ]

            # Remain Object is the new one, update to track_obj
            for cur_pt_idx in it.count(0):
                if cur_pt_idx>=(len(self.cur_pts[label])): break

                cur_pt = self.cur_pts[label][cur_pt_idx]
                self.track_obj[label][ self.track_idx[label] ] = cur_pt
                self.track_obj_bbox[label][ self.track_idx[label] ] = self.cur_bbox[label][cur_pt_idx]
                self.track_idx[label] +=1

            # Not for first frame
            if self.frame_idx < 1: return None

            # The Object is Tracked, Draw the Index on center_point
            for track_idx, cur_pt in self.track_obj[label].items():
                
                # Update direction to calculate average vector
                if not (track_idx in self.track_obj_rec[label]): self.track_obj_rec[label][track_idx] = list()
                if not (track_idx in self.track_obj_score[label]): self.track_obj_score[label][track_idx] = 0
                

                # Setup Shared Color
                self.target_color = PASS_COLOR

                # Calculate Arrow Aera
                self.track_obj_vec[track_idx] = self.scale_arrow(label, track_idx)
                got_direction = not (None in self.track_obj_vec[track_idx])
                if got_direction :

                    # In which error direction
                    in_trg_area = self.check_in_area(cur_pt)
                    if in_trg_area != (-1):
                        
                        moving_theta = get_angle_for_cv( 
                            self.track_obj_vec[track_idx][0], self.track_obj_vec[track_idx][1] )
                        
                        arrow_theta = get_angle_for_cv( 
                            self.vec_pts[in_trg_area][0], self.vec_pts[in_trg_area][1] )
                        
                        # Error Direction
                        if abs( moving_theta - arrow_theta ) <= 90:
                            if self.track_obj_score[label][track_idx]<= self.track_obj_thres:
                                self.track_obj_score[label][track_idx] += 1
                        # Correct Direction
                        else:
                            self.track_obj_score[label][track_idx] = 0

                # Draw bbound and index on current center
                if not draw: continue

                if self.track_obj_score[label][track_idx] >= self.track_obj_thres:
                    # logging.warning("Really Erro Direction")
                    self.target_color = ERRO_COLOR
                    
                    frame = draw_text(
                            frame       = frame, 
                            text        = self.alarm, 
                            left_top    = ( self.padding, self.padding ),
                            color       = (255, 255, 255),
                            size        = self.trg_scale,
                            thick       = self.trg_thick,
                            outline     = True,
                            background  = True,
                            background_color = (0, 0, 255) )

                    # if got_direction:

                    #     arrow_size = max( int(self.trg_scale), 1 )
                    #     cv2.arrowedLine(
                    #         frame, self.track_obj_vec[track_idx][1], self.track_obj_vec[track_idx][0], 
                    #         self.target_color, arrow_size , tipLength=arrow_size/2)


                (x1,x2,y1,y2) = self.track_obj_bbox[label][track_idx]
                draw_rect( frame, (x1,y1), (x2, y2), self.target_color, self.trg_scale )
                    
            # update the preview information    
            self.pre_pts[label] = self.cur_pts[label].copy()

    # Main

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
        self.init_draw_param( frame )
        self.clear_tracking_data()

        frame = self.draw_all_area_vector( frame )
        
        # capture all center point in current frame and draw the bounding box
        self.update_point_and_draw( info, frame)

        # if the first frame web have to saving all object here
        self.save_pts_at_first()

        # if not the firt frame, we update the center point and separate the new one
        self.track_prev_object( )

        # adding the remaining point to track_obj
        self.track_new_and_draw( frame )

        return frame, None
