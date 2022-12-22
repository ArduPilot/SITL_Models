#!/bin/bash

# Kill all SITL binaries when exiting
trap "killall -9 arduplane" SIGINT SIGTERM EXIT

# assume we start the script from the root directory
ROOTDIR=$ARDUPILOT_HOME
PLANE=$ROOTDIR/build/sitl/bin/arduplane

# edit the location of the SITL_Models directory if different
SITL_MODELS_DIR="$ARDUPILOT_HOME/../simulation/SITL_Models"

# build binary if not present
[ -x "$PLANE" ] || {
    ./waf configure --board sitl --debug
    ./waf plane
}

#--------------------------------------------------------------------
# Alti Transition QuadPlane

mkdir -p sitl/alti_transition_quad

PLANE_DEFAULTS="$SITL_MODELS_DIR/Gazebo/config/alti_transition_quad.param"

(cd sitl/alti_transition_quad && $PLANE -S --model JSON --speedup 1 --slave 0 --instance 0 --sysid 1 --defaults $PLANE_DEFAULTS) &

wait

