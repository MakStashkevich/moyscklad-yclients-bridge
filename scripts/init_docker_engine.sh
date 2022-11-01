#!/bin/bash

if [ -x "$(command -v docker)" ]; then
  echo 'Error: docker is installed.' >&2
  exit 1
fi

echo "### Uninstall older versions ..."
sudo apt-get remove docker docker-engine docker.io containerd runc -y
echo

echo "### Update apt packages ..."
sudo apt-get update -y
echo

echo "### Install needed packages ..."
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release -y
echo

echo "### Add Docker’s official GPG key ..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo

echo "### Set up the repository ..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
echo

echo "### Install Docker Engine ..."
sudo apt-get update -y
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y
echo