# SkyCat TVBS QuadPlane

A model for a SkyCat TVBS QuadPlane. It is derived from the [RF version in SITL_Models]( https://github.com/ArduPilot/SITL_Models/tree/master/RealFlight/Released_Models/QuadPlanes/Tailsitters/SkyCat_TVBS)

![skycat_tvbs_1](https://user-images.githubusercontent.com/24916364/145025150-4e7e48e1-3e83-4c83-be7b-b944db1d9152.png)

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
gz sim -v4 -r skycat_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/skycat_tvbs.param --console --map
```

### Testing

The tailsitter has a basic tune so that it is operational, but it could be much improved. The aerodynamics model (the lift-drag system plugin) does not account for prop-wash or similar effects, so the simulation is illustrative rather than realistic.  

Takeoff

https://user-images.githubusercontent.com/24916364/145026559-15f581f1-0b90-46b1-97e7-1ffaca7d852a.mov

Transition from QSTABILIZE to FBWA

https://user-images.githubusercontent.com/24916364/145026785-b89bea76-f2de-4daa-a3f6-0a8bad1534e1.mov

Transition from FBWA to QLAND

https://user-images.githubusercontent.com/24916364/145026794-d66d89d0-ab62-4ecd-a8de-c139e5afd63c.mov
