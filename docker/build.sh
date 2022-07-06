#!/bin/bash

# Store the utilities
ROOT=$(dirname `realpath $0`)
source "${ROOT}/utils.sh"

# Install pre-requirement
if [[ -z $(which jq) ]];then
    printd "Installing requirements .... " Cy
    sudo apt-get install jq -yqq
fi

# Checking environment configuration is existed.
CONF="init-i.json"
FLAG=$(ls ${CONF} 2>/dev/null)
if [[ -z $FLAG ]];then
    CONF="${RUN_PWD}/${CONF}"
    FLAG=$(ls ${CONF} 2>/dev/null)
    if [[ -z $FLAG ]];then
        printd "Couldn't find configuration (${CONF})" Cy
        exit
    fi
else
    printd "Detected configuration (${CONF})" Cy
fi

# Parse information from configuration
BASE_NAME=$(cat ${CONF} | jq -r '.PROJECT')
TAG_VER=$(cat ${CONF} | jq -r '.VERSION')
TAG_PLATFORM=$(cat ${CONF} | jq -r '.PLATFORM')

# Concate name
IMAGE_NAME="${BASE_NAME}/${TAG_PLATFORM}:${TAG_VER}"
printd "Concatenate docker image name: ${IMAGE_NAME}" Cy

# Build the docker image
cd $ROOT
printd "Build the docker image. (${IMAGE_NAME})" Cy
docker build -t ${IMAGE_NAME} .