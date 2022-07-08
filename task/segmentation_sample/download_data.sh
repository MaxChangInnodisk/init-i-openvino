#!/bin/bash

TRG_FOLDER="/workspace/data"
FILE_NAME="retail_sample.png"

URL="https://innodisk365-my.sharepoint.com/:i:/g/personal/max_chang_innodisk_com/EaEd9CjMf71DklXbD0RoSScBbJTZqftZLa-i325l89Y2Yg?e=Fnnzdr"
KEY="&download=1"
URL="${URL}${KEY}"

FILE_PATH="${TRG_FOLDER}/${FILE_NAME}"

if [[ ! -d "${TRG_FOLDER}" ]];then
	echo "Not found ${TRG_FOLDER}"
	mkdir ${TRG_FOLDER}
fi

wget "${URL}" -O ${FILE_PATH}