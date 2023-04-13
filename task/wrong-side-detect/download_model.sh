#!/bin/bash

function download(){

	if [[ ! -z $(ls model 2>/dev/null )  ]];then
		echo "$(date +"%F %T") the model folder has already exist !"
	else
		gdown --id $1 -O $2
	fi
}

# ------------------------------------------------------------------------------

echo "$(date +"%F %T") Download model from google drive ..."
ROOT=$(dirname `realpath ${0}`)
echo $ROOT
cd $ROOT

TRG_FOLDER="/workspace/model"
if [[ ! -d ${TRG_FOLDER} ]];then
	mkdir ${TRG_FOLDER}
fi

if [[ ! (${TRG_FOLDER} == *"${ROOT}"*) ]];then
	echo "$(date +"%F %T") Move terminal to $(realpath ${TRG_FOLDER})"
	cd ${TRG_FOLDER}
fi

# ------------------------------------------------------------------------------

# Model: https://drive.google.com/file/d/1VZy_7pgLISdHTH1hh7CZ2zuFlSAbkKGH/view?usp=share_link
NAME="yolo-v4-tiny-tf"
ZIP="${NAME}.zip"
if [[ -d ${NAME} ]];then
	echo "$(date +"%F %T") Model already exist"
	exit 1
fi

GID="1VZy_7pgLISdHTH1hh7CZ2zuFlSAbkKGH"
download $GID ${ZIP}
unzip $ZIP -d ${NAME} && rm "${ZIP}"
