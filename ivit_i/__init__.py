from ivit_i.utils import verify
from ivit_i.utils.logger import config_logger

config_logger('./ivit-i.log', 'w', "info")
verify.innousb()