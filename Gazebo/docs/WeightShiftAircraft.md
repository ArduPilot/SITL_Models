# Weight-Shift Aircraft

Model for the [Romaeris](https://www.romaeris.com/) unmanned weight-shift control (uWSC) electric aircraft.
 
![uWSC_motion](https://github.com/NDevDrone/SITL_Models/assets/50757802/9aee8639-d1a1-4807-8118-03f4ccdcc9ff)

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
gz sim -v4 -r wsc_aircraft_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/wsc_aircraft.param --console --map
```

It may be required to set the pitch joint axis to an adjusted trim value near the mid-point, in order to arm the aircraft controller. For example, using the default mavproxy input, the 2nd rc channel can be set to a roughly midpoint state by entering:
```
rc 2 1552
```

The provided parameter configuration modifies the default plane parameter set to provide automatic flight control mode for the weight-shift aircraft model, as follows:

```bash
SERVO1_FUNCTION = 4
SERVO1_REVERSED = 0
SERVO2_FUNCTION = 19
SERVO2_REVERSED = 0
SERVO4_FUNCTION = 21
SERVO4_REVERSED = 0
SERVO5_FUNCTION = 78
SERVO5_REVERSED = 1
SERVO6_FUNCTION = 77
SERVO6_REVERSED = 1
SERVO10_FUNCTION = 74
SERVO10_TRIM = 1100
SERVO11_FUNCTION = 73
SERVO11_TRIM = 1100
INS_ACCOFFS_X   0.001
INS_ACCOFFS_Y   0.001
INS_ACCOFFS_Z   0.001
INS_ACCSCAL_X   1.001
INS_ACCSCAL_Y   1.001
INS_ACCSCAL_Z   1.001
INS_ACC2OFFS_X   0.001
INS_ACC2OFFS_Y   0.001
INS_ACC2OFFS_Z   0.001
INS_ACC2SCAL_X   1.001
INS_ACC2SCAL_Y   1.001
INS_ACC2SCAL_Z   1.001
INS_GYR_CAL      0
ARSPD_TYPE 0
BATT_MONITOR    4
RUDD_DT_GAIN = 1
LIM_PITCH_MAX = 2700
LIM_PITCH_MIN = -1000
LIM_ROLL_CD 2000
MIS_TOTAL = 413
NAVL1_DAMPING = 0.85
NAVL1_PERIOD = 50
RLL_RATE_P = 0.5
SIM_SAFETY_STATE = 2
WP_RADIUS = 10
```

![uWSC_gasplume](https://github.com/NDevDrone/SITL_Models/assets/50757802/b2636499-a5b3-4e01-985c-76852ab118a0)

## Included camera gimbal demo
The model includes a 3-axis camera gimbal implementation that makes use of the Ardupilot [3-axis gimbal controls](https://ardupilot.org/copter/docs/common-mount-targeting.html).

![GimbalDemo](https://github.com/NDevDrone/SITL_Models/assets/50757802/9844586d-614e-4028-973f-9e12f8dd68c5)

## Notes

- The uWSC model flies by the principles of weight-shift flight control inherent to hang-gliders and ultralight/microlight air-trikes.
- The uWSC model is composed of two bodies; the flying wing, and an attached mass that hangs beneath the wing including batteries and propulsion.
- The flying wing is a rigid approximation of a typical flexible hang-glider wing, with four surfaces sections that mimic the aerodynamic characteristics of washout and wing twist. 
- The servo input of conventional control surfaces is replaced by the actuation of a two revolute axis (2R) joint called the 'hang-block', that shifts position of the weight beneath the wing.
- The flying wing attitude is controlled by default plane PID controllers for pitch and roll, where control input induces weight-shift of the net center of gravity.
- The model's axis is rotated 90 degrees around the z-axis, positioning y as the forward direction instead of x. This is accommodated by adjustments in both the IMU sensor pose and ArduPilot plugin poses to rectify the orientation discrepancy. This will be corrected for in a future PR when time permits.

## Modelling and comparison to real weight-shift flight

Information on the aircraft model's body dynamics, aerodynamics, and comparison of the model fidelity with real weight-shift flight data can be found in the forthcoming conference paper titled "uWSC Aircraft Simulator: A Gazebo-based model for uncrewed weight-shift control aircraft flight simulation" that may be cited as follows:

- Mailhot, N., de Jesus Krings, T., Tuta Navajas, G., Zhou, B., & Spinello, D. (2023). uWSC Aircraft Simulator: A Gazebo-based model for uncrewed weight-shift control aircraft flight simulation. 2023 IEEE Symposium on Robotics and Sensors Environments (ROSE), Tokyo, Japan.

```
@INPROCEEDINGS{uWSCAircraftSimulator2023,
	title = {{uWSC} {Aircraft} {Simulator}: {A} {Gazebo}-based model for uncrewed weight-shift control aircraft flight simulation},
	booktitle = {2023 IEEE Symposium on Robotics and Sensors Environments (ROSE)},
	author = {Nathaniel, Mailhot and Teresa, de Jesus Krings and Gilmar, Tuta Navajas and Boyan, Zhou and Davide, Spinello},
	month = nov,
	year = {2023},
}
```

## Credits

- The model is based on the [Romaeris Corporations'](https://www.romaeris.com/) unmanned weight-shift aircraft prototype called the "Romaeris eUAV".
- Contributors: Nathaniel Mailhot, Trevor Phair, Boyan Zhou, Teresa de Jesus Krings, and Gilmar Tuta Navajas. 
- Please feel free to e-mail nmailhot@uottawa.ca for any questions pertaining to this work.
