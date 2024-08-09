#!/bin/bash
# Copyright (c) 2023 Innodisk Corporation
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# ========================================================
# Store the utilities
FILE=$(realpath "$0")
ROOT=$(dirname "${FILE}")
source "${ROOT}/utils.sh"

# ========================================================
# Basic Parameters
CONF="ivit-i.json"
DOCKER_USER="innodiskorg"
DOCKER_COMPOSE="./docker/docker-compose.yml"

# ========================================================
# Check configuration is exit
check_config ${CONF}

# ========================================================
# Parse information from configuration
check_jq
PROJECT=$(cat ${CONF} | jq -r '.PROJECT')
VERSION=$(cat ${CONF} | jq -r '.VERSION')
PLATFORM=$(cat ${CONF} | jq -r '.PLATFORM')
TAG=$(cat "${CONF}" | jq -r '.TAG')

# ========================================================
# Get Option

INTERATIVE=true
QUICK=false

# Help
function help(){
	echo "Run the iVIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-bqh]"
	echo "options:"
	echo "b		Run in background"
	echo "q		Qucik launch iVIT-I"
	echo "h		help."
}

# Get information from argument
while getopts "bqh:" option; do
	case $option in
		b )
			INTERATIVE=false ;;
		q )
			QUICK=true ;;
		h )
			help; exit ;;
		\? )
			help; exit ;;
		* )
			help; exit ;;
	esac
done

# ========================================================
# Initialize Docker Command Variables

# [NAME]
DOCKER_IMAGE="${DOCKER_USER}/${PROJECT}-${PLATFORM}:${VERSION}-${TAG}"
DOCKER_NAME="${PROJECT}-${PLATFORM}-${VERSION}-${TAG}"

# [BASIC]
WS="/workspace"
SET_NAME="--name ${DOCKER_NAME}"
MOUNT_WS="-w ${WS} -v $(pwd):${WS}"
SET_TIME="-v /etc/localtime:/etc/localtime:ro"
SET_NETS="--net=host"

# [DEFINE COMMAND]
RUN_CMD="bash"

# [PLACEHOLDER]
SET_CONTAINER_MODE="-it"
SET_VISION=""
SET_PRIVILEG="--privileged"
MOUNT_CAM="-v /dev:/dev"
SET_MEM="--ipc=host"

# ========================================================

# [ACCELERATOR]
MOUNT_ACCELERATOR="--user=root --device=/dev/dri --device=/dev/accel --group-add=$(stat -c '%g' /dev/dri/render* | head -n 1) --group-add=$(stat -c '%g' /dev/dri/card* | head -n 1)"


# [VISION] Set up Vision option for docker if need
if [[ ! -z $(echo ${DISPLAY}) ]];then
	SET_VISION="-v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix${DISPLAY}"
	xhost + > /dev/null 2>&1
	printd " * Detected monitor"
else
	printd " * Can not detect monitor"
fi

# [Basckground] Update background option
if [[ ${INTERATIVE} = true ]]; then 
	printd " * Run Interative Terminal Mode"
else
	SET_CONTAINER_MODE="-dt"; 
	printd " * Run Background Mode"
fi

# ========================================================
# Conbine docker command line
DOCKER_CMD="docker run \
--rm \
${SET_CONTAINER_MODE} \
${SET_NAME} \
${SET_PRIVILEG} \
${MOUNT_ACCELERATOR} \
${MOUNT_CAM} \
${SET_NETS} \
${SET_MEM} \
${SET_TIME} \
${MOUNT_WS} \
${SET_VISION} \
${DOCKER_IMAGE} ${RUN_CMD}"

# ========================================================
# Logout and wait
echo -ne "\n${DOCKER_CMD}\n\n"
if [[ ${QUICK} = false ]];then waitTime 5; fi

# ========================================================
# Execution

# Rund Docker Compose
printd "Launch Relative Container" G
docker compose --file ${DOCKER_COMPOSE} -p ${TAG} up -d 

# Run docker command 
printd "Launch iVIT-I Container" G
docker rm -f ${DOCKER_NAME} &> /dev/null

bash -c "${DOCKER_CMD}"

if [[ ${INTERATIVE} = true ]];then
	printd "Close Relative Container" R
	docker compose -f ${DOCKER_COMPOSE} -p ${TAG} down
fi

exit 0;