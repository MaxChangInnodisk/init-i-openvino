
import sys, os
sys.path.append( os.getcwd() )
from ivit_i.common.app import iAPP_HANDLER

if __name__ == "__main__":

    print_title = lambda title: print(f'\n# {title}')

    # Init ivitAppHandler
    app_handler = iAPP_HANDLER()

    # Register 
    app_handler.register_from_folder('samples/register_app_folder_sample')

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
    app = app_handler.get_app("CustomObjApp")()
    print( 'Current Application Name is {}'.format(app.__class__.__name__))
    print( 'Current Application Type is {}'.format(app.get_type()))
    print( 'Execute Application: {}'.format(app()) )