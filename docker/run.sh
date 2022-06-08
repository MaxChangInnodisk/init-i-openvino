#!/bin/bash
# --------------------------------------------------------
# Sub function
function check_image(){ 
	echo "$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep ${1} | wc -l )" 
}
function check_container(){ 
	echo "$(docker ps -a --format "{{.Names}}" | grep ${1} | wc -l )" 
}

function lower_case(){
	echo "$1" | tr '[:upper:]' '[:lower:]'
}
function upper_case(){
	echo "$1" | tr '[:lower:]' '[:upper:]'
}
function get_abbr_frameowkr(){
	framework=$1
	framework=$(lower_case $framework)
	case $framework in 
		"tensorrt" )
			echo "trt";;
		"trt" )
			echo "trt";;
		"openvino" )
			echo "vino";;
		"vino" )
			echo "vino";;
		\? )
			echo "";;
		* )
			echo "";;
	esac

}
function print_magic(){
	info=$1
	magic=$2
	echo ""
	if [[ $magic = true ]];then
		echo -e $info | boxes -d dog -s 80x10
	else
		echo -e $info
	fi
	echo ""
}
# ---------------------------------------------------------
# Set the default value of the getopts variable 
gpu="all"
port=""
framework=""
magic=false
server=false
# ---------------------------------------------------------
# help
function help(){
	echo "-----------------------------------------------------------------------"
	echo "Run the iNIT-I environment."
	echo
	echo "Syntax: scriptTemplate [-g|p|c|f|smh]"
	echo "options:"
	echo "g		select the target gpu."
	echo "p		run container with Web API, setup the web api port number."
	echo "f		Setup framework like [ tensorrt, openvino ]."
	echo "s		Server mode for non vision user"
	echo "m		Print information with magic"
	echo "h		help."
	echo "-----------------------------------------------------------------------"
}
while getopts "g:p:c:f:shm" option; do
	case $option in
		g )
			gpu=$OPTARG
			;;
		p )
			port=$OPTARG
			;;
		f )
			framework=$OPTARG
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
# App framework
framework_abbr=$(get_abbr_frameowkr ${framework})
if [[ -z $framework_abbr ]];then help;echo "[ERROR] Unexcepted framework"; exit; fi

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
mount_gpu="--gpus"
set_vision=""
command="bash"
web_api="./run_web_api.sh"
docker_image="ivinno-${framework_abbr}"
workspace="/ivinno-${framework_abbr}"
docker_name="${docker_image}"

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
all_cam=$(ls /dev/video*)
cam_arr=(${all_cam})

for cam_node in "${cam_arr[@]}"
do
    mount_camera="${mount_camera} --device ${cam_node}:${cam_node}"
done

# ---------------------------------------------------------
# Combine gpu option
mount_gpu="${mount_gpu} device=${gpu}"

# ---------------------------------------------------------
# If port is available, run the WEB API
if [[ -n ${port} ]];then 
	# command="python3 ${web_api} --host 0.0.0.0 --port ${port} --af ${framework}"
	command="source ${web_api} -n ${framework_abbr} -b 0.0.0.0:${port} -t 10"
fi

# ---------------------------------------------------------
title="\n\
PROGRAMMER: Welcome to iNIT-I \n\
FRAMEWORK:  ${framework}\n\
MODE:  ${mode}\n\
DOCKER: ${docker_name} \n\
PORT: ${port} \n\
CAMERA:  $((${#cam_arr[@]}/2))\n\
GPU:  ${gpu}\n\
COMMAND: ${command}"

print_magic "${title}" "${magic}"

# ---------------------------------------------------------
# Run container
docker_cmd="docker run \
--name ${docker_name} \
${mount_gpu} \
--rm -it \
--net=host --ipc=host \
-w ${workspace} \
-v `pwd`:${workspace} \
${mount_camera} \
${set_vision} \
${docker_image} \"${command}\""

echo ""
echo -e "Command: ${docker_cmd}"
echo ""
bash -c "${docker_cmd}"
