#!/bin/bash
WID=80

# Install pre-requirement
if [[ -z $(which jq) ]];then
    echo "Installing requirements .... "
    sudo apt-get install jq -yqq
fi

# Variable
CONF="ivit-i.json"
FLAG=$(ls ${CONF} 2>/dev/null)
if [[ -z $FLAG ]];then
    CONF="${RUN_PWD}/${CONF}"
    FLAG=$(ls ${CONF} 2>/dev/null)
    if [[ -z $FLAG ]];then
        echo "Couldn't find configuration (${CONF})"
        exit
    fi
fi

# Parse information from configuration
PORT=$(cat ${CONF} | jq -r '.PORT')
WORKER=$(cat ${CONF} | jq -r '.WORKER')
THREADING=$(cat ${CONF} | jq -r '.THREADING')
export IVIT_I=/workspace/ivit-i.json

# Run
if [[ ! -d "./ivit_i/web" ]];then
    echo "Could not found the web api, make sure the submodule is downloaded."
    exit
fi

# get ip address
IP=$(python3 ./docker/update_available_ip.py)

figlet -w ${WID} -c "iVIT-I Web API"
echo "HOST: ${IP}:${PORT}" | boxes -s "${WID}x5" -a c
echo ""

gunicorn --worker-class eventlet \
-w ${WORKER} \
--threads ${THREADING} \
--bind 0.0.0.0:${PORT} \
ivit_i.web.app:app
