from .utils import verify
from .utils.logger import config_logger

config_logger('./ivit-i.log', 'w', "info")
verify.innousb()