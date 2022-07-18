#!/bin/bash
source /workspace/docker/utils.sh

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
printd "ALL DONE !" G
echo ""
