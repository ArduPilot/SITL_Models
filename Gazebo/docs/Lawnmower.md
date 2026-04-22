# Lawnmower Rover

A model for a ride-on lawnmower with differential drive.

## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

### `lawnmower`

A ride-on lawnmower rover with differential drive and rotating cutter blades.

#### Specifications

- **Dimensions:** 1.8 m (L) × 0.65 m (W) × 0.55 m (H)
- **Mass:** 236 kg (220 kg body + 16 kg wheels)
- **Wheel diameter:** 0.44 m
- **Max speed:** 10.5 km/h
- **Drive type:** Differential (skid-steer)

#### Run Gazebo

```bash
gz sim -v4 -r lawnmower_runway.sdf
```

#### Run ArduPilot SITL

The model can be run with the default `rover-skid` SITL parameters.

```bash
sim_vehicle.py -v Rover -f rover-skid --model JSON --console --map
```

#### Controls

- **Channel 0 (SERVO1):** Left wheel (Throttle Left)
- **Channel 2 (SERVO3):** Right wheel (Throttle Right)

#### Configuration

Use the provided parameter file for optimal performance:

```bash
sim_vehicle.py -v Rover -f rover-skid --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/lawnmower.param --console --map
```

## Credits

- The model is based on the [PX4 Lawnmower Chassis](https://github.com/PX4/PX4-gazebo-models/tree/main/models/lawnmower)