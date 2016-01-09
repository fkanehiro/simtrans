#!/bin/sh

set -e

export ORBgiopMaxMsgSize=2097152000

CMD="simtrans -v"

OPENHRP_MODEL="`pkg-config openhrp3.1 --variable=prefix`/share/OpenHRP-3.1/sample/model"

# fetch the drc_practice_* models from gazebo model database
#python -m simtrans.gzfetch -f tests/models.txt

# convert from urdf to wrl
rosrun xacro xacro.py `rospack find atlas_description`/robots/atlas_v3.urdf.xacro > /tmp/atlas.urdf
$CMD -i /tmp/atlas.urdf -o /tmp/atlas.wrl

rosrun xacro xacro.py `rospack find pr2_description`/robots/pr2.urdf.xacro > /tmp/pr2.urdf
$CMD -i /tmp/pr2.urdf -o /tmp/pr2.wrl

$CMD -i `rospack find ur_description`/urdf/ur10_robot.urdf -o /tmp/ur10.wrl

$CMD -i `rospack find baxter_description`/urdf/baxter.urdf -o /tmp/baxter.wrl

#$CMD -i `rospack find nao_description`/urdf/naoV50_generated_urdf/nao.urdf -o /tmp/nao.wrl

# convert from sdf to wrl
for i in `cat tests/models.txt`; do
    if pkg-config "sdformat >= 1.5"; then
        $CMD -i model://$i/model.sdf -o /tmp/$i.wrl
    else
        $CMD -i model://$i/model-1_4.sdf -o /tmp/$i.wrl
    fi
done

# convert from wrl to sdf
if [ -d "$HOME/.gazebo/models" ]; then
    mkdir -p $HOME/.gazebo/models
fi
if [ -f $HOME/HRP-4C/HRP4Cmain.wrl ]; then
    $CMD -i $HOME/HRP-4C/HRP4Cmain.wrl -o $HOME/.gazebo/models/hrp4c.world
fi
$CMD -i $OPENHRP_MODEL/PA10/pa10.main.wrl -o $HOME/.gazebo/models/pa10.world
$CMD -i $OPENHRP_MODEL/closed-link-sample.wrl -o $HOME/.gazebo/models/closed-link-sample.world
$CMD -i $OPENHRP_MODEL/house/house.main.wrl -o $HOME/.gazebo/models/house.world

# this specific case should return error
set +e
$CMD -i $OPENHRP_MODEL/crawler.wrl -o $HOME/.gazebo/models/crawler.world
set -e

$CMD -i $OPENHRP_MODEL/simple_vehicle_with_camera.wrl -o $HOME/.gazebo/models/simple_vehicle_with_camera.world
$CMD -i $OPENHRP_MODEL/simple_vehicle_with_rangesensor.wrl -o $HOME/.gazebo/models/simple_vehicle_with_rangesensor.world
