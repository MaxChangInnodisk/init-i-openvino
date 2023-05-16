# iVIT Source Sample
iVIT Source Module will create a thread to keeping update the lastest frame and support [ `Image`, `DirImage`, `Video`, `RTSP`, `UsbCam` ] with the same usage and inferface.

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
    cd /workspace/samples/ivit_source_sample
    
    # Download File
    chmod u+x ./*.sh && ./download_data.sh        
    ```
* Setting Varaible
    ```bash
    EXEC_PY="python3 ./ivit-source-usage.py"

    ROOT=/workspace
    INPUT=${ROOT}/data/4-corner-downtown.mp4
    ```
* Run Sample: Enable CV Window and RTSP Stream
    
    ```bash
    ${EXEC_PY} -i ${INPUT}  # Press Q or Esc to leave
    ```

## Usage

* Image
    ```bash
    # Basic
    ${EXEC_PY} -i path/to/image/file
    
    # Resize
    ${EXEC_PY} -i path/to/image/file -s 640x480
    ```

* Video
    ```bash
    # Basic
    ${EXEC_PY} -i path/to/video/file
    
    # Resize
    ${EXEC_PY} -i path/to/video/file -s 640x480
    ```

* RTSP
    ```bash
    # Basic
    ${EXEC_PY} -i ${rtsp_url}
    
    # Resize
    ${EXEC_PY} -i ${rtsp_url} -s 640x480
    ```

* USB Camera
    The camera mount at /dev and the name will be `/dev/video{N}`, `N` will be an integer 0, 1, 2, 3, 4
    ```bash
    # Basic
    ${EXEC_PY} -i /dev/video0
    
    # Resize
    ${EXEC_PY} -i /dev/video0 -s 640x480

    # Set FPS
    ${EXEC_PY} -i /dev/video0 -s 1920x1080 -f 30
    ```