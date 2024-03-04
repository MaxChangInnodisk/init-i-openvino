# Object Detection Sample
iVIT Object Detection Sample, this sample demonstrates how to do inference of image object detection models using iVIT [Source](../ivit_source_sample/README.md) and [Displayer](../ivit_displayer_sample/README.md).


* Setting Varaible
    ```bash
    cd /workspace/samples/torch_onnx_yolo_sample
    ```
* Run Sample:
    
    ```bash
    ROOT=/workspace
    EXEC_PY="python3 onnx_demo.py"
    INPUT=${ROOT}/data/sd-card.png
    MODEL=${ROOT}/model/sd_card_yolo_torch_ir/sd_card_yolo_torch_ir.xml
    LABEL=${ROOT}/model/sd_card_yolo_torch_ir/coco.name
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
