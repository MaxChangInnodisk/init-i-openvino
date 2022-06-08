#!/bin/bash

function download(){
	ID=$1
	NAME=$2

	if [[ -f $NAME ]];then
		echo "$(date +"%F %T") $NAME is exists !"
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

# Model: https://drive.google.com/file/d/1zbRkdUWLGLiQbnoWG6pb_3VRd60Ej4Cz/view?usp=sharing
NAME="model.zip"
GID="1zbRkdUWLGLiQbnoWG6pb_3VRd60Ej4Cz"
download $GID ${NAME}
unzip $NAME && rm "${NAME}"
