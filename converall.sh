#!/bin/sh

CMD="python -m simtrans.cli"
OPENHRP_MODEL="/usr/local/share/OpenHRP-3.1/sample/model"

# convert from urdf to wrl
$CMD -i package://atlas_description/urdf/atlas_v3.urdf -o /tmp/atlas.wrl
$CMD -i package://ur_description/urdf/ur5_robot.urdf -o /tmp/ur5.wrl
$CMD -i package://ur_description/urdf/ur10_robot.urdf -o /tmp/ur10.wrl

# convert from sdf to wrl
$CMD -i model://pr2 -o /tmp/pr2.wrl

# convert from wrl to sdf
$CMD -i $OPENHRP_MODEL/PA10/pa10.main.wrl -o $HOME/.gazebo/models/pa10.world
$CMD -i $OPENHRP_MODEL/closed-link-sample.wrl -o $HOME/.gazebo/models/closed-link-sample.world
$CMD -i $OPENHRP_MODEL/house/house.main.wrl -o $HOME/.gazebo/models/house.world
