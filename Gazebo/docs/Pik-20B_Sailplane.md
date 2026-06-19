# Pik-20B sailplane

Model for a full size Pik-20B sailplane.

![pik_20b_sailplane_v1](https://github.com/ArduPilot/SITL_Models/assets/24916364/342ec2a4-525e-4589-8814-279cda15df5d)


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
$ gz sim -v4 -r sailplane_runway.sdf
```

#### Run ArduPilot SITL

```bash
$ sim_vehicle.py -v ArduPlane -f JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/pik_20b_sailplane.param --console --map
```

