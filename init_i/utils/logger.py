from asyncore import write

import logging

# ===============================================================================================

LOG_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR
    }

def config_logger(log_name=None, write_mode='a', level='Debug'):

    # ---------------------------------------------------
    logger = logging.getLogger() # get logger
    logger.setLevel(LOG_LEVEL[level]) # set level
    # ---------------------------------------------------
    if not logger.hasHandlers(): # if the logger is not setup
        formatter = logging.Formatter( "%(asctime)s [%(levelname)-.4s] in %(module)s: %(message)s", "%y-%m-%d %H:%M:%S")
    # ---------------------------------------------------
    # add stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOG_LEVEL[level.lower()])
        logger.addHandler(stream_handler)
    # ---------------------------------------------------
    # add file handler
        if log_name:
            file_handler = logging.FileHandler(log_name, write_mode, 'utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(LOG_LEVEL['info'])
            logger.addHandler(file_handler)
    # ---------------------------------------------------
    logger.info('Create logger.({})'.format(logger.name))
    logger.info('Enabled stream {}'.format(f'and file mode.({log_name})' if log_name else 'mode'))

    return logger
