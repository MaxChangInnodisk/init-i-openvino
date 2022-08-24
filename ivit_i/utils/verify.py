#!/usr/bin/python3
import os, sys, logging, errno
import subprocess as sb

PID         = "196d"
VID         = "0201"

def innousb():

    p = sb.run( f"lsusb | grep {PID}:{VID}", 
                shell   = True,
                stdout  = sb.DEVNULL, 
                stderr  = sb.STDOUT)

    if not p.returncode:
        msg = f"Verifying Innodisk Device ... Success!!!"
        logging.info("-"*len(msg))
        logging.info(msg)
        logging.info("-"*len(msg))
    else:
        msg = f"Verifying Innodisk Device ... Failed!!!"
        # "Failed !!! Could not find innodisk device."
        logging.error("*"*len(msg))
        logging.error(msg)
        logging.error("*"*len(msg))
        sys.exit(errno.EINTR)

if __name__ == '__main__':
    from logger import config_logger
    config_logger('./verify-device.log', 'w', "info")
    innousb()

