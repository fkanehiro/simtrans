#!/bin/bash

set -x

# install ros
export ROS_DISTRO=hydro
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu precise main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -

# install drcsim
sudo sh -c 'echo "deb http://packages.osrfoundation.org/drc/ubuntu precise main" > /etc/apt/sources.list.d/drc-latest.list'
wget http://packages.osrfoundation.org/drc.key -O - | sudo apt-key add -

# register hrg daily ppa
sudo add-apt-repository -y ppa:hrg/daily

# install required packages
sudo apt-get update -qq
sudo apt-get install -qq -y python-pip graphviz openhrp openrtm-aist-python python-omniorb omniidl-python omniorb-idl omniidl python-numpy ros-$ROS_DISTRO-xacro ros-$ROS_DISTRO-pr2-description ros-$ROS_DISTRO-ur-description ros-$ROS_DISTRO-baxter-description drcsim

# install python libraries
sudo pip install --upgrade pip
sudo pip install -r requirements.txt
sudo pip install -r requirements-dev.txt

set +x
source /opt/ros/$ROS_DISTRO/setup.bash
source /usr/share/drcsim/setup.sh
set -x

source ./convertall.sh

cd doc
source ./build.sh
