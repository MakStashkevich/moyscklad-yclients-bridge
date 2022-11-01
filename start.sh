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
echo "Run bridge ..."
sudo docker run -p 3000:3000 --rm bridge