# Quadruped rover

The controller for this model is the result of Ashvath's project [GSoC 2020: Walking Robot Support For Ardupilot](https://discuss.ardupilot.org/t/gsoc-2020-walking-robot-support-for-ardupilot/57080).

![quadruped_stand_1](https://user-images.githubusercontent.com/24916364/144449710-5bab34b4-dabf-410f-b276-d290ddbb54b2.gif)

## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

#### Run Gazebo

```bash
gz sim -v4 -r quadruped_runway.sdf
```

#### Run ArduPilot SITL

This model requires a custom controller which is implemented in the ArduPilot Lua script [`quadruped.lua`](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/examples/quadruped.lua). There is a copy of this script in `SITL_Models/Gazebo/config/scripts` for convenience.

Set up the rover and SITL following the ArduPilot wiki instructions for [Walking Robots](https://ardupilot.org/rover/docs/walking-robots.html).

Copy the Lua script `quadruped.lua` to the `scripts` folder for SITL (this is usually `$ARDUPILOT_HOME/scripts`).

The parameters set `SCR_ENABLE = 1` and you will need to reboot the autopilot after the initial start to retrieve the full set of scripting parameters. You may also need to increase the `SCR_HEAP_SIZE`.

```bash
sim_vehicle.py -v Rover --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/quadruped.param --console --map
```

#### Controls

Manual control in MAVLink:

```bash
# stand up from rest position
MANUAL> arm throttle
# rotate counter clockwise
MANUAL> rc 1 1000
# rotate clockwise
MANUAL> rc 1 1000
# lean right
MANUAL> rc 2 1000
# lean left
MANUAL> rc 2 2000
# walk backward
MANUAL> rc 3 1000
# walk forward
MANUAL> rc 3 2000
# lean forward
MANUAL> rc 4 1000
# lean backwards
MANUAL> rc 4 2000
# return to rest position
MANUAL> disarm
``` 

## Dimensions

- height: 53.23 mm
- coxa_axis_width: 101.42 mm
- coxa_axis_length: 177.03 mm
- coxa_axis_to_femur_axis: 30.0 mm
- femur_axis_to_tibia_axis: 76.17 mm
- tibia_axis_to_foot: 122.0 mm

## Credits

### Hexapod CAD model

- Author: [Tim Mills](https://grabcad.com/tim.mills-1)
- Model: [Hexapod Robot](https://grabcad.com/library/hexapod-robot-1)
