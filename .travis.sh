#!/bin/bash

set -x

sudo apt-get update -qq
sudo apt-get install -qq -y python-pip graphviz
sudo pip install -r requirements.txt

cd doc
source ./build.sh
