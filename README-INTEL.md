# iVINNO-VINO
A library to inference model of openvino. This library enables the use of classification, object detection, segmentation, humanpose.


##  Installation docker container  
```shell
sudo ./docker/build.sh
sudo ./docker/run.sh -m
```

## Demo config
Open to app/example_sample/task.json. Change the path of model_json to you will using the application.
```json
{
    "framework":"openvino",
    "input_data":"/dev/video0",
    "prim-1":{
        "model_json":"./config/model_config/classification.json"
        }
}

```
If you want to change your model of openvino and parameters, you should be changed the content of app/example_sample/example.json 

### Example
```json

{  
    "tag":"class",
    "openvino":{
        "model_path":"resnet_v1_50_inference.xml",
        "label_path":"iamgenet.names",
        "loop":false,
        "output":false,
        "device":"CPU",
        "num_infer_requests":0,
        "num_streams":"",
        "num_threads":null,
        "number_top":1,
        "config":null,
        "output_resolution":null,
        "utilization_monitors":""
    }
```
## RUN
``` shell
python3 openvino_demo.py --config app/example_sample/task.json
```

## Samples

name             | model of test                           | describe
-----------------|-----------------------------------------|--------------
Classification   | [Resnet50](https://docs.openvino.ai/latest/omz_models_model_resnet_50_tf.html)                              | Classification samples for OpenVINO
OBject detection | [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO
Segmentation     | [Deeplabv3](https://docs.openvino.ai/latest/omz_models_model_deeplabv3.html)                               | Segmentation samples for OpenVINO
Pose             | [OpenPose](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python),  [Associative Embedding ](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python)        | Pose samples for OpenVINO
