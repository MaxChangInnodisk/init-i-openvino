# Activate Environment for Developer
1. Run container in background.
2. Provide initialize shell script.
3. Provide fast testing.

## Define Parameters
```bash
# Must modify to the correct information
BRAND=intel
VER=v0.9
ROOT=</path/to/ivit-i-${BRAND}>
```

## Run Docker
```bash
# Move back to ivit-i
cd ${ROOT}

# Run in background
docker run \
--name ivit-i-${BRAND} \
--gpus device=all -dt \
--net=host --ipc=host \
--privileged -v /dev:/dev \
-v /etc/localtime:/etc/localtime:ro \
-w /workspace \
-v `pwd`:/workspace \
-v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix:0 \
ivit-i-${BRAND}:${VER} \
"bash"
```
* Run background and tty mode `-dt`
* Capture GPU `--gpus device=all`
* Allow Network connect `--net=host --ipc=host`
* Auto detected USB device ( Cam ) `--privileged -v /dev:/dev`
* Update local time `-v /etc/localtime:/etc/localtime:ro`
* Setup workspace `-w /workspace`
* Mount Repository `-v `pwd`:/workspace`
* Allow Display `-v /tmp/.x11-unix:/tmp/.x11-unix:rw -e DISPLAY=unix:0`

## Initialize Default Samples
```bash
docker exec -it ivit-i-${BRAND} ./init_samples.sh
```

## Attach Container
```bash
docker exec -it ivit-i-${BRAND} bash
```

## Run Web API
```bash
docker exec -it ivit-i-${BRAND} ./exec_web_api.sh
```

## Fast Testing ( Not unit test )
Please check the [documentation](../test/README.md)