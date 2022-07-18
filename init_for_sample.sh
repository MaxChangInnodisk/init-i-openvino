#!/bin/bash
source /workspace/docker/utils.sh

cd /workspace
echo "-----------------------------------"
printd "Initialize Classification Sample" G
./test/classification.sh

# echo "-----------------------------------"
# printd "Initialize YOLOv4 Sample" G
# ./test/yolov4.sh

# echo "-----------------------------------"
# printd "Initialize YOLOv4-tiny Sample" G
# ./test/yolov4-tiny.sh

echo "-----------------------------------"
printd "ALL DONE !" G
echo ""
