#!/bin/bash
source format_print.sh

# Initial
printd "$(date +"%T") Initialize ... " Cy
apt-get update -qqy

ROOT=`pwd`
echo "Workspace is ${ROOT}" | boxes -p a1

# OpenCV
printd "$(date +"%T") Install OpenCV " Cy
apt-get install -qqy ffmpeg libsm6 libxext6 #> /dev/null 2>&1

# Flask
pip3 install flask

printd -e "Done${REST}"
