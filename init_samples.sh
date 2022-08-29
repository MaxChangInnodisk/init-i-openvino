#!/bin/bash
source /workspace/docker/utils.sh

printd "Start to initialize Sample ..." BCy
echo -e "\
\n
Supported Samples: \n\
    - Classification \n\
    - objectdetection_sample \n\
    - retail_product_detection \n\
    - segmentation_sample \n\
    - humanpose_sample_ae \n\
    - yolov4-tiny \n"

cd /workspace
echo "-----------------------------------"
printd "Initialize Classification Sample" G
./test/classification.sh

echo "-----------------------------------"
printd "Initialize humanpose_sample_ae" G
./test/humanpose_sample_ae.sh

echo "-----------------------------------"
printd "Initialize objectdetection_sample" G
./test/objectdetection_sample.sh

echo "-----------------------------------"
printd "Initialize retail_product_detection" G
./test/retail_product_detection.sh

echo "-----------------------------------"
printd "Initialize segmentation_sample" G
./test/segmentation_sample.sh

echo "-----------------------------------"
printd "Initialize yolov4-tiny" G
./test/yolov4-tiny.sh

echo "-----------------------------------"
printd "ALL DONE !" G
echo ""

/bin/bash -c "$@"