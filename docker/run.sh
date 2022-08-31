#!/bin/bash
source "$(dirname $(realpath $0))/utils.sh"

# Set the default value of the getopts variable 
GPU="all"
RUN_WEB=true
RUN_CLI=false
RELEASE=false
MAGIC=true
SERVER=false
INIT=true
CONF="./ivit-i.json"

# Install pre-requirement
if [[ -z $(which jq) ]]; then printd "Installing requirements .... "; sudo apt-get install jq -yqq; fi

# Check configuration is exit
FLAG=$(ls ${CONF} 2>/dev/null)
if [[ -z $FLAG ]];then
	printd "Couldn't find configuration (${CONF})" Cy; exit
else
    printd "Detected configuration (${CONF})" Cy
fi

# Parse information from configuration
PROJECT=$(cat ${CONF} | jq -r '.PROJECT')
VERSION=$(cat ${CONF} | jq -r '.VERSION')
PLATFORM=$(cat ${CONF} | jq -r '.PLATFORM')
PORT=$(cat ${CONF} | jq -r '.PORT')

# Help
function help(){
	echo "Run the iVIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-g|wsmih]"
	echo "options:"
	echo "g		select the target GPU."
	echo "s		Server mode for non vision user."
	echo "c		Run as command line mode"
	echo "m		Print information with MAGIC."
	echo "n		Not to initialize samples."
	echo "h		help."
}

# Get information from argument
while getopts "g:wcshmhnl" option; do
	case $option in
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
		l )
			RELEASE=true ;;
		h )
			help; exit ;;
		\? )
			help; exit ;;
		* )
			help; exit ;;
	esac
done

# Setup Masgic package
if [[ ${MAGIC} = true ]];then
	if [[ -z $(which boxes) ]];then 
		printd "Preparing MAGIC "; sudo apt-get install -qy boxes > /dev/null 2>&1; 
	fi
fi

# --------------------------------------------------
# Setup variable
# --------------------------------------------------

DOCKER_IMAGE="${PROJECT}-${PLATFORM}:${VERSION}"
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
if [[ ${RUN_CLI} = true ]]; then RUN_CMD="${RUN_CMD} ${CLI_CMD}";
else RUN_CMD="${RUN_CMD} ${WEB_CMD}"; fi

# If need release, no initialize
if [[ ${RELEASE} = true ]]; then RUN_CMD="${REL_CMD}"; fi

# Check if image come from docker hub
# DOCKER_HUB_IMAGE="maxchanginnodisk/${DOCKER_IMAGE}"
# if [[ ! $(check_image $DOCKER_HUB_IMAGE) -eq 0 ]];then
# 	DOCKER_IMAGE=${DOCKER_HUB_IMAGE}
# 	echo "From Docker Hub ... Update Docker Image Name: ${DOCKER_IMAGE}"
# fi

# Check SERVER or DESKTOP MODE
if [[ ${SERVER} = false ]];then
	mode="DESKTOP"
	SET_VISION="-v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix${DISPLAY}"
	xhost + > /dev/null 2>&1
else
	mode="SERVER"
fi

# Combine Camera option
all_cam=$(ls /dev/video* 2>/dev/null)
cam_arr=("${all_cam}")
# for cam_node in "${cam_arr[@]}"; do MOUNT_CAMERA="${MOUNT_CAMERA} --device ${cam_node}:${cam_node}"; done # legacy

# Combine GPU option
# MOUNT_GPU="${MOUNT_GPU} device=${GPU}"

# Combine Intel Option
MOUNT_INTEL="--device /dev/dri --device-cgroup-rule='c 189:* rmw' "

# Sync Time
SET_TIME="-v /etc/localtime:/etc/localtime:ro"

# Combine docker RUN_CMD line
DOCKER_CMD="docker run \
-it \
--privileged \
-v /dev:/dev \
--name ${DOCKER_NAME} \
${MOUNT_GPU} \
${MOUNT_INTEL} \
--net=host --ipc=host \
${SET_TIME} \
-w ${WORKSPACE} \
-v $(pwd):${WORKSPACE} \
${SET_VISION} \
${DOCKER_IMAGE} ${RUN_CMD}"

# Show information
INFO="\n\
PROGRAMMER: Welcome to ${PROJECT} \n\
FRAMEWORK:  ${PLATFORM}\n\
MODE:  ${mode}\n\
DOCKER: ${DOCKER_IMAGE} \n\
CONTAINER: ${DOCKER_NAME} \n\
Web API: ${RUN_WEB} \n\
HOST: 0.0.0.0:${PORT} \n\
MOUNT_CAMERA:  $((${#cam_arr[@]}/2))\n\
GPU:  ${MOUNT_GPU}\n\
COMMAND: ${RUN_CMD} \n"

# Print the INFO
print_magic "${INFO}" "${MAGIC}"
echo -e "Command: ${DOCKER_CMD}"

# Log
date +%m-%d-%Y
echo "${INFO}"
echo -ne "\nDOCKER COMMAND: \n${DOCKER_CMD}"

# Define run command
RUN_CMD=$(if [[ ${RUN_CLI} = false ]]; then echo ${WEB_CMD}; else echo ${CLI_CMD};fi)

# Check is the container not exist
if [[ $(check_container "${DOCKER_NAME}") -eq 0 ]];then
	
	printd "Run docker container ..." Cy
	bash -c "${DOCKER_CMD}"

# If container exist
else
    printd "Found docker container " Cy

	# Check is the container still running
	if [ "$(check_container_run "${DOCKER_NAME}")" == "true" ]; then
		printd "Container is running" Cy
		docker exec -it "${DOCKER_NAME}" "${RUN_CMD}"
	
	# Start container if container not running 
	else
		printd "Start the docker container" Cy
		docker start "${DOCKER_NAME}"
		docker exec -it "${DOCKER_NAME}" "${RUN_CMD}"
	fi;
fi;