ROOT=$(dirname `realpath $0`)
cd $ROOT

echo "Build the docker image."
docker build -t ivinno-vino .