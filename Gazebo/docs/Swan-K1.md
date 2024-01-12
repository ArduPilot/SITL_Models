# Swan-K1 Copter Tailsitter Quadplane

Model for the Swan-K1 copter tailsitter quadplane for use with ArduPilot.
It is derived from the [version prepared for RealFlight](https://github.com/ArduPilot/SITL_Models/tree/master/RealFlight/Released_Models/QuadPlanes/Tailsitters/Swan_K-1_HWing).


![swan-k1-hwing-flying](https://user-images.githubusercontent.com/24916364/210408630-01e5f56d-57ba-430e-b04d-62cb8d232527.png)


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
gz sim -v4 -r swan_k1_hwing_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/swan_k1_hwing.param --console --map
```
