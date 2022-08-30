#!/usr/bin/python3
import os, sys, logging, errno, time
import subprocess as sb

PID         = "196d"
VID         = "0201"
WID         = 80

class ColorMap:
    def __init__(self):
        self.HEADER      = '\033[95m'
        self.OKBLUE      = '\033[94m'
        self.OKCYAN      = '\033[96m'
        self.OKGREEN     = '\033[92m'
        self.WARNING     = '\033[93m'
        self.FAIL        = '\033[91m'
        self.ENDC        = '\033[0m'
        self.BOLD        = '\033[1m'
        self.BRED        = '\033[7;31m'
        self.UNDERLINE   = '\033[4m'

class CustomLogger(ColorMap):
    
    def __init__(self):
        super().__init__()
        self.DEBUG      = '[DEBU]'
        self.INFO       = '{}[INFO]{}'.format(self.OKGREEN, self.ENDC)
        self.WARNING    = '{}[WARN]{}'.format(self.WARNING, self.ENDC)
        self.ERROR      = '{}[ERRO]{}'.format(self.FAIL, self.ENDC)
        self.CRITICAL   = '{}[CRIT]{}'.format(self.BRED, self.ENDC)
    
    def format_time(self):
        res = time.localtime()
        return "{}-{}-{} {:02}:{:02}:{:02}".format(
            str(res.tm_year)[-2:],
            res.tm_mon,
            res.tm_mday,
            res.tm_hour,
            res.tm_min,
            res.tm_sec
        )

    def args_to_str(self, args):
        return ''.join( [ arg+' ' for arg in args ] )

    def logger(self, mode, args):
        print("{} {} {}".format(
            self.format_time(), mode , self.args_to_str(args)))

    def debug(self, *args):
        self.logger( self.DEBUG, args )
    
    def info(self, *args):
        self.logger( self.INFO, args )
    
    def warning(self, *args):
        self.logger( self.WARNING, args )
    
    def error(self, *args):
        self.logger( self.ERROR, args )
        
    def critical(self, *args):
        self.logger( self.CRITICAL, args )

def has_logger():
    logger = logging.getLogger()
    return False if not logger.hasHandlers() else True
      
def get_logger():
    
    logger = CustomLogger()
    
    if has_logger():
        from .logger import config_logger
        logger = config_logger('./verify-device.log', 'w', "debug")
        
    return logger

def innousb():

    logger = get_logger()

    p = sb.run( f"lsusb | grep {PID}:{VID}", 
                shell   = True,
                stdout  = sb.DEVNULL, 
                stderr  = sb.STDOUT)

    if not p.returncode:
        msg = f"SUCCESS: Found Innodisk Device !!! "
        
        print()
        sb.run( f"echo '\n{msg}\n' | boxes -s {WID}x5 -a c", shell = True)
        print()
    else:
        msg = f"FAILED: Could not Innodisk Device ... "
        print()
        sb.run( f"echo '\n{msg}\n' | boxes -s {WID}x5 -a c", shell = True)
        print()
        sys.exit(errno.EINTR)

if __name__ == '__main__':
    innousb()