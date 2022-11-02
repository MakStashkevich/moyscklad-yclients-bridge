#!/usr/bin/env bash

if ! [ -x "$(command -v docker)" ]; then
  echo "Not found Docker to start ..."
  sudo ./scripts/init_docker_engine.sh
fi
echo "Remove old bridge image ..."
sudo docker rmi bridge
echo
echo "Build bridge image ..."
sudo docker build -t bridge .
echo
echo "Read .env file"
if [ ! -f .env ]
then
    set -a; source .env; set +a
fi
echo "Run bridge on port ${WEBSERVER_PORT:-80}..."
sudo docker run -p "${WEBSERVER_PORT:-80}:${WEBSERVER_PORT:-80}" --rm bridge