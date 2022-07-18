#!/bin/bash

function download(){
	ID=$1
	NAME=$2

	if [[ ! -z $(ls model 2>/dev/null )  ]];then
		echo "$(date +"%F %T") the model folder has already exist !"
	else
		gdown --id $ID -O $NAME
	fi
}

# ------------------------------------------------------------------------------

echo "$(date +"%F %T") Download model from google drive ..."
ROOT=$(dirname `realpath ${0}`)
echo $ROOT
cd $ROOT

TRG_FOLDER="./"

if [[ ! (${TRG_FOLDER} == *"${ROOT}"*) ]];then
	echo "$(date +"%F %T") Move terminal to $(realpath ${TRG_FOLDER})"
	cd ${TRG_FOLDER}
fi

# ------------------------------------------------------------------------------

# Model: https://drive.google.com/file/d/1HgMRV9VLv0tdhXE1vH6_5YjS-ZLiFvf7/view?usp=sharing
NAME="model.zip"
GID="1HgMRV9VLv0tdhXE1vH6_5YjS-ZLiFvf7"
download $GID ${NAME}
unzip $NAME && rm "${NAME}"
