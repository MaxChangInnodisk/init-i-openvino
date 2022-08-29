#!/bin/bash

ROOT=$(pwd)
API="ivit_i"
WEB="web"

OUTPUT="./out"

# Exclude Web API
mv -f "${API}/${WEB}" "${ROOT}/"

# Start to cythonize via merak
ln -s /usr/bin/python3 /usr/bin/python
merak cythonize "${API}" "${OUTPUT}"

# Remove whole ivit_i folder and create a new one
rm -rf "${API}" && mv -f "${OUTPUT}/${API}" "${ROOT}"

# Move so api file and web api into ivit_i folder
mv -f "${ROOT}/${WEB}"  ${API}

echo "Done !!!!"