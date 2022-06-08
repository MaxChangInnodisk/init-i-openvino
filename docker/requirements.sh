#!/bin/bash
source utils.sh

# Initial
printd "Initialize ... " Cy
apt-get update -qqy
apt-get install -qy figlet boxes tree > /dev/null 2>&1

ROOT=`pwd`
echo "Workspace is ${ROOT}" | boxes -p a1

printd "Install OpenCV " Cy
apt-get install -qqy libxrender1 libsm6 libxext6 #> /dev/null 2>&1

printd "Install other msicellaneous packages " Cy
apt-get -qy install bsdmainutils zip
pip3 install --disable-pip-version-check tqdm cython gdown setuptools packaging pycocotools GPUtil wget colorlog

# For web api
pip3 install flask flask-socketio flask-cors flasgger gunicorn==20.1.0 eventlet==0.30.2
apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase
printd -e "Done${REST}"
