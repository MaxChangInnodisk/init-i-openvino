#!/bin/bash

# Varaibles
IVIT="/home/innodisk/workspace/ivit-i-intel"

# Helper
REST='\e[0m'
GREEN='\e[0;32m'
BGREEN='\e[7;32m'
RED='\e[0;31m'
BRED='\e[7;31m'
YELLOW='\e[0;33m'
BYELLOW='\e[7;33m'
Cyan='\033[0;36m'
BCyan='\033[7;36m'

function printd(){            
    if [ -z $2 ];then COLOR=$REST
    elif [ $2 = "G" ];then COLOR=$GREEN
	elif [ $2 = "BG" ];then COLOR=$BGREEN
	elif [ $2 = "R" ];then COLOR=$RED
    elif [ $2 = "BR" ];then COLOR=$BRED
	elif [ $2 = "Y" ];then COLOR=$YELLOW
    elif [ $2 = "BY" ];then COLOR=$BYELLOW
    elif [ $2 = "Cy" ];then COLOR=$Cyan
    elif [ $2 = "BCy" ];then COLOR=$BCyan
    else COLOR=$REST
    fi
    echo -e "$(date +"%y:%m:%d %T") ${COLOR}$1${REST}"
}




SLEEP_TIME=3
sleep $SLEEP_TIME

printd "Launch iVIT-I" BR
cd "${IVIT}" || exit
./docker/run.sh