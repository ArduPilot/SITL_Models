# Skywalker X8 QuadPlane

Models for the Skywalker X8 in plane and quad-plane configurations for use with ArduPilot.

![skywalker_x8_quad_2](https://user-images.githubusercontent.com/24916364/142733947-1a39e963-0aea-4b1b-a57b-85455b2278fe.png)

## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

### `skywalker_x8`

An X8 configured as a delta-wing plane.

#### Run Gazebo

```bash
gz sim -v4 -r skywalker_x8_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/skywalker_x8.param --console --map
```

### `skywalker_x8_quad`

An X8 configured as a delta-wing quad plane.

#### Run Gazebo

```bash
gz sim -v4 -r skywalker_x8_quad_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/skywalker_x8_quad.param --console --map
```

### Notes

- The plane / quad-plane parameters have been [auto-tuned](https://ardupilot.org/plane/docs/automatic-tuning-with-autotune.html) for regular flight. The Q-modes are using default parameters.
- The quad plane has been set up as an H-frame as the original configuration as an X-frame had such poor yaw authority the vehicle could not be controlled when transitioning from FBWA flight back to Q modes.
- Additional yaw authority is provided by rotating the VTOL motors 3 degrees towards the centreline.

## Credits

The model is adapted from the `standard_vtol` model available from these repos:

- https://github.com/SwiftGust/ardupilot_gazebo/tree/master/models/standard_vtol
- https://github.com/PX4/PX4-SITL_gazebo/tree/master/models/standard_vtol

Textures were adapted from:

- https://github.com/ArduPilot/SITL_Models/tree/master/RealFlight/WIP/Tridge/QuadPlane/X8TiltTri
