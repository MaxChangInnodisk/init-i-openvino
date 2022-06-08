import cv2, time, logging, os, sys

EXTENSION_MAP={
    'Image': ['jpg', 'png', 'bmp'],
    'Video': ['mp4', 'avi'],
    'V4L2': ['dev', 'video'],
    'RTSP': ['rtsp']
}

def get_source_type(file_name):
    
    if type(file_name)==int or file_name.isdigit():
        return 'V4L2'

    name, ext = os.path.splitext(file_name)
    ext = ext.replace('.', '')

    if ext=="":
        for key in ['V4L2', 'RTSP']:
            for keyword in EXTENSION_MAP[key]:
                if keyword in name:
                    return key
    else:
        for key in ['Image', 'Video']:
            if ext in EXTENSION_MAP[key]:
                return key

class Img:
    def __init__(self, input_data) -> None:
        self.img = cv2.imread(input_data)

    def release(self):
        self.img=None

    def __del__(self):
        self.img=None

    def read(self):
        # if not None then return true
        return (self.img is not None), self.img

class Source():
    
    def __init__(self, input_data, input_type=None):

        self.src = None
        self.input_data = input_data.rstrip().replace('\n', '').replace(' ', '')
        self.input_type = input_type if input_type!=None else get_source_type(input_data)
        self.status, self.err = self.check_status()
        # --------------------------------------------
        logging.warning('Detect source type is : {}'.format(self.input_type))
        if self.status:
            if input_type in ['V4L2', 'Video']:
                self.src = cv2.VideoCapture(self.input_data)
            elif input_type=='Image':
                self.src = Img(self.input_data)            
            elif input_type=='RTSP':
                self.src = cv2.VideoCapture(self.input_data)
            else:
                logging.error('Unexcepted input data.')
        # --------------------------------------------
        self.isStop = False
        
    def __del__(self):
        self.stop()

    def check_status(self):
        status, err_msg = True, ""
        if self.input_type in ['Video', 'Image', 'V4L2']:
            # check file exist
            if not os.path.exists(self.input_data):
                status = False
                err_msg = "Could not find data ({})".format(self.input_data)
        
        return status, err_msg

    def get_status(self):            
        return self.status, self.err

    def get_type(self):
        return self.input_type

    def stop(self):
        self.isStop = True
    
    def release(self):
        try:
            self.isStop = True
            self.src.release()
        except:
            logging.warning('Could not release object')
        finally:
            logging.warning('Set source to `None`')
            self.src=None
    
    def get_frame(self):
        return self.src.read()

if __name__ == "__main__":
    logging.info('Testing source.py')

    # rtsp -> rtsp://admin:admin@172.16.21.1:554/snl/live/1/1/n
    input_data = "rtsp://admin:admin@172.16.21.1:554/snl/live/1/1/n"
    src = Source(input_data, "rtsp")
    
    while(True):
        ret, frame = src.get_frame()
        cv2.imshow('Test', frame)
        if cv2.waitKey(1)==ord('q'):
            break
    
    src.release()