# Wild Thumper 6WD skid-steer rover

A model for a Wild Thumper 6WD skid-steer rover.

![wildthumper_5](https://user-images.githubusercontent.com/24916364/144286154-231ac9b3-e54b-489f-b35e-bc2adb4b1aa0.png)

## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

### `wildthumper`

A Wild Thumper 6WD skid-steer rover.

#### Run Gazebo

```bash
gz sim -v4 -r wildthumper_runway.sdf
```

#### Run ArduPilot SITL

The model can be run with the default `rover-skid` SITL parameters.

```bash
sim_vehicle.py -v Rover -f rover-skid --model JSON  --console --map
```

## Credits

- The model visuals are based on the [Wild Thumper 6DW Chassis](https://grabcad.com/library/wild-thumper-6wd-chassis-1) published by [Pamir](https://grabcad.com/pamir-2)
