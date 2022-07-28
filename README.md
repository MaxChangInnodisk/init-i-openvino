# iVIT-I-Intel
iNIT-I is an AI inference tool which could support multiple AI framework and this repository is just for intel platform.

* [Pre-requirements](#pre-requirements)
* [Build docker image](#build-docker-image)
* [Run Sample](#run-sample)
* [Fast Testing](#fast-testing)
* [Web API](#web-api)
* [Sample Information](#sample-information)

# Pre-requirements
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/)


# Build docker image
1. Download iVIT-I with Web API
    ```shell
    git clone --recurse-submodules https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
    ```
2. Build from docker file
    
    We use [ivit-i.json](ivit-i.json) to manage environment, like "docker image name", "docker image version", "port number", etc. You can see more detail in [setup_environment.md](docs/setup_environment.md)
    ```bash
    sudo ./docker/build.sh
    ```
3. Run the docker container with web api
    ```bash
    # Initialize default sample
    sudo ./docker/run.sh

    # Run with CLI mode
    sudo ./docker/run.sh -c
    ```
    * To see more detail -> [running_workflow.md](docs/running_workflow.md)
        <img src="docs/images/run_script_info.png" width=80%>

# Run Sample
We use `task.json` to configure each AI tasks and using `<model>.json` to configure each AI models, check [ task configuration ](./docs/task_configuration.md) and [model configuration](./docs/model_configuration.md) to get more detail.

1. Enter container
    ```bash
    sudo ./docker/run.sh
    ```
2. Download model ( only in sample task ) and meta data.
    ```bash
    # Model
    ./task/classification_sample/download_model.sh

    # Meta data
    ./task/classification_sample/download_data.sh
    ```
3. Run demo script.
    ``` bash
    python3 demo.py --config task/classification_sample/task.json
    ```

# Fast Testing
We provide the fast-test for each sample, please check the [document](./test/README.md).


# Web API
<details>
    <summary>
        We recommand <a href="https://www.postman.com/">Postman</a> to test your web api , you could see more detail in <code>{IP Address}:{PORT}/apidocs</code>.
    </summary>
    <img src="docs/images/apidocs.png" width=80%>
</details>
<br>

# Sample Information

name             | model                            | describe
-----------------|-----------------------------------------|--------------
Classification   | [Resnet50](https://docs.openvino.ai/latest/omz_models_model_resnet_50_tf.html)                              | Classification samples for OpenVINO
Object detection | [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO
Segmentation     | [Deeplabv3](https://docs.openvino.ai/latest/omz_models_model_deeplabv3.html)                               | Segmentation samples for OpenVINO
Pose             | [OpenPose](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python),  [Associative Embedding ](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python)        | Pose samples for OpenVINO

