
import sys, os
sys.path.append( os.getcwd() )
from ivit_i.common.app import iAPP_CLS, iAPP_OBJ, iAPP_SEG, iAPP_HANDLER

class CustomClsApp(iAPP_CLS):
    
    def __init__(self):
        """ Do nothing """
        pass
     
    def __call__(self):
        """ Do nothing """
        return 'This is custom classification application'
    
class CustomObjApp(iAPP_OBJ):
    
    def __init__(self):
        """ Do nothing """
        pass
     
    def __call__(self):
        """ Do nothing """
        return None

class CustomSegApp(iAPP_SEG):
    
    def __init__(self):
        """ Do nothing """
        pass
     
    def __call__(self):
        """ Do nothing """
        return None

if __name__ == "__main__":
    
    print_title = lambda title: print(f'\n# {title}')
    
    # Init ivitAppHandler    
    app_handler = iAPP_HANDLER()
    print_title('iAPP_HANDLER Support {}'.format(app_handler.get_sup_type()))

    # Register Application
    print_title('Register application')
    app_handler.register(CustomClsApp.__name__, CustomClsApp)
    app_handler.register(CustomObjApp.__name__, CustomObjApp)
    app_handler.register(CustomSegApp.__name__, CustomSegApp)

    # Get Test app from app_handler and initailize
    app = app_handler.get_app(CustomClsApp.__name__)()
    
    # Get all application
    print_title( 'Get all application')
    print( app_handler.get_all_apps() )

    # Get all application which sort by type
    print_title( 'Get all application which sort by type')
    print( app_handler.get_sort_apps() )

    # Get all application which implement on classification 
    print_title( 'Get all application which implement on classification')
    print( app_handler.get_type_app('CLS') )

    # Instance app
    print_title( 'Instance app' )
    app = app_handler.get_app(CustomClsApp.__name__)()
    print( 'Current Application Name is {}'.format(app.__class__.__name__))
    print( 'Current Application Type is {}'.format(app.get_type()))
    print( 'Execute Application: {}'.format(app()) )