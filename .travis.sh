#!/bin/bash

set -x

# install ros
export ROS_DISTRO=indigo
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu trusty main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -

# install drcsim
sudo sh -c 'echo "deb http://packages.osrfoundation.org/drc/ubuntu trusty main" > /etc/apt/sources.list.d/drc-latest.list'
wget http://packages.osrfoundation.org/drc.key -O - | sudo apt-key add -

# register hrg daily ppa
sudo add-apt-repository -y ppa:hrg/daily

# install required packages
sudo apt-get update -qq
sudo apt-get install -qq -y pkg-config python-dev python-pip graphviz meshlab xvfb openhrp openrtm-aist-python python-omniorb omniidl-python omniorb-idl omniidl python-numpy ros-$ROS_DISTRO-xacro ros-$ROS_DISTRO-pr2-description ros-$ROS_DISTRO-ur-description ros-$ROS_DISTRO-baxter-description drcsim

# install python libraries
sudo pip install --upgrade pip
sudo pip install -r requirements.txt --ignore-installed
sudo pip install -r requirements-dev.txt --ignore-installed

# now installs simtrans
sudo python setup.py install

set +x
source /opt/ros/$ROS_DISTRO/setup.bash
source /usr/share/drcsim/setup.sh
set -x

python -m simtrans.gzfetch -f tests/models.txt

git clone --depth 1 https://github.com/jvrc/model.git jvrcmodels

xvfb-run python testrunner.py

xvfb-run ./convertall.sh

cd doc
source ./build.sh
