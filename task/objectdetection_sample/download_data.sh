#!/bin/bash

TRG_FOLDER="/workspace/data"
FILE_NAME="street.mp4"

URL="https://innodisk365-my.sharepoint.com/:v:/g/personal/max_chang_innodisk_com/EWWLtmDrwQBEkpBLBD_9AJIBU3Krg6qIIa8-lk-SHdxHwQ?e=EZAQ7B"
KEY="&download=1"
URL="${URL}${KEY}"

FILE_PATH="${TRG_FOLDER}/${FILE_NAME}"

if [[ ! -d "${TRG_FOLDER}" ]];then
	echo "Not found ${TRG_FOLDER}"
	mkdir ${TRG_FOLDER}
fi

wget "${URL}" -O ${FILE_PATH}