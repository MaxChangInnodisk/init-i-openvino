#!/bin/bash
source utils.sh

# Initial
printd "Initialize ... " Cy
apt-get update -qqy
apt-get install -qy figlet boxes tree > /dev/null 2>&1

printd "System Require " Cy
apt-get -qy install bsdmainutils zip jq wget usbutils

ROOT=`pwd`
echo "Workspace is ${ROOT}" | boxes -p a1

printd "Install OpenCV " Cy
apt-get install -qqy libxrender1 libsm6 libxext6 #> /dev/null 2>&1

printd "Install other msicellaneous packages " Cy
pip3 install --disable-pip-version-check tqdm cython gdown setuptools packaging wget colorlog psutil

# For web api
printd "For Web API " Cy
pip3 install flask flask-socketio==5.1.2 flask-cors flasgger gunicorn==20.1.0 eventlet==0.30.2
pip3 install python-engineio==4.3.2 python-socketio==5.6.0
apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase
printd "Done"
