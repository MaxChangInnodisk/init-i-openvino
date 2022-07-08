#!/bin/bash

TRG_FOLDER="/workspace/data"

URL="https://innodisk365-my.sharepoint.com/:i:/g/personal/max_chang_innodisk_com/EcRmWXHSyftOllhXUGIkMYsBy-Lm5XurT6tB-l29rDhN2g?e=T368sP&download=1"

FILE_NAME="${TRG_FOLDER}/cat.jpg"

if [[ ! -d "${TRG_FOLDER}" ]];then
	echo "Not found ${TRG_FOLDER}"
	mkdir ${TRG_FOLDER}
fi

wget "${URL}" -O ${FILE_NAME}