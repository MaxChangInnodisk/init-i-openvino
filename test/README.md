# Fast Testing
Fast Testing for `Intel` platform:
1. Download data and model from Google Drive.
2. Run demo script if you give the argument `-r`, you could use `-r` to disable the cv window.

* Run the testing script
    ```bash
    ./docker/run.sh -c
    <script.sh> < -r > < -s > < -h >
    ```
    |   name    |   descr                   
    |   ----    |   -----
    |   `-r`    |   run the demo script and display the result
    |   `-s`    |   server mode, only print the result not dispay
    |   `-h`    |   show help information

* Run script outside the docker container

    ```bash
    docker start ivit-i-intel
    docker exec -it ivit-i-intel <script.sh> < -r > < -s > < -h >
    ```

* Examples
    * classification.sh
        ```bash
        docker exec -it ivit-i-intel ./test/classification.sh -r
        ```
    * objectdetection_sample.sh
        ```bash
        docker exec -it ivit-i-intel ./test/objectdetection_sample.sh -r
        ```
    * segmentation_sample.sh
        ```bash
        docker exec -it ivit-i-intel ./test/segmentation_sample.sh -r
        ```
    * humanpose_sample_ae.sh
        ```bash
        docker exec -it ivit-i-intel ./test/humanpose_sample_ae.sh -r
        ```
    * retail_product_detection.sh
        ```bash
        docker exec -it ivit-i-intel ./test/retail_product_detection.sh -r
        ```
