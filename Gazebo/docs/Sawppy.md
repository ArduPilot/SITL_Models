# Sawppy Rover

This is a Gazebo model of [Roger Chen's Sawppy Rover](https://github.com/Roger-random/Sawppy_Rover) with Ardupilot integration.

![sawppy-pivot-1](https://user-images.githubusercontent.com/24916364/210653579-e635ffc2-2962-4221-83a8-9622915a4121.png)

## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

### Install Lua scripts

The model requires a custom mixer for the drive motors and steering.
This is implemented using a Lua script `sawppy_motor_mixer.lua` available
in the `scripts` directory. SITL will need to be configured to use scripting:
see the Ardupilot documentation [Lua Scripts](https://ardupilot.org/rover/docs/common-lua-scripts.html?highlight=lua#lua-scripts) for more detail.


### Start Gazebo

```bash
gz sim -v4 sawppy_playpen.sdf
```

### Start SITL

```bash
sim_vehicle.py -v Rover --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/sawppy.param --console --map
```

### Configure parameters

Enable Lua scripting by setting `SCR_ENABLE = 1`, refresh parameters and reboot. 

A full parameter set for the rover is saved in `config/sawppy.param`.
The key parameters are:

**Scripting**

```bash
# Enable scripting and you may need to increase the memory available
SCR_ENABLE       1
SCR_HEAP_SIZE    65536
```

**Servos**

```bash
# The first 10 servos are controlled by the Lua script
SERVO1_FUNCTION  94
SERVO1_MAX       2000
SERVO1_MIN       1000
SERVO1_TRIM      1500
SERVO2_FUNCTION  95
SERVO2_MAX       2000
SERVO2_MIN       1000
SERVO2_TRIM      1500
SERVO3_FUNCTION  96
SERVO3_MAX       2000
SERVO3_MIN       1000
SERVO3_TRIM      1500
SERVO4_FUNCTION  97
SERVO4_MAX       2000
SERVO4_MIN       1000
SERVO4_TRIM      1500
SERVO5_FUNCTION  98
SERVO5_MAX       2000
SERVO5_MIN       1000
SERVO5_TRIM      1500
SERVO6_FUNCTION  99
SERVO6_MAX       2000
SERVO6_MIN       1000
SERVO6_TRIM      1500
SERVO7_FUNCTION  100
SERVO7_MAX       2000
SERVO7_MIN       1000
SERVO7_TRIM      1500
SERVO8_FUNCTION  101
SERVO8_MAX       2000
SERVO8_MIN       1000
SERVO8_TRIM      1500
SERVO9_FUNCTION  102
SERVO9_MAX       2000
SERVO9_MIN       1000
SERVO9_TRIM      1500
SERVO10_FUNCTION 103
SERVO10_MAX      2000
SERVO10_MIN      1000
SERVO10_TRIM     1500

# Servos 11 and 12 are not used but are set to Throttle Left and Throttle Right
# to indicate to Ardupilot the vehicle can skid-steer. This enables pivot turns
# in Guided and Auto modes.
SERVO11_FUNCTION 73
SERVO11_MAX      2000
SERVO11_MIN      1000
SERVO11_TRIM     1500
SERVO12_FUNCTION 74
SERVO12_MAX      2000
SERVO12_MIN      1000
SERVO12_TRIM     1500
```

**RC**

```bash
RC1_MAX          2000
RC1_MIN          1000
RC1_TRIM         1500
RC3_MAX          2000
RC3_MIN          1000
RC3_TRIM         1500
```

**Tuning**

```bash
# Do not disarm with rudder 
ARMING_RUDDER    1

# Speed control - the maximum vehicle speed is approx 0.38 m/s
ATC_SPEED_P      0.100000
CRUISE_SPEED     0.270000
CRUISE_THROTTLE  70
MOT_SPD_SCA_BASE 0.000000

# Steering control
ACRO_TURN_RATE   90.000000
ATC_STR_ANG_P    3.000000
ATC_STR_RAT_D    0.010000
ATC_STR_RAT_FF   1.500000
ATC_STR_RAT_I    0.100000
ATC_STR_RAT_MAX  90.000000
ATC_STR_RAT_P    0.500000
GCS_PID_MASK     1

# Navigation L1 control 
NAVL1_DAMPING    1.000000
NAVL1_PERIOD     10.000000

# Waypoints and pivot turns
WP_OVERSHOOT     0.500000
WP_PIVOT_ANGLE   90
WP_PIVOT_RATE    80
WP_RADIUS        0.500000
WP_SPEED         0.270000
```

## Credits

- Roger Chen, https://github.com/Roger-random/Sawppy_Rover.
- ROS / Gazebo11 model: https://github.com/srmainwaring/curio.


## Appendix A: Migration guide

Gazebo Garden is captures most of the features available in Gazebo11,
however some gaps remain and the treatment of kinematic loops in Gazebo Garden
is different to the earlier version. The Swappy rover has a kinematic loop
arising from the differential brace connecting the left and right rocker-bogie
suspension assemblies.

In this version we have not closed the loop and have fixed the rocker joints
to prevent the body from grounding. The full suspension will be restored in
an update. The steering and wheels are fully functional.

### Kinematic loops in SDF

Figure: kinematic tree for the rover and the loop
induced by the differential brace coupling the rocker assemblies.


```bash
# kinematic chain
base_link
├── diff_brace_link
├── laser
├── left_rocker_link # fix joint until kinematic loops supported 
│   ├── front_left_steer_link
│   │   └── front_left_wheel_link
│   └── left_bogie_link
│       ├── back_left_steer_link
│       │   └── back_left_wheel_link
│       └── mid_left_wheel_link
└── right_rocker_link # fix joint until kinematic loops supported
    ├── front_right_steer_link
    │   └── front_right_wheel_link
    └── right_bogie_link
        ├── back_right_steer_link
        │   └── back_right_wheel_link
        └── mid_right_wheel_link

# kinematic loop - requires upstream change to Gazebo
base_link
├── diff_brace_link
│   ├── left_turnbuckle_link
│   └── right_turnbuckle_link
├── left_rocker_link
│   └── left_turnbuckle_link
└── right_rocker_link
    └── right_turnbuckle_link
```

### Colours for Gazebo Sim

Material scripts are discontinued in Gazebo Garden. The vehicle uses the
following plain colours until full PBS materials have been prepared.

```bash
# dark grey
<ambient>0.175 0.175 0.175 1</ambient>
<diffuse>0.175 0.175 0.175 1</diffuse>
<specular>0.175 0.175 0.175 1</specular>

# orange
<ambient>1 0.5088 0.0468 1</ambient>
<diffuse>1 0.5088 0.0468 1</diffuse>
<specular>0.5 0.5 0.5 1</specular>

# lidar - flat black
<ambient>0.05 0.05 0.05 1</ambient>
<diffuse>0.05 0.05 0.05 1</diffuse>
<specular>0.001 0.001 0.001 1</specular>

# wheels - ultramarine blue
<ambient>0.001 0.005 0.2 1</ambient>
<diffuse>0.001 0.005 0.2 1</diffuse>
<specular>0.01 0.01 0.01 1</specular>
```

