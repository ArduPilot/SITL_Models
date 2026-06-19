# Omnicopter

Model for the 6DoF omnicopter for use with ArduPilot.
It is derived from the [version prepared for RealFlight](https://github.com/ArduPilot/SITL_Models/tree/master/RealFlight/WIP/iampete/Lynchpin).


![omnicopter_2](https://user-images.githubusercontent.com/24916364/146563555-57b4afc7-dec5-4720-9446-d1dafb82aeca.png)

![omnicopter_1_viz](https://user-images.githubusercontent.com/24916364/146563631-592c6459-d72c-45a7-86c6-09da64a96e22.png)

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
gz sim -v4 -r omnicopter_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduCopter -f JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/omnicopter.param --console --map
```
