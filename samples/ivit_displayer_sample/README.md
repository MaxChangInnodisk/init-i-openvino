# iVIT Displayer Sample
iVIT Displayer Module can displaying CV window and sending RTSP at the same time. This sample integrate with  [iVIT-I Source Module](../ivit_source_sample/README.md), please take a look first.

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
    cd /workspace/samples/ivit_displayer_sample
    
    # Download File
    chmod u+x ./*.sh && ./download_data.sh        
    ```
* Setting Varaible
    ```bash
    
    EXEC_PY="python3 ./ivit-displayer-usage.py"

    ROOT=/workspace
    INPUT=${ROOT}/data/4-corner-downtown.mp4
    ```
* Run Sample: Enable CV Window and RTSP Stream
    
    ```bash
    # Press Q, Esc to leave
    # RTSP at `rtsp://127.0.0.1:8554/ivit`

    ${EXEC_PY} -i ${INPUT} --cv --rtsp 
    ```

## Usage

* Help
    ```bash
    usage: ivit-displayer-usage.py [-h] -i INPUT [-n NAME] [-s SIZE] [-f FPS] [--cv] [--rtsp]

    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                            The input data.
    -n NAME, --name NAME  The window name and rtsp namespace.
    -s SIZE, --size SIZE  The size you want to get from source object.
    -f FPS, --fps FPS     The size you want to get from source object.
    --cv                  Display OpenCV Window
    --rtsp                Display OpenCV Window

    ```

* Only Enable CV Windwos

    ```bash
    ${EXEC_PY} -i ${INPUT} --cv     # Press Q, Esc to leave
    ```

* Only Enable RTSP Stream

    ```bash
    ${EXEC_PY} -i ${INPUT} --rtsp   # Default is rtsp://localhost:8554/ivit
    ```

## Issue

1. RTSP Started but can't capture the stream
    - Make sure the rtsp-simple-server is launched
        ```bash
        # Check the docker container
        $ sudo docker ps -a

        CONTAINER ID   IMAGE                                COMMAND                 CREATED         STATUS                     PORTS     NAMES
        8bf385f31947   maxchanginnodisk/ivit-i-intel:v1.1   "entrypoint bash"       4 seconds ago   Up 3 seconds                         ivit-i-intel-v1.1
        ecff312558b2   aler9/rtsp-simple-server             "/rtsp-simple-server"   5 seconds ago   Exited (1) 4 seconds ago             docker-rtsp-1

        ```
        
2. If RTSP Service not start, maybe is port 8554 is using.
    ```
    kill $(lsof -t -i:8554)
    ```