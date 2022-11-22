#!/bin/bash

# Basic Parameters
CONF="ivit-i.json"
DOCKER_USER="maxchanginnodisk"

# Store the utilities
FILE=$(realpath "$0")
ROOT=$(dirname "${FILE}")
source "${ROOT}/utils.sh"

# Set the default value of the getopts variable 
GPU="all"
BG=false
RUN_WEB=true
RUN_CLI=false
MAGIC=true
SERVER=false
INIT=true
MODE="SERVER"

# Install pre-requirement
check_jq

# Check configuration is exit
FLAG=$(ls ${CONF} 2>/dev/null)
if [[ -z $FLAG ]];then printd "Couldn't find configuration (${CONF})" Cy; exit
else printd "Detected configuration (${CONF})" Cy; fi

# Parse information from configuration
PROJECT=$(cat ${CONF} | jq -r '.PROJECT')
VERSION=$(cat ${CONF} | jq -r '.VERSION')
PLATFORM=$(cat ${CONF} | jq -r '.PLATFORM')
PORT=$(cat ${CONF} | jq -r '.PORT')

# Help
function help(){
	echo "Run the iVIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-g|wbsmih]"
	echo "options:"
	echo "b		background"
	echo "g		select the target GPU."
	echo "s		Server MODE for non vision user."
	echo "c		Run as command line MODE"
	echo "m		Print information with MAGIC."
	echo "n		Not to initialize samples."
	echo "h		help."
}

# Get information from argument
while getopts "g:bwcshmhn" option; do
	case $option in
		b )
			BG=true ;;
		g )
			GPU=$OPTARG ;;
		s )
			SERVER=true ;;
		c )
			RUN_CLI=true ;;
		m )
			MAGIC=false ;;
		n )
			INIT=false ;;
		h )
			help; exit ;;
		\? )
			help; exit ;;
		* )
			help; exit ;;
	esac
done

# Setup Masgic package
if [[ ${MAGIC} = true ]];then check_boxes; fi

# --------------------------------------------------
# Setup variable
# --------------------------------------------------

DOCKER_IMAGE="${DOCKER_USER}/${PROJECT}-${PLATFORM}:${VERSION}"
DOCKER_NAME="${PROJECT}-${PLATFORM}-${VERSION}"

# MOUNT_CAMERA=""	# legacy
MOUNT_GPU=""
MOUNT_INTEL=""

WORKSPACE="/workspace"
SET_VISION=""
SET_TIME=""

INIT_CMD="/workspace/init_samples.sh"
WEB_CMD="/workspace/exec_web_api.sh"
CLI_CMD="bash"
REL_CMD="/workspace/cythonize.sh"
RUN_CMD=""

# --------------------------------------------------
# Combine Docker Command
# --------------------------------------------------

# Initialize Samples
if [[ ${INIT} = true ]]; then RUN_CMD=${INIT_CMD}; fi

# Run CLI or Web
if [[ ${RUN_CLI} = true ]]; then 
	RUN_CMD="${RUN_CMD} ${CLI_CMD}";
else 
	RUN_CMD="${RUN_CMD} ${WEB_CMD}"; 
fi

# Run WebRTC to Web Docker Service
run_webrtc_server;

if [[ ${BG} == true ]]; then RUN_CMD="bash"; fi

# If is desktop mode
if [[ ${SERVER} = false ]];then
	MODE="DESKTOP"
	SET_VISION="-v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix${DISPLAY}"
	xhost + > /dev/null 2>&1
fi

# Docker Container Mode
SET_CONTAINER_MODE="-it"
if [[ ${BG} = true ]]; then SET_CONTAINER_MODE="-dt"; fi

# Setup docker name
SET_NAME="--name ${DOCKER_NAME}"

# System privileged and detect usb device automatically
SET_PRIVILEG="--privileged -v /dev:/dev"

# Intel Option
MOUNT_INTEL="--device /dev/dri --device-cgroup-rule='c 189:* rmw'"

# Sync Time
SET_TIME="-v /etc/localtime:/etc/localtime:ro"

# Mount Network and Port
SET_NETS="--net=host --ipc=host"

# Mount Workspace
MOUNT_WS="-w ${WORKSPACE} -v $(pwd):${WORKSPACE}"

# docker command line
DOCKER_CMD="docker run \
--rm \
${SET_CONTAINER_MODE} \
${SET_PRIVILEG} \
${SET_NAME} \
${MOUNT_GPU} \
${MOUNT_INTEL} \
${SET_NETS} \
${SET_TIME} \
${MOUNT_WS} \
${SET_VISION} \
-e \"IVIT_DEBUG=True\" \
${DOCKER_IMAGE} ${RUN_CMD}"

# Log
printd "Start to run docker command" Cy
echo -ne "${DOCKER_CMD}\n"

bash -c "${DOCKER_CMD}"

stop_webrtc_server; exit 0;