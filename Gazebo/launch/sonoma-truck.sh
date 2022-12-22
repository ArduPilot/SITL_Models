#!/bin/bash

# Truck - Quadplane Landing Example
#
# 

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
# Truck - tractor

mkdir -p sitl/tractor/scripts

# copy the mixer script to sitl/tractor/scripts
cp -f "$SITL_MODELS_DIR/Gazebo/scripts/daf_xf_450_tractor_mixer.lua" sitl/tractor/scripts

TRACTOR_DEFAULTS="$SITL_MODELS_DIR/Gazebo/config/daf_xf_450_tractor.param"

# additional parameter file for the tractor unit
cat <<EOF > sitl/tractor/leader.param
SYSID_THISMAV 1
AUTO_OPTIONS 7
EOF

(cd sitl/tractor && $ROVER -S --model JSON --home=$HOMELAT,$HOMELONG,$HOMEALT,-55 --speedup 1 --slave 0 --instance 0 --sysid 1 --defaults $TRACTOR_DEFAULTS,leader.param) &


#--------------------------------------------------------------------
# Truck - trailer

# mkdir -p sitl/trailer

# TRAILER_DEFAULTS="$ROOTDIR/Tools/autotest/default_params/rover.parm"

# # additional parameter file for the trailer unit
# cat <<EOF > sitl/trailer/leader.param
# SYSID_THISMAV 2
# AUTO_OPTIONS 7
# EOF

# (cd sitl/trailer && $ROVER -S --model JSON --home=$HOMELAT,$HOMELONG,$HOMEALT,0 --speedup 1 --slave 0 --instance 1 --sysid 2 --defaults $TRAILER_DEFAULTS,leader.param) &

wait

