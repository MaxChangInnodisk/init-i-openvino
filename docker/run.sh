#!/bin/bash
source "$(dirname $(realpath $0))/utils.sh"

# Set the default value of the getopts variable 
web=""
project_name="ivit-i"
platform=""
version="latest"
magic=false
server=false

# Install pre-requirement
if [[ -z $(which jq) ]];then
    printd "Installing requirements .... " Cy
    sudo apt-get install jq -yqq
fi

# Variable
CONF="ivit-i.json"
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
project_name=$(cat ${CONF} | jq -r '.PROJECT')
version=$(cat ${CONF} | jq -r '.VERSION')
platform=$(cat ${CONF} | jq -r '.PLATFORM')
port=$(cat ${CONF} | jq -r '.PORT')

# help
function help(){
	echo "Run the iNIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-wsmh]"
	echo "options:"
	echo "w		run container with Web API."
	echo "s		Server mode for non vision user"
	echo "m		Print information with magic"
	echo "h		help."
}
while getopts "c:f:v:wshmh" option; do
	case $option in
		w )
			web=true
			;;
		s )
			server=true
			;;
		m )
			magic=true
			;;
		h )
			help
			exit
			;;
		\? )
			help
			exit
			;;
		* )
			help
			exit
			;;
	esac
done

# ---------------------------------------------------------
# Setup Masgic
if [[ ${magic} = true ]];then
	printf "Preparing magic ... "
	sudo apt-get install -qy boxes > /dev/null 2>&1
	printf "Done \n"
fi

# ---------------------------------------------------------
# Setup variable
docker_image=""
workspace=""
docker_name=""
mount_camera=""
set_vision=""
command="bash"
web_api="./exec_web_api.sh"
docker_image="${project_name}-${platform}:${version}"
workspace="/workspace"
docker_name="${project_name}-${platform}"

# ---------------------------------------------------------
# Check if image come from docker hub
hub_name="maxchanginnodisk/${docker_image}"
from_hub=$(check_image $hub_name)
if [[ ! from_hub -eq 0 ]];then
	echo "From Docker Hub"
	docker_image=${hub_name}
fi

# ---------------------------------------------------------
# SERVER or DESKTOP MODE
if [[ ${server} = false ]];then
	mode="DESKTOP"
	set_vision="-v /etc/localtime:/etc/localtime:ro -v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix${DISPLAY}"
	# let display could connect by every device
	xhost + > /dev/null 2>&1
else
	mode="SERVER"
fi

# ---------------------------------------------------------
# Combine Camera option
all_cam=$(ls /dev/video* 2>/dev/null)
cam_arr=(${all_cam})

for cam_node in "${cam_arr[@]}"
do
    mount_camera="${mount_camera} --device ${cam_node}:${cam_node}"
done

# ---------------------------------------------------------
# If web is available, run the WEB API
if [[ -n ${web} ]];then 
	command="${web_api}"
fi

# ---------------------------------------------------------
# Show information
title="\n\
PROGRAMMER: Welcome to iNIT-I \n\
FRAMEWORK:  ${platform}\n\
MODE:  ${mode}\n\
DOCKER: ${docker_image} \n\
CONTAINER: ${docker_name} \n\
Web API: ${web} \n\
HOST: 0.0.0.0:${port} \n\
CAMERA:  $((${#cam_arr[@]}/2))\n\
GPU:  ${gpu}\n\
COMMAND: ${command}"

print_magic "${title}" "${magic}"

# ---------------------------------------------------------
# Run container
docker_cmd="docker run \
--name ${docker_name} \
--rm -it \
--net=host --ipc=host \
--device /dev/dri \
--device-cgroup-rule='c 189:* rmw' \
-v /dev/bus/usb:/dev/bus/usb \
-w ${workspace} \
-v `pwd`:${workspace} \
${mount_camera} \
${set_vision} \
${docker_image} \"${command}\""

echo ""
echo -e "Command: ${docker_cmd}"
echo ""
bash -c "${docker_cmd}"
