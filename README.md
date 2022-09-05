# iVIT-I-Intel
iNIT-I is an AI inference tool which could support multiple AI framework and this repository is just for intel platform.

* [Pre-requirements](#pre-requirements)
* [Prepare Environment](#prepare-environment)
* [Run Sample](#run-sample)
* [Fast Testing](#fast-testing)
* [Web API](#web-api)
* [Sample Information](#sample-information)

# Pre-requirements
* Install [Docker](https://docs.docker.com/engine/install/ubuntu/)



# Prepare Environment

1. Clone Repository and submodule

    * About submodules
    
        Submodule is the web api for ivit-i which will be place in [ivit_i/web](./ivit_i/web)

    * Clone with submodule
        ```bash
        git clone --recurse-submodules https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
        
        # check if submodule is downloaded
        ls ./ivit_i/web
        ai  api  app_bk.py  app.py  docs  __init__.py tools    
        ```
    * Clone pure-repository and download submodule
        ```bash
        git clone https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
        
        git submodule init && git submodule update
        ```
    * Clone specificall branch ( with submodule )
        ```bash
        VER=r0.8
        git clone --recurse-submodules --branch ${VER} https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
        ```

2. Build the docker images

    * Before building docker images

        We use [ivit-i.json](ivit-i.json) to manage environment, like "docker image name", "docker image version", "port number", etc. You can see more detail in [setup_environment.md](docs/setup_environment.md)
    
    * Build docker image with shell script
        ```bash
        sudo ./docker/build.sh
        ```
        In my case, it costs about 12 minutes.

    * Build docker image step by step for developer

        Here is the [documentation](docs/activate_env_for_developer.md) explaining the workflow of `build docker image` and `run docker container`.

3. Run the docker container with web api

    * Before running the container
        1. Avoid Container Conflict

            If you run `ivit-i-{brand}` before, make sure there is no container naming `ivit-i-{brand}` exists, you could run `docker rm ivit-i-{brand}` to remove it.

        2. Initialize Automatically
        
            It will initialize serveral samples which define in [init_samples.sh](./init_samples.sh).
        
    * Run container with **web api**
        ```bash
        sudo ./docker/run.sh
        ```

    * Run container with **interactive mode**
        ```bash
        sudo ./docker/run.sh -c
        ```

    * Run docker container step by step for developer

        Here is the [documentation](docs/activate_env_for_developer.md) explaining the workflow of `build docker image` and `run docker container`.

    * Terminal Output

        <img src="docs/images/run_script_info.png" width=80%>
        
        Refer to [running_workflow.md](docs/running_workflow.md) to see more output information.

# Run Sample
We use `task.json` to configure each AI tasks and using `<model>.json` to configure each AI models, check [ task configuration ](./docs/task_configuration.md) and [model configuration](./docs/model_configuration.md) to get more detail.

1. Enter docker container
    ```bash
    ./docker/run.sh -c
    ```
2. Download model and meta data.
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
* Support Sample

    name             | model                            | describe
    -----------------|-----------------------------------------|--------------
    Classification   | [Resnet50](https://docs.openvino.ai/latest/omz_models_model_resnet_50_tf.html)                              | Classification samples for OpenVINO
    Object detection | [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO
    Segmentation     | [Deeplabv3](https://docs.openvino.ai/latest/omz_models_model_deeplabv3.html)                               | Segmentation samples for OpenVINO
    Pose             | [OpenPose](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python),  [Associative Embedding ](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python)        | Pose samples for OpenVINO
    Yolov4-tiny    |  [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO


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

# Release
```bash
# not initialize and run background
./docker/run.sh -nb

# package python module
docker exec ivit-i-intel ./cythonize.sh
```