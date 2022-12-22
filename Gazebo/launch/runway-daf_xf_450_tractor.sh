#!/bin/bash

# Kill all SITL binaries when exiting
trap "killall -9 ardurover" SIGINT SIGTERM EXIT

# assume we start the script from the root directory
ROOTDIR=$ARDUPILOT_HOME
ROVER=$ROOTDIR/build/sitl/bin/ardurover

# edit the location of the SITL_Models directory if different
SITL_MODELS_DIR="$ARDUPILOT_HOME/../simulation/SITL_Models"

# build binary if not present
[ -x "$ROVER" ] || {
    ./waf configure --board sitl --debug
    ./waf plane rover
}

#--------------------------------------------------------------------
# Truck - DAF XF 450 Tractor

mkdir -p sitl/tractor/scripts

# copy the mixer script to sitl/tractor/scripts
cp -f "$SITL_MODELS_DIR/Gazebo/scripts/daf_xf_450_tractor_mixer.lua" sitl/tractor/scripts

TRACTOR_DEFAULTS="$SITL_MODELS_DIR/Gazebo/config/daf_xf_450_tractor.param"

(cd sitl/tractor && $ROVER -S --model JSON --speedup 1 --slave 0 --instance 0 --sysid 1 --defaults $TRACTOR_DEFAULTS) &

wait
