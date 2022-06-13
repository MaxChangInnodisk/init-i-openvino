
APP_KEY = "application"
FRAMEWORK = "openvino"

def get_application(config:dict):
    
    if not APP_KEY in config:
        raise Exception("Could not find the {}".format(APP_KEY))
    
    app_config = config[APP_KEY]
    app_name = app_config['name']
    
    if not 'depend_on' in app_config:
        # capture all label list
        depend_label = get_labels(config)
    else:
        depend_label = app_config['depend_on'] if type(app_config['depend_on'])==list else [ app_config['depend_on'] ]

    if 'counting' in app_name:
        from .counting import Counting as trg
    elif 'direction' in app_name:
        from .moving_direction import MovingDirection as trg
    
    return trg(depend_label)
            
def get_labels(config:dict) -> list:
    """ get the label file and capture all category in it """
    content = []
    with open(config[FRAMEWORK]["label_path"], 'r') as f:
        for line in f.readlines():
            content.append(line.strip('\n'))
    return content