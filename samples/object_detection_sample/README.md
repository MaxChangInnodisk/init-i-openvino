# Object Detection Sample
iVIT Object Detection Sample, this sample demonstrates how to do inference of image object detection models using iVIT [Source](../ivit_source_sample/README.md) and [Displayer](../ivit_displayer_sample/README.md).

## Getting Start
* Clone Repository    
    ```bash
    git clone  https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
    ```
* Run iVIT-I Docker Container
    ```bash
    sudo ./docker/run.sh    # Enter the docker container
    ```
* Download Data
    ```bash
    # Move to target folder
    cd /workspace/samples/object_detection_sample
    
    # Download File
    chmod u+x ./download_data.sh ./download_yolov3.sh ./download_yolov4-tiny.sh
    ./download_data.sh        # Testing Data
    ./download_yolov3.sh      # Download YOLOv3 Model
    ./download_yolov4-tiny.sh # Download YOLOv4-Tiny Model
    ```
* Setting Varaible
    ```bash
    EXEC_PY="python3 ./object_detection_demo.py"

    ROOT=/workspace
    INPUT=${ROOT}/data/car.mp4
    ```
* Run Sample:
    
    ```bash
    MODEL=${ROOT}/model/yolo-v3-tf/yolo-v3-tf.xml
    LABEL=${ROOT}/model/yolo-v3-tf/coco.names
    ARCHT=yolo
    ${EXEC_PY} -m ${MODEL} -l ${LABEL} -i ${INPUT} -at ${ARCHT}
    ```

# Usage
* Base on YOLOv4
    ```bash
    cd /workspace/samples/object_detection_sample
    ./download_yolov4-tiny.sh
    
    # YOLOv4 Tiny: `-at` have to be yolov4, same with yolov4 model
    MODEL=${ROOT}/model/yolo-v4-tiny-tf/yolo-v4-tiny-tf.xml
    LABEL=${ROOT}/model/yolo-v4-tiny-tf/coco.names
    ARCHT=yolov4
    ```
* Add Confidence Threshold
    ```bash
    # Define threshold
    THRES=0.9
    ${EXEC_PY} -m ${MODEL} -l ${LABEL} -i ${INPUT} -at ${ARCHT} -t ${THRES}
    ```
    
* Run with iGPU
    ```bash
    ${EXEC_PY} -m ${MODEL} -l ${LABEL} -i ${INPUT} -at ${ARCHT} -d GPU

## Format of output 
*  The format of result after model predict like below.

| Type | Description |
| --- | --- |
|object|Object's properties : xmin ,ymin ,xmax ,ymax ,score ,id ,label |
* Example:
    ```bash
        detection        # (type object)                   
        detection.label  # (type str)           value : person   
        detection.score  # (type numpy.float64) value : 0.960135 
        detection.xmin   # (type int)           value : 1        
        detection.ymin   # (type int)           value : 78       
        detection.xmax   # (type int)           value : 438      
    ```

# Advance

* Custom Model with custom anchors
    
    ```bash
    MODEL=${ROOT}/model/safety_helmet/safety_helmet.xml
    LABEL=${ROOT}/model/safety_helmet/classes.txt
    ARCHT=yolov4
    INPUT=/dev/video0
    ANCHOR="20.0 24.0 46.0 18.0 31.0 38.0 45.0 54.0 86.0 38.0 41.0 106.0 67.0 77.0 111.0 110.0 170.0 196.0"

    ${EXEC_PY} -m ${MODEL} -l ${LABEL} -i ${INPUT} -at ${ARCHT} --anchors ${ANCHOR} 

    ```
