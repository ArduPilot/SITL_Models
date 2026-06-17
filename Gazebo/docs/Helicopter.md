# Helicopter

A model for a traditional Helicopter.

_TODO: Add image here_

- ## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

### Run Gazebo

```bash
gz sim -v4 -r helicopter_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduCopter --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/heli_ddfp_cw.param --console --map
```


### Credits

- [PB/Two blade small helicopter rotor head](https://grabcad.com/library/two-blade-small-helicopter-rotor-head-2)
