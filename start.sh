#!/usr/bin/env bash

if ! [ -x "$(command -v docker)" ]; then
  echo "Not found Docker to start ..."
  sudo ./scripts/init_docker_engine.sh
fi
echo "Remove old bridge container ..."
sudo docker rm -f bridge_container
echo
echo "Remove old bridge image ..."
sudo docker rmi makstashkevich/moyscklad-yclients-bridge:latest
echo
echo "Build bridge image ..."
sudo docker build -t makstashkevich/moyscklad-yclients-bridge:latest .
echo
echo "Read .env file"
if [ -f .env ]
then
    set -a; source .env; set +a
fi
echo
echo "Prepare session file ..."
sudo touch "$(pwd)"/bridge.session
echo
echo "Run bridge on port ${WEBSERVER_PORT:-80}..."
sudo docker run \
    --name=bridge_container \
    --restart=always \
    --mount type=bind,source="$(pwd)"/bridge.session,target=/bridge/bridge.session \
    -p "${WEBSERVER_PORT:-80}:${WEBSERVER_PORT:-80}" makstashkevich/moyscklad-yclients-bridge:latest