#!/bin/bash

# Kill all SITL binaries when exiting
trap "killall -9 arducopter" SIGINT SIGTERM EXIT

# assume we start the script from the root directory
ROOTDIR=$ARDUPILOT_HOME
COPTER=$ROOTDIR/build/sitl/bin/arducopter

# edit the location of the SITL_Models directory if different
SITL_MODELS_DIR="$ARDUPILOT_HOME/../simulation/SITL_Models"

# drones will be located here
HOMELAT=38.161479
HOMELONG=-122.454630
HOMEALT=488.0

# build binary if not present
[ -x "$COPTER" ] || {
    ./waf configure --board sitl --debug
    ./waf copter
}

#--------------------------------------------------------------------
# Iris

mkdir -p sitl/iris_sonoma

COPTER_DEFAULTS="$ROOTDIR/Tools/autotest/default_params/copter.parm,$ROOTDIR/Tools/autotest/default_params/gazebo-iris.parm"

(cd sitl/iris_sonoma && $COPTER -S --model JSON --home=$HOMELAT,$HOMELONG,$HOMEALT,-55 --speedup 1 --slave 0 --instance 0 --sysid 1 --defaults $COPTER_DEFAULTS) &

wait

