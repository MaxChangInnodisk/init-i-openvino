#!/bin/bash

function waitTime(){
	TIME_FLAG=$1
	while [ $TIME_FLAG -gt 0 ]; do
		printf "\rWait ... (${TIME_FLAG}) "; sleep 1
		(( TIME_FLAG-- ))
	done
	printf "\r                 \n"
}

# ========================================================
# Basic Parameters
CONF="ivit-i.json"
DOCKER_USER="maxchanginnodisk"

# ========================================================
# Store the utilities
FILE=$(realpath "$0")
ROOT=$(dirname "${FILE}")
source "${ROOT}/utils.sh"

# ========================================================
# Check configuration is exit
FLAG=$(ls ${CONF} 2>/dev/null)
if [[ -z $FLAG ]];then 
	printd "Couldn't find configuration (${CONF})" Cy; 
	exit
else 
	printd "Detected configuration (${CONF})" Cy; 
fi

# ========================================================
# Set the default value of the getopts variable 
INTERATIVE=true
RUN_WEB=true
RUN_CLI=false
MAGIC=true
INIT=true
QUICK=false

# ========================================================
# Install pre-requirement
check_jq

# ========================================================
# Parse information from configuration
PROJECT=$(cat ${CONF} | jq -r '.PROJECT')
VERSION=$(cat ${CONF} | jq -r '.VERSION')
PLATFORM=$(cat ${CONF} | jq -r '.PLATFORM')
PORT=$(cat ${CONF} | jq -r '.PORT')
WEB_PORT=$(cat ${CONF} | jq -r '.WEB_PORT')
NGINX_PORT=$(cat ${CONF} | jq -r '.NGINX_PORT')

# Update docker-compose value
update_compose_env ${ROOT}/docker-compose.yml API_PORT=${PORT} NGINX_PORT=${NGINX_PORT} WEB_PORT=${WEB_PORT}

# Update ivit-i-web-ui
WEB_CONFIG=${ROOT}/ivit-i-web-ui.json
jq --arg WEB_PORT "${WEB_PORT}" \
--arg NGINX_PORT "${NGINX_PORT}" \
'(.web_port = $WEB_PORT | .nginx_port=$NGINX_PORT)' ${WEB_CONFIG} > file.tmp
mv file.tmp ${WEB_CONFIG}

# ========================================================
# Help
function help(){
	echo "Run the iVIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-g|bcmqnh]"
	echo "options:"
	echo "b		run in background"
	echo "c		Run with command line interface mode"
	echo "m		Print information with MAGIC."
	echo "q		Qucik launch iVIT-I"
	echo "n		Not to initialize samples."
	echo "h		help."
}

# Get information from argument
while getopts "g:bcmnqh:" option; do
	case $option in
		b )
			INTERATIVE=false ;;
		c )
			RUN_CLI=true ;;
		m )
			MAGIC=false ;;
		q )
			QUICK=true ;;
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

# ========================================================
# Initialize Docker Command Option

# [NAME]
DOCKER_IMAGE="${DOCKER_USER}/${PROJECT}-${PLATFORM}:${VERSION}"
DOCKER_NAME="${PROJECT}-${PLATFORM}-${VERSION}"

# [BASIC]
WS="/workspace"
SET_NAME="--name ${DOCKER_NAME}"
MOUNT_WS="-w ${WS} -v $(pwd):${WS}"
SET_TIME="-v /etc/localtime:/etc/localtime:ro"
SET_NETS="--net=host"

# [DEFINE COMMAND]
RUN_CMD=""
INIT_CMD="/${WS}/init_samples.sh"
WEB_CMD="/${WS}/exec_web_api.sh"
CLI_CMD="bash"

# [DEFINE OPTION]
SET_CONTAINER_MODE=""
SET_VISION=""
SET_PRIVILEG=""
SET_MEM=""
MOUNT_ACCELERATOR=""

##############################################################################
#																			 #
# !!!  Important, Please modify [ACCELERATOR] to fit your platform need  !!! #
#																			 #
##############################################################################

# [ACCELERATOR]
SET_PRIVILEG="--privileged -v /dev:/dev"
SET_MEM="--ipc=host"
MOUNT_ACCELERATOR="--device /dev/dri --device-cgroup-rule='c 189:* rmw'"

# ========================================================
# [COMMAND] Checking Docker Command

# If need initialize samples
if [[ ${INIT} = true ]]; then 	
	RUN_CMD=${INIT_CMD}
	printd " * Need Initialize Samples" R
fi

# Checking Run CLI or Web
if [[ ${RUN_CLI} = true ]]; then 
	RUN_CMD="${RUN_CMD} ${CLI_CMD}"
	printd " * Run Command Line Interface" R
else 
	RUN_CMD="${RUN_CMD} ${WEB_CMD}"
	printd " * Run Web API Directly" R
fi

# ========================================================
# [VISION] Set up Vision option for docker if need
if [[ ! -z $(echo ${DISPLAY}) ]];then
	SET_VISION="-v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix${DISPLAY}"
	xhost + > /dev/null 2>&1
	printd " * Detected monitor" R
fi

# ========================================================
# [Basckground] Update background option
if [[ ${INTERATIVE} = true ]]; then 
	SET_CONTAINER_MODE="-it"
	printd " * Run Interative Terminal Mode" R
else
	SET_CONTAINER_MODE="-dt"; 
	printd " * Run Background Mode" R
fi

# Conbine docker command line
DOCKER_CMD="docker run \
--rm \
${SET_CONTAINER_MODE} \
${SET_NAME} \
${SET_PRIVILEG} \
${MOUNT_ACCELERATOR} \
${SET_NETS} \
${SET_MEM} \
${SET_TIME} \
${MOUNT_WS} \
${SET_VISION} \
-e \"IVIT_DEBUG=True\" \
${DOCKER_IMAGE} ${RUN_CMD}"

# ========================================================
# Logout and wait
echo -ne "\n${DOCKER_CMD}\n"
echo ""
if [[ ${QUICK} = false ]];then waitTime 5; fi

# ========================================================
# Execution

printd "Launch Relative Container" BR
docker compose -f ./docker/docker-compose.yml up -d 

# Run docker command 
printd "Launch iVIT-I Container" BR
bash -c "${DOCKER_CMD}"

printd "Close Relative Container" BR
if [[ ${INTERATIVE} = true ]];then
	docker compose -f ./docker/docker-compose.yml down
fi

exit 0;