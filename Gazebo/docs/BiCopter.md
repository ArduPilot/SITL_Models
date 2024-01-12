# BiCopter

A model for a BiCopter developed here: [GreenPine-CK/bicopter_simulation](https://github.com/GreenPine-CK/bicopter_simulation)


![gz_bicopter_ardupilot_auto](https://github.com/ArduPilot/SITL_Models/assets/24916364/0f41a75e-f356-4812-9407-9c19ec6f76a4)

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
gz sim -v4 -r bicopter_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduCopter --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/bicopter.param --console --map
```

### Notes

In MAVProxy the flight modes for the BiCopter appear as Plane modes, so you need to enter the Plane mode with the same index as the Copter mode you want:

For example the Copter simulation starts in STABILIZE mode which appears as MANUAL when running the bicopter.

*Table: Map flight modes from Plane to Copter*

| # | Copter | Plane |
| --- | --- | --- |
|  0 | STABILIZE | MANUAL |
|  1 | ACRO | CIRCLE |
|  2 | ALT_HOLD |STABILIZE |
|  3 | AUTO | TRAINING |
|  4 | GUIDED | ACRO |
|  5 | LOITER | FBWA |
|  6 | RTL | FBWB |
|  7 | CIRCLE | CRUISE |
|  8 |  | AUTOTUNE |
|  9 | LAND |  |
| 10 |  |  |
| 11 | DRIFT | RTL |
| 12 |  |  |
| 13 | SPORT | TAKEOFF |

### Credits

- Lee ChangKeun, [GreenPine-CK/bicopter_simulation](https://github.com/GreenPine-CK/bicopter_simulation)
- [Валентин Дмитриев](https://grabcad.com/-5981), [Propeller Phantom 3 9450](https://grabcad.com/library/propeller-phantom-3-9450-1)
- [Vincent Shi](https://grabcad.com/vincent.shi-1), [DJI 2312(E305) Motor](https://grabcad.com/library/dji-2312-e305-motor-1)
- [PedroC](https://grabcad.com/pedroc-1), [Hitech Servo HS-422](https://grabcad.com/library/hitech-servo-hs-422-1)
