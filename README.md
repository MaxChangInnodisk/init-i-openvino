![COVER](assets/images/iVIT-I-Logo-B.png)

# iVIT-I-INTEL
iVIT-I is an AI inference tool which could support multiple AI framework and this repository is for intel platform.

* [Requirements](#requirements)
* [Getting Start](#getting-start)
* [Compare with OpenVINO](#compare-with-openvino)

# Requirements
* [Docker 20.10 + ](https://docs.docker.com/engine/install/ubuntu/)
* [Docker-Compose v2.15.1 ](https://docs.docker.com/compose/install/linux/#install-using-the-repository)
    * you can check via `docker compose version`

# Getting Start
1. Clone Repository
    
    * Donwload Target Version
        ```bash
        git clone -b r1.1 https://github.com/InnoIPA/ivit-i-intel.git && cd ivit-i-intel
        ```

2. Run iVIT-I Docker Container

    * Run CLI container
        ```bash
        sudo ./docker/run.sh

        "USAGE: ./docker/run.sh -h" << EOF
        Run the iVIT-I environment.

        Syntax: scriptTemplate [-bqh]
        options:
        b               run in background
        q               Qucik launch iVIT-I
        h               help.
        >>
        ```

3. Run Samples

    * [Source Sample](samples/classification_sample/README.md)
    * [Displayer Sample](samples/ivit_displayer_sample/README.md)
    * [Classification Sample](samples/classification_sample/README.md)
    * [Object Detection Sample](samples/object_detection_sample/README.md)
    * [iDevice Sample](samples/ivit_device_sample/README.md)

# Python Library Documentation
[iVIT-I-Intel API Docs](https://github.com/InnoIPA/ivit-i-intel.io)

# Compare with OpenVINO

* iVIT ( r1.1 )
    1. A Simplier Way to use.
        1. Initialize iVIT Model.
        2. Initialize Source Object.
        3. Initialize Displayer Object.
        4. Do Inference
            * One line to inference
            * Draw result if result is not empty
            * Displayer with one line
        5. Finish inference only need to do release()
    2. Only ~60 lines could finish the AI Inference

* OpenVINO ( 2022.3 )
    1. A Complicate workflow, hard to use
        1. Initailize Model Adaptor. 
        2. Initialize Model Wrapper.
        3. Initialize AsyncPipeline.
        4. Initialize Image Capture Module.
        5. Do Inference.
            * Check the exception of the async_pipeline
            * Check result via frame index from async_pipeline
                * Draw result if result is not empty, and skip to the next iteration.
                * if not, next to step C
            * Submit frame and frame index into async_pipline
        6. Finish inference have to wait async_pipeline clear the buffer.
    2. Too many code have to setup
        * The main() workflow has about 100+ lines ( [classification_vino_demo.py](./samples/classification_sample/classification_vino_demo.py) )
