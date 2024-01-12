# Alti Transition QuadPlane

A model for an Alti Transition QuadPlane. It is derived from the [RF version in SITL_Models](https://github.com/ArduPilot/SITL_Models/tree/master/RealFlight/Released_Models/QuadPlanes/Alti_Transition_QuadPlane).

![alti_transition_quadplane_front](https://user-images.githubusercontent.com/24916364/150612555-958a64d4-c434-4f90-94bd-678e6b6011ec.png)


## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

### Run Gazebo

```bash
gz sim -v4 -r alti_transition_runway.sdf
```

###  Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/alti_transition_quad.param --console --map
```

### Preflight checks

The parameters configure the vehicle as an H-frame as this seems to give better yaw control.

#### Motors

```bash
# front right motor (motor1) should spin clockwise
MANUAL> motortest 1 1 1005 2

# rear right motor (motor4) should spin counter-clockwise
MANUAL> motortest 2 1 1005 2

# rear left motor (motor2) should spin clockwise
MANUAL> motortest 3 1 1005 2

# front left motor (motor3) should spin counter-clockwise
MANUAL> motortest 4 1 1005 2

# pusher motor (throttle) should spin clockwise
MANUAL> arm throttle
MANUAL> rc 3 1010
```

## Notes

- The model is auto-tuned using a combination of parameters from the Skywalker X8 quadplane and the RF Alti Transition as an initial configuration.
- The CP for the main wing and CoM for the base link have been adjusted to reduce the amount of elevator required to maintain level flight (it was originally saturating), another round of tuning the model physical parameters could reduce this further (see figure below).

![alti_transition_tuning_run2](https://user-images.githubusercontent.com/24916364/150661239-14fb132c-8863-4307-8f38-216f6738786d.png)
