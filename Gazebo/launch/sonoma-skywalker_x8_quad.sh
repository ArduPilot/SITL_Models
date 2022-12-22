#!/bin/bash

# Kill all SITL binaries when exiting
trap "killall -9 arduplane" SIGINT SIGTERM EXIT

# assume we start the script from the root directory
ROOTDIR=$ARDUPILOT_HOME
PLANE=$ROOTDIR/build/sitl/bin/arduplane

# edit the location of the SITL_Models directory if different
SITL_MODELS_DIR="$ARDUPILOT_HOME/../simulation/SITL_Models"

# drones will be located here
HOMELAT=38.161479
HOMELONG=-122.454630
HOMEALT=488.0

# build binary if not present
[ -x "$PLANE" ] || {
    ./waf configure --board sitl --debug
    ./waf plane
}

#--------------------------------------------------------------------
# Iris

mkdir -p sitl/skywalker_x8_quad_sonoma

PLANE_DEFAULTS="$SITL_MODELS_DIR/Gazebo/config/skywalker_x8_quad.param"

(cd sitl/skywalker_x8_quad_sonoma && $PLANE -S --model JSON --home=$HOMELAT,$HOMELONG,$HOMEALT,-55 --speedup 1 --slave 0 --instance 0 --sysid 1 --defaults $PLANE_DEFAULTS) &

wait

