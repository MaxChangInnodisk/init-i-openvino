#!/bin/bash
CONF="ivit-i.json"
USER="maxchanginnodisk"
GITHUB_USER="MaxChangInnodisk"
GITHUB_TOKEN="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"

# Store the utilities
FILE=$(realpath "$0")
ROOT=$(dirname "${FILE}")
source "${ROOT}/utils.sh"

# Install pre-requirement
check_jq

# Install pyinstaller for inno-verify
check_pyinstaller

# Checking environment configuration is existed.
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
IMAGE_NAME="${USER}/${BASE_NAME}-${TAG_PLATFORM}:${TAG_VER}"
printd "Concatenate docker image name: ${IMAGE_NAME}" Cy


# Build the docker image
printd "Build the docker image. (${IMAGE_NAME})" Cy

docker build -t "${IMAGE_NAME}" \
--build-arg "VER=${TAG_VER//v/r}" \
--build-arg "GITHUB_USER=${GITHUB_USER}" \
--build-arg "GITHUB_TOKEN=${GITHUB_TOKEN}" \
-f "${ROOT}/DockerfileRelease" . 