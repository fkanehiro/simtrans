#!/bin/sh

set -e

export ORBgiopMaxMsgSize=2097152000

CMD="simtrans -v"

JVRC_MODEL="jvrcmodels"

$CMD -i $JVRC_MODEL/JVRC-1/main.wrl -o /tmp/jvrc-1.world

for f in `ls $JVRC_MODEL/tasks/*/*.wrl`; do
    $CMD -i $f -o /tmp/tmp.world
done
