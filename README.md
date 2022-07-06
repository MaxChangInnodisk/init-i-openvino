# iNIT-I-Intel
iNIT-I is an AI inference tool which could support multiple AI framework and this repository is just for intel platform.

* [Pre-requirements](#pre-requirements)
* [Setting up configuration](#setting-environment)
* [Build docker image](#build-docker-image)
* [Run docker container](#run-docker-container)
* [Task configuration](#configuration)
* [Run DEMO](#run-demo)
* [Samples](#samples)

## Pre-requirements
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/)

## Setting environment
We use [init-i.json](init-i.json) to configure environment, you can see the detail in [configure_environment.md](docs/configure_environment.md)
| Key       | Sample            | Describe
| ---       | ---               | --- 
| PROJECT   | init-i            | project name
| VERSION   | v0.1              | docker image version
| HOST      |                 | ip address, it will capture automatically if not setting.
| PORT      | 819               | port number, 819 for intel

##  Build docker image
```shell
sudo ./docker/build.sh
```

## Run docker container
```shell
sudo ./docker/run.sh -wm
```

## Run DEMO
We Using `task.json` to configure each AI task and using `<model>.json` to configure each models, check [ task configuration ](./docs/task_configuration.md) and [model configuration](./docs/model_configuration.md) to see more detail.
> Classficiation
``` shell
python3 demo.py --config task/classificaiton_sample/task.json
```

## Samples

name             | model                            | describe
-----------------|-----------------------------------------|--------------
Classification   | [Resnet50](https://docs.openvino.ai/latest/omz_models_model_resnet_50_tf.html)                              | Classification samples for OpenVINO
OBject detection | [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO
Segmentation     | [Deeplabv3](https://docs.openvino.ai/latest/omz_models_model_deeplabv3.html)                               | Segmentation samples for OpenVINO
Pose             | [OpenPose](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python),  [Associative Embedding ](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python)        | Pose samples for OpenVINO
