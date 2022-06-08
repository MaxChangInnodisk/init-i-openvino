# iNIT-I For Intel
iNIT-I for Intel CPU, GPU

## Pre-requirements
* Install [docker](https://max-c.notion.site/Install-Docker-9a0927c9b8aa4455b66548843246152f)

## Prepare Environment
1. Clone Repository and submodule
    > submodule is web api which will be place in [init_i/web](./init_i/web)
    ```bash
    # clone repo and submodule
    git clone --recurse-submodules https://github.com/MaxChangInnodisk/init-i-intel.git
    
    # check if submodule is downloaded
    ls ./init_i/web
    ai  api  app.py  __init__.py  utils

    # if not exist then download submodule again
    # $ git submodule init && git submodule update
    ```

2. Build the docker images
    ```bash
    ./docker/build.sh
    ```
    > about 12 min.
3. Run the docker container with web api
    ```bash
    ./docker/run.sh -f intel -v v0.1 -wm
    # enter container without web api
    ./docker/run.sh -f intel -v v0.1 -m
    ```