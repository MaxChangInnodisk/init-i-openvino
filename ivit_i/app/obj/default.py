import cv2, logging
import itertools as it

from ivit_i.app.common import App, DETS



class Default(App):

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.init_result_params()
        self.init_draw_params()
        self.update_palette(
            config['application'].get('custom_palette') 
        )

        logging.info("Get Defualt Application")

    def get_params(self) -> dict:
        """ Define Counting Parameter Format """
        
        # Define Dictionary
        ret = {
            "name": self.def_param("string", "tracking", "define application name"),
            "depend_on": self.def_param("list", "[ \"car\" ]", "launch application on target label")
        }
        
        # Console Log
        logging.info("Get The Basic Parameters of Application")
        for key, val in ret.items():
            logging.info("\t- {}".format(key))
            [ logging.info("\t\t- {}: {}".format(_key, _val)) for _key, _val in val.items() ]    
        return ret

    # --------------------------------------------------------------
    # Start of General Function

    @staticmethod
    def depend_label(label:str, interest_labels:list):
        """ Custom function for filter uninterest label """
        if interest_labels == []:
            return True
        # Not setup interest labels
        return (label in interest_labels)

    def init_result_params(self):
        """ Initialize Parameters """
        self.results = {}
        self.log = []
        self.alarm = ""
    
    def init_draw_params(self):
        """ Initialize Draw Parameters """
        self.frame_idx = 0
        self.frame_size = None
        self.font_size  = None
        self.font_thick = None
        self.thick      = None

    def update_draw_params(self, frame):
        """ Update the parameters of the drawing tool, which only happend at first time. """
        
        # if frame_size not None means it was already init 
        if( self.frame_idx > 1): return None

        # Parameters
        FRAME_SCALE     = 0.0005    # Custom Value which Related with Resolution
        BASE_THICK      = 1         # Setup Basic Thick Value
        BASE_FONT_SIZE  = 0.5   # Setup Basic Font Size Value
        FONT_SCALE      = 0.2   # Custom Value which Related with the size of the font.

        # Get Frame Size
        self.frame_size = frame.shape[:2]
        
        # Calculate the common scale
        scale = FRAME_SCALE * sum(self.frame_size)
        
        # Get dynamic thick and dynamic size 
        self.thick  = BASE_THICK + round( scale )
        self.font_thick = self.thick//2
        self.font_size = BASE_FONT_SIZE + ( scale*FONT_SCALE )
        
        logging.info('Frame: {} ({}), Get Border Thick: {}, Font Scale: {}, Font Thick: {}'
            .format(self.frame_size, scale, self.thick, self.font_size, self.font_thick))

    def draw_bg_text(self, frame, label, color:tuple, left_top:tuple, ):
        """ Draw the text with background """

        xmin, ymin = left_top

        # Draw Background
        (t_wid, t_hei), t_base = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, self.font_size, self.font_thick)
        t_xmin, t_ymin, t_xmax, t_ymax = xmin, ymin-(t_hei+(t_base*2)), xmin+t_wid, ymin
        cv2.rectangle(frame, (t_xmin, t_ymin), (t_xmax, t_ymax), color , -1)

        # Draw Text
        cv2.putText(
            frame, label, (xmin, ymin-(t_base)), cv2.FONT_HERSHEY_SIMPLEX,
            self.font_size, (255,255,255), self.font_thick, cv2.LINE_AA
        )

        return frame

    def update_obj_num(self, obj_nums, label):
        """ update the number of each object """
        if obj_nums.get(label) is None:
            obj_nums.update({label:0})
        obj_nums[label]+=1
        return obj_nums

    # End of General Function
    # --------------------------------------------------------------

    # Lable Color Function Start 
    # --------------------------------------------------------------
    def update_palette(self, new_palette:dict):
        """ update palette via `custom_palette` in configuration file """

        # Checking
        if new_palette=={} or new_palette is None:
            return

        # Update label color
        for label, color in new_palette.items():
            if self.palette.get(label) is None:
                logging.warning('Get unexpected label: {}'.format(label))
                continue
            self.palette.update({label:color})
    
        logging.info('Updated color palette')

    def __call__(self, frame, data, draw=True):
        
        self.frame_idx += 1
        self.update_draw_params( frame )

        # Capture all center point in current frame and draw the bounding box
        obj_nums = {}

        for det in (data['detections']):

            # Check Label is what we want
            if not self.depend_label(det['label'], self.depend_labels):
                continue
            
            # Parsing output
            ( label, score, xmin, ymin, xmax, ymax ) \
                 = [ det[key] for key in [ 'label', 'score', 'xmin', 'ymin', 'xmax', 'ymax' ] ]                  
        
            # Draw Top N label
            if not draw: continue

            # Draw bounding box
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), self.palette.get(label) , self.thick)
    
            # Further Process
            frame = self.draw_bg_text(
                frame = frame,
                label = '{} {:.1%}'.format(label, score),
                color = self.palette.get(label),
                left_top = (xmin, ymin)
            )

            # Update current object numbers
            obj_nums = self.update_obj_num(obj_nums, label)

        # Update result
        self.log = ', '.join([ f'{_num:03} {_label}' for _label, _num in obj_nums.items()])
        self.results.update({
            'log': self.log,
            'alarm': self.alarm
        })

        return frame, self.results
        