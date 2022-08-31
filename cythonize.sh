#!/bin/bash

ROOT=$(pwd)
API="ivit_i"
WEB="web"

OUTPUT="./out"

# Exclude Web API
if [[ -d "${API}/${WEB}" ]];then 
    echo "Move out Web API folder"
    mv -f "${API}/${WEB}" "${ROOT}/"; 
fi

# Start to cythonize via merak
if [[ -z $(which python) ]];then 
    echo "Could not find python, link python3 to python"
    ln -s /usr/bin/python3 /usr/bin/python; 
fi

echo "Start to cythonize ivit_i ... "
merak cythonize "${API}" "${OUTPUT}"

# Remove whole ivit_i folder and create a new one
rm -rf "${API}"
mv -f "${OUTPUT}/${API}" "${ROOT}"
rm -rf out

# Move so api file and web api into ivit_i folder
mv -f "${ROOT}/${WEB}" ${API}

# Change Owner
chown 1000:1000 -R /workspace

echo "Done !!!!"