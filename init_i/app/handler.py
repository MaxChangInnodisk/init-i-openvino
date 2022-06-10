
APP_KEY = "application"

def get_application(config:dict):
    
    if not APP_KEY in config:
        raise Exception("Could not find the {}".format(APP_KEY))
    
    app_config = config[APP_KEY]
    app_name = app_config['name']
    depend_label = app_config['depeed_on'] if type(app_config['depeed_on'])==list else [ app_config['depeed_on'] ]

    if 'counting' in app_name:
        from .counting import Counting as trg
    elif 'direction' in app_name:
        from .moving_direction import MovingDirection as trg
    
    return trg(depend_label)
            