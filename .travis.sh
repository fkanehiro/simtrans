#!/bin/bash

set -x


sudo add-apt-repository -y ppa:hrg/daily
sudo apt-get update -qq
sudo apt-get install -qq -y python-pip graphviz openhrp openrtm-aist-python python-omniorb
sudo pip install -r requirements-dev.txt

cd doc
source ./build.sh
