![LOGO](docs/images/iVIT-I-Logo-B.png)

# iVIT-I-Intel
iNIT-I is an AI inference tool which could support multiple AI framework and this repository is just for intel platform.

* [Pre-requirements](#pre-requirements)
* [Prepare Environment](#prepare-environment)
* [Run Sample](#run-sample)
* [Fast Testing](#fast-testing)
* [Web API](#web-api)

# Pre-requirements
* [Docker](https://docs.docker.com/engine/install/ubuntu/)

# Prepare Environment

1. Clone Repository

    ```bash
    git clone  https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
    ```

2. Run the docker container with web api

    * Run container with **web api**
        ```bash
        sudo ./docker/run.sh
        ```

    * Run container with **command line mode**
        ```bash
        sudo ./docker/run.sh -c
        ```

    * Run container without initialize sample
        ```bash
        sudo ./docker/run.sh -nc

        # if you need to initialize samples
        ./init_samples.sh

        # if you need to launch web api
        ./exec_web_api.sh
        ```

    * Run docker container step by step for developer

        Here is the [documentation](docs/activate_env_for_developer.md) explaining the workflow of `run docker container`.

    * Terminal Output

        <img src="docs/images/run_script_info.png" width=80%>
        

# Run Sample
We use `task.json` to configure each AI tasks and using `<model>.json` to configure each AI models, check [ task configuration ](./docs/task_configuration.md) and [model configuration](./docs/model_configuration.md) to get more detail.

1. Enter docker container
    ```bash
    ./docker/run.sh -c

    TASK_NAME=classification-sample
    ```
2. Download model and meta data.
    ```bash
    # Model
    ./task/${TASK_NAME}/download_model.sh

    # Meta data
    ./task/${TASK_NAME}/download_data.sh
    ```
3. Run demo script with GUI.
    ``` bash
    python3 demo.py -c task/${TASK_NAME}/task.json
    ```
4. CLI mode - without GUI, only console output
    ```bash
    python3 demo.py -c task/${TASK_NAME}/task.json -s
    ```
5. RTSP mode
    ```bash
    # rtsp://localhost:8554/mystream
    python3 demo.py -c task/${TASK_NAME}/task.json -r
    ```
6. Custom RTSP
    ```bash
    # rtsp://localhost:8554/test
    python3 demo.py -c task/${TASK_NAME}/task.json -r \
    --name /test
    ```
7. Usage
    ```bash
    python3 demo.py --help
    
    cat <<EOF
    usage: demo.py [-h] [-c CONFIG] [-s] [-r] [-d] [-m MODE] [-i IP] [-p PORT]
                [-n NAME]

    optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                            The path of application config
    -s, --server          Server mode, not to display the opencv windows
    -r, --rtsp            RTSP mode, not to display the opencv windows
    -d, --debug           Debug mode
    -m MODE, --mode MODE  Select sync mode or async mode{ 0: sync, 1: async }
    -i IP, --ip IP        The ip address of RTSP uri
    -p PORT, --port PORT  The port number of RTSP uri
    -n NAME, --name NAME  The name of RTSP uri
    EOF
    ```

# Fast Testing

* Supported Samples: 
    - Classification 
    - object-detection-sample 
    - yolov4-tiny 
    - parking-lot-detect 
    - traffic-flow-detect 
    - wrong-side-detect 

* classification-sample
    ```bash
    # Initialize
    ivit-launcher --task classification-sample

    # Initialize and Run
    ivit-launcher --task classification-sample --demo 

    # Start with RTSP
    ivit-launcher --task classification-sample --demo --rtsp
    ```
* show available task name
    ```bash
    List Tasks
        1  classification-sample
        2  object-detection-sample
        3  parking-lot-detect
        4  traffic-flow-detect
        5  wrong-side-detect
        6  yolov4-tiny-sample
    ```
* usage (help)
    ```
    ivit-launcher --help

    Usage:
            -t | --task             : define task name
            -l | --list             : show available task name
            -d | --demo             : run demo ( display cv window )
            -s | --server   : run server mode ( only show log )
            -r | --rtsp             : run rtsp mode ( rtsp://127.0.0.0:8554/mystream )
            --route                 : define rtsp route, ( rtsp://127.0.0.0:8554/<route> )
            --help                  : show usage
    ```

# Web API
<details>
    <summary>
        We recommand <a href="https://www.postman.com/">Postman</a> to test your web api , you could see more detail in <code>{IP Address}:{PORT}/apidocs</code>.
    </summary>
    <img src="docs/images/apidocs.png" width=80%>
</details>
<br>


# Log
* r1.0.3
    1. Add source pipeline to improve the streaming.
    2. Add async inference pipeline to improve the streaming.
    3. Add RTSP output: add [rtsp-simple-server](https://github.com/aler9/rtsp-simple-server), gstreamer and rebuild opencv.
    4. Add WebRTC server: add [rtsp-to-web](https://github.com/deepch/RTSPtoWeb).
    5. Provide new entrance `ivit-launcher` to test sample quickly. ([check here](#fast-testing)).
    6. Reset application when source pipeline is restart.

* r1.0.2
    1. Application with `new condition` and `new algorithm`
        * Add `Area Event` in Each Application.
        * Add `Condition Event (Logic)` , `Alerm` in `Counting`.
        * Add `Alerm`, `Sensitivity` in `Area Detection` and `Moving Direction`.
        * Add `Direction` in `Moving Direction`.
    2. New Default Task Sample ( More Realistic Use Case )
        * Add `parking-lot-detect` ,`wrong-side-detect` , `traffic-flow-detect` 
        * delete `pose estimation` and `segmentation`  samples.
    3. New Model and Label Path
        * Change the model path to `/workspace/model` folder to reduce the task operation time and reduce disk space.


* Support Sample

    name             | model                            | describe
    -----------------|-----------------------------------------|--------------
    Classification   | [Resnet50](https://docs.openvino.ai/latest/omz_models_model_resnet_50_tf.html)                              | Classification samples for OpenVINO
    Object detection | [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO
    Segmentation     | [Deeplabv3](https://docs.openvino.ai/latest/omz_models_model_deeplabv3.html)                               | Segmentation samples for OpenVINO
    Pose             | [OpenPose](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python),  [Associative Embedding ](https://docs.openvino.ai/latest/omz_demos_human_pose_estimation_demo_python.html#doxid-omz-demos-human-pose-estimation-demo-python)        | Pose samples for OpenVINO
    Yolov4-tiny    |  [YOLOv3](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tf.html), [YOLOv4](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tf.html), [YOLOv3-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v3_tiny_tf.html), [YOLOv4-tiny](https://docs.openvino.ai/latest/omz_models_model_yolo_v4_tiny_tf.html)| Object detection samples for OpenVINO

