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
        sudo ./docker/run.sh -n -c

        # if you need to initialize samples
        ./init_samples.sh

        # if you need to launch web api
        ./exec_web_api.sh
        ```

    * Run docker container step by step for developer

        Here is the [documentation](docs/activate_env_for_developer.md) explaining the workflow of `run docker container`.

# Run Sample
We use `task.json` to configure each AI tasks and using `<model>.json` to configure each AI models, check [ task configuration ](./docs/task_configuration.md) and [model configuration](./docs/model_configuration.md) to get more detail.

1. Enter docker container
    ```bash
    sudo ./docker/run.sh -c -n
    ```
2. Download model and meta data.
    ```bash
    echo \
    """
    List Tasks
        1  classification-sample
        2  object-detection-sample
        3  parking-lot-detect
        4  traffic-flow-detect
        5  wrong-side-detect
        6  yolov4-tiny-sample
    """

    TASK=classification-sample
    ./task/${TASK}/download_model.sh
    ./task/${TASK}/download_data.sh
    ```
3. Run demo script with GUI.
    ``` bash
    python3 demo.py -c task/${TASK}/task.json
    ```
4. CLI mode - without GUI, only console output
    ```bash
    python3 demo.py -c task/${TASK}/task.json -s
    ```
5. RTSP mode
    ```bash
    # rtsp://localhost:8554/mystream
    python3 demo.py -c task/${TASK}/task.json -r
    ```
6. Custom RTSP
    ```bash
    # rtsp://localhost:8554/test
    python3 demo.py -c task/${TASK}/task.json -r \
    --name /test
    ```
7. Usage
    ```bash
    python3 demo.py --help
    
    """
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
    """
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
    # Define Task
    TASK=classification-sample
    # Initialize
    ivit-launcher --task ${TASK}
    # Initialize and Run
    ivit-launcher --task ${TASK} --demo 
    # Initialize and Run with RTSP
    ivit-launcher --task ${TASK} --demo --rtsp
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

# Credit
* Using [aler9/rtsp-simple-server](https://github.com/aler9/rtsp-simple-server) to handle RTSP stream.
* Conver RTSP to WebRTC by using [deepch/RTSPtoWeb](https://github.com/deepch/RTSPtoWeb).