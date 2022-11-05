#!/usr/bin/env bash

echo "Remove old bridge image ..."
sudo docker rmi makstashkevich/moyscklad-yclients-bridge:latest
echo
echo "Build bridge image ..."
sudo docker build -t makstashkevich/moyscklad-yclients-bridge:latest .
echo
echo "Push bridge image to Docker ..."
sudo docker push makstashkevich/moyscklad-yclients-bridge:latest