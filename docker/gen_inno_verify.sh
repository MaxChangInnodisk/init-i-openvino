#!/bin/bash
FILE_PATH=$(realpath "$0")

FILE_DIR=$(dirname "${FILE_PATH}" )

cd "${FILE_DIR}" || exit

pyinstaller -F ../ivit_i/utils/verify.py

mv dist/verify ./inno_verify

rm -rf dist build verify* 

chown 1000:1000 -R .

echo "Done"