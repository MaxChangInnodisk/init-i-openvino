FNAME="./verify-inno-usb";
REST='\e[0m';
GREEN='\e[0;32m';
BGREEN='\e[7;32m';
BRED='\e[7;31m';
Cyan='\033[0;36m';
BCyan='\033[7;36m';

function printd(){            
    
    if [ -z $2 ];then COLOR=$REST
    elif [ $2 = "G" ];then COLOR=$GREEN
    elif [ $2 = "R" ];then COLOR=$BRED
    elif [ $2 = "Cy" ];then COLOR=$Cyan
    elif [ $2 = "BCy" ];then COLOR=$BCyan
    else COLOR=$REST
    fi

    echo -e "$(date +"%T") ${COLOR}$1${REST}"
}

function verify(){
    PID="196d"
    VID="0201"

    result=`lsusb | grep "${PID}:${VID}"`


    if [[ -z ${result} ]];then
        printd "Verify Innodisk Device ... FAILED" R
        exit
    else
        printd "Verify Innodisk Device ... PASS" BCy
    fi
}

# Verify USB
verify

# 
if [[ -f "/workspace/init_samples.sh" ]];then
    bash /workspace/init_samples.sh
else
    echo "Not found init_samples"
fi

# Entry Point
/bin/bash -c "$@"