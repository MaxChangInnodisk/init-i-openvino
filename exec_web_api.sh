#!/bin/bash
WID=80
source /workspace/tools/utils.sh

# Variable
CONF="ivit-i.json"
FLAG=$(ls ${CONF} 2>/dev/null)
if [[ -z $FLAG ]];then
    CONF="${RUN_PWD}/${CONF}"
    FLAG=$(ls ${CONF} 2>/dev/null)
    if [[ -z $FLAG ]];then
        printd "Couldn't find configuration (${CONF})" R && exit
    fi
fi

# Parse information from configuration
PORT=$(cat ${CONF} | jq -r '.PORT')
WORKER=$(cat ${CONF} | jq -r '.WORKER')
THREADING=$(cat ${CONF} | jq -r '.THREADING')
export IVIT_I=/workspace/ivit-i.json

# Check is web api is running
if [[ -n $(lsof -i:${PORT}) ]];then
    printd "Web API is still running" Y && exit
fi

# get ip address
IP=$(python3 ./tools/update_available_ip.py)
printd "Update available ip address ($IP)"

# Run web api
printd "Run Web API in background"
gunicorn \
-w ${WORKER} \
--threads ${THREADING} \
--bind 0.0.0.0:${PORT} \
ivit_i.web.app:app