#!/bin/bash
source /workspace/tools/utils.sh

printd "Start to initialize Sample ..." BCy
echo -e "\
\n
Supported Samples: \n\
    - Classification \n\
    - object-detection-sample \n\
    - yolov4-tiny \n\
    - parking-lot-detect \n\
    - traffic-flow-detect \n\
    - wrong-side-detect \n\
"

cd /workspace || exit

#  1  classification-sample
#  2  object-detection-sample
#  3  parking-lot-detect
#  4  traffic-flow-detect
#  5  wrong-side-detect
#  6  yolov4-tiny-sample

echo "-----------------------------------"
printd "Initialize Classification Sample" G
# ./test/classification.sh
ivit-launcher --task classification-sample

echo "-----------------------------------"
printd "Initialize object-detection-sample" G
# ./test/object-detection-sample.sh
ivit-launcher --task object-detection-sample

echo "-----------------------------------"
printd "Initialize yolov4-tiny" G
# ./test/yolov4-tiny.sh
ivit-launcher --task yolov4-tiny-sample

echo "-----------------------------------"
printd "Initialize parking-lot-detect" G
# ./test/parking-lot-detect.sh
ivit-launcher --task parking-lot-detect

echo "-----------------------------------"
printd "Initialize traffic-flow-detect" G
# ./test/traffic-flow-detect.sh
ivit-launcher --task traffic-flow-detect

echo "-----------------------------------"
printd "Initialize wrong-side-detect" G
# ./test/wrong-side-detect.sh
ivit-launcher --task wrong-side-detect

echo "-----------------------------------"
printd "ALL DONE !" G
echo ""

VAR=$@
CMD="bash"

if [[ -n "$VAR" ]];then 
    CMD=$VAR; echo $CMD
fi

/bin/bash -c "$CMD"