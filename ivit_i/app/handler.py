
import logging, os
from .common import get_application

def get_app_list():
    """
    Legacy Func
    """
    dir_path = os.path.dirname(__file__)    
    logging.warning(dir_path)
    ret = []
    for path in os.listdir(dir_path):
        
        full_path = os.path.join(dir_path, path)

        if os.path.isdir(full_path) and path!="__pycache__":

            for app in os.listdir(full_path):

                app_path = os.path.join(full_path, app)
                check_file = os.path.isfile(app_path)
                check_ext = os.path.splitext(app)[1]!=".pyc"
                check_name = app != "__init__.py"

                if check_file and check_ext and check_name:
                    ret.append(os.path.splitext(app)[0])
    ret.append("default")
    return ret

def get_tag_app_list():
    dir_path = os.path.dirname(__file__)    
    logging.warning(dir_path)
    ret = {}

    from ivit_i.app import APP_LIST
    for key, val in APP_LIST.items():
        APP_LIST[key].append("default")
        
    ret = APP_LIST

    return ret
