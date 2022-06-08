#!/bin/bash

# Install pre-requirement
if [[ -z $(which jq) ]];then
    echo "Installing requirements .... "
    sudo apt-get install jq -yqq
fi

# Variable
CONF="init-i.json"
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
export INIT_I=/workspace/init-i.json

# Run
if [[ ! -d "./init_i/web" ]];then
    echo "Could not found the web api, make sure the submodule is downloaded."
    exit
fi

# get ip address
ip=$(python3 -c "from init_i.web.utils.common import get_address;print(get_address())")
echo "HOST: ${ip}" | boxes -s 80x5 -a c

gunicorn --worker-class eventlet \
-w ${WORKER} \
--threads ${THREADING} \
--bind 0.0.0.0:${PORT} \
init_i.web.app:app
