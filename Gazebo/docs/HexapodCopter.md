# Hexapod Copter

A Gazebo model for a hexapod copter (a hexapod rover with motors on each arm).

The original quadruped version of this frame is the result of Ashvath's project [GSoC 2020: Walking Robot Support For Ardupilot](https://discuss.ardupilot.org/t/gsoc-2020-walking-robot-support-for-ardupilot/57080).


![hexapod_copter_hover](https://user-images.githubusercontent.com/24916364/225340320-9aa31fe2-4602-4036-ba6b-491f72097c01.jpg)

The frame is fully articulated. Each of the 6 legs has 3 joints, however only 16 are actuated. The middle two 'hip' joints are fixed in this example. The motor ordering and orientation is the same as a standard hexa X frame, however in this case the FRAME_CLASS 17 (Dynamic Scripting Matrix) and the motor mixing is set in the Lua script.

The legs have two positions - folded when disarmed, and unfolded when armed.

If the scripting control of the legs is disabled they may be moved using gz topic commands:

```bash
# move the mid right femur joint down from its initial position of -0.6 rad to -0.4 rad 
gz topic -t "/femur_mr_joint/cmd_pos" -m gz.msgs.Double -p "data: -0.4"
```

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
gz sim -v4 -r hexapod_copter_runway.sdf
```

#### Run ArduPilot SITL

Copy the script $HOME/SITL_Models/Gazebo/scripts/hexapod_copter.lua to the SITL scripts directory,
then start SITL:

```bash
sim_vehicle.py -v ArduCopter -f hexa --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/hexapod_copter.param --console --map
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
