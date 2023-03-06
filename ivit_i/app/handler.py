
import logging, os, sys
from werkzeug.utils import secure_filename

# ivitApp
from .common import ivitApp, SUP_APP_TYPE, get_application

# ivitAppHandler
import pkgutil, importlib
from ivit_i.utils.err_handler import handle_exception


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
    
    from ivit_i.app import APP_LIST
    # for key, val in APP_LIST.items():
    #     APP_LIST[key].append("default")
        
    return APP_LIST

def search_all_custom_app(app_path, inherit_obj=None):
    """
    Searching all application in custom folder
    ---
    - args
        - app_path: the path to application ( folder )
        - ingerit_obj: if using difference base module, you could modify this argument, default is ivitApp
    """
    if not os.path.exists(app_path):
        raise FileNotFoundError('Could not find custom application folders ({})'.format(app_path))

    custom_apps = {}
    for finder, name, _ in pkgutil.iter_modules([app_path]):
        try:
            importlib.import_module('{}.{}'.format(app_path, name))
        except Exception as e:
            print('Can not import {} ({})'.format(name, handle_exception(e)))
    
    if inherit_obj is None:
        inherit_obj = ivitApp

    for subm in ivitApp.__subclasses__():
        custom_apps.update({
           subm.__name__: subm
        })

    return custom_apps

class ivitAppHandler(object):
    """
    ivitAppHandler
    
    Handle each ivitApp
    """
    def __init__(self, support_type=SUP_APP_TYPE) -> None:

        # Total Application with name (key) and object (value)
        self.apps = {}
        self.sort_apps = {}

        self.app_folder = None
        self.inherit_obj = ivitApp

        # Apps dict with app type
        self.support_type = support_type

    def add_sort_app(self, app_key, app_obj):
        app_type = app_obj().get_type()
        assert app_type in self.support_type, "Excepted type is {}, but got {}".format(self.support_type, app_type)
        
        if not app_type in self.sort_apps:
            self.sort_apps.update( { app_type: [] } )

        if app_key in self.sort_apps.get(app_type):   
            return

        self.sort_apps[app_type].append( app_key )

    def register(self, app_key, app_obj:ivitApp):
        """
        Register each custom application
        ---
        - args
            - app_key: the key of the application which is the keyword when user want to get the application.
            - app_obj: the module of the application, we will double check is the subclasss of the ivitApp or not.
        """
        try:
            # Update applications
            self.apps.update( { app_key: app_obj } )
            
            # Update sort of the application
            self.add_sort_app(app_key, app_obj)
            
            logging.info('Updated Application ({}) into ivitAppHandler !'.format(app_key))
            return True
        except Exception as e:
            logging.error(handle_exception(e))
            return False

    def register_from_folder(self, app_folder, inherit_obj=ivitApp):
        """
        Searching all application in custom folder
        ---
        - args
            - app_folder: the path to application ( folder )
            - inherit_obj: if using difference base module, you could modify this argument, default is ivitApp
        """

        # Safe Path
        self.app_folder = secure_filename(app_folder)
        self.inhereit_obj = inherit_obj
                
        # Double Check
        if not os.path.exists(self.app_folder):
            raise FileNotFoundError('Could not find custom application folders ({})'.format(self.app_folder))
        
        # Log
        logging.info('Searching Application ( {} ) from folder ({})'.format(self.inherit_obj.__name__, self.app_folder))

        # Import All Module
        for finder, name, _ in pkgutil.iter_modules([self.app_folder]):
            try:
                importlib.import_module('{}.{}'.format(self.app_folder, name))
            except Exception as e:
                logging.warning('Can not import {} when register application ... ({})'.format(name, handle_exception(e)))
        
        # Update variable
        for idx, sub_module in enumerate(self.inherit_obj.__subclasses__()):
            app_key, app_obj = sub_module.__name__, sub_module

            # Update applications
            self.apps.update( { app_key: app_obj } )
            
            # Update sort of the application
            self.add_sort_app(app_key, app_obj)
        
        logging.info('Get applications from folder: {}'.format( 
            ', '.join( 
                [ f'{tag}:{len(apps)}' for tag, apps in self.sort_apps.items() ] 
        )))
        logging.info('Applications: {}'.format(self.sort_apps))

        return self.apps

    def get_app(self, app_key):
        assert app_key in self.apps, "Excepted name is [ {} ] , but got {}".format(list(self.apps.keys()), app_key)
        return self.apps.get(app_key)

    def get_sup_type(self):
        """ Get the support type of the ivitAppHandler """
        return self.support_type

    def get_type_app(self, app_type):
        return self.sort_apps.get(app_type, [])
    
    def get_all_apps(self):
        return self.apps
    
    def get_sort_apps(self):
        return self.sort_apps