#!/bin/bash

# Kill all SITL binaries when exiting
trap "killall -9 ardurover" SIGINT SIGTERM EXIT

# assume we start the script from the root directory
ROOTDIR=$ARDUPILOT_HOME
ROVER=$ROOTDIR/build/sitl/bin/ardurover

# edit the location of the SITL_Models directory if different
SITL_MODELS_DIR="$ARDUPILOT_HOME/../simulation/SITL_Models"

# drones will be located here
HOMELAT=38.161479
HOMELONG=-122.454630
HOMEALT=488.0

# build binary if not present
[ -x "$ROVER" ] || {
    ./waf configure --board sitl --debug
    ./waf rover
}

#--------------------------------------------------------------------
# WildThumper

mkdir -p sitl/wildthumper_sonoma

ROVER_DEFAULTS="$ROOTDIR/Tools/autotest/default_params/rover.parm,$ROOTDIR/Tools/autotest/default_params/rover-skid.parm"

(cd sitl/wildthumper_sonoma && $ROVER -S --model JSON --home=$HOMELAT,$HOMELONG,$HOMEALT,-55 --speedup 1 --slave 0 --instance 0 --sysid 1 --defaults $ROVER_DEFAULTS) &

wait

