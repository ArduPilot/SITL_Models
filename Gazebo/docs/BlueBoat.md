# BlueBoat

[Blue Robotics BlueBoat](https://bluerobotics.com/product-category/boat/) (operates as [skid steer rover](https://ardupilot.org/rover/docs/rover-motor-and-servo-configuration.html#skid-steering) in ArduPilot using
the [Boat](https://ardupilot.org/rover/docs/boat-configuration.html#boat-configuration) `FRAME_CLASS`).
 
![blueboat_gz](https://github.com/ArduPilot/SITL_Models/assets/24916364/11213e94-9e58-45eb-8181-1cec6c64ee19)

## Usage

Gazebo and the plugins should be installed as per the [ArduPilot Gazebo Plugin](https://github.com/ArduPilot/ardupilot_gazebo) instructions.

Update the `GZ_SIM_RESOURCE_PATH` to include these models:

```bash
export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:\
$HOME/SITL_Models/Gazebo/models:\
$HOME/SITL_Models/Gazebo/worlds
```

#### Waves model

The model is configured to work with the hydrodynamics plugin from the [wave sim](https://github.com/srmainwaring/asv_wave_sim) package. Follow the package instructions to set up the marine simulation.

The model may be included in the [`waves.sdf`](https://github.com/srmainwaring/asv_wave_sim/blob/master/gz-waves-models/worlds/waves.sdf) world by adding the element:

```xml
<include>
  <pose degrees="true">0 0 0 0 0 90</pose>
  <uri>model://blueboat</uri>
</include>
```

#### Run Gazebo

```bash
gz sim -v4 -r waves.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v Rover -f rover-skid --model JSON  --console --map --custom-location='51.566151,-4.034345,10.0,-135'
```

The default skid steer rover parameters give a workable simulation with minor modifications:

```bash
CRUISE_SPEED      2.0
CRUISE_THROTTLE   50.0
FRAME_CLASS       2.0
WP_SPEED          2.0
```

![blueboat_gz_clip](https://github.com/ArduPilot/SITL_Models/assets/24916364/c2fb9c7f-bde2-46ba-9a3a-e4e641163b67)

## Notes

The hull form used to model the hydrodynamics is an approximation. It has slightly more volume in the keel fins and aft, which requires the centre of mass in the simulation to be moved aft for level trim. The hull collision meshes used to calculate the buoyancy and hydrodynamics could be further refined to more closely model the true hull form at a later stage if needed.

<img width="1312" alt="blueboat_gz_waterline" src="https://github.com/ArduPilot/SITL_Models/assets/24916364/4e1f9a2d-85d3-4ab7-91a7-6606a4b11727">


## Credits

Original 3D Models retrieved from BlueRobotics: [BLUEBOAT_120_BR-101447_RevA_PUB](https://cad.bluerobotics.com/BLUEBOAT_120_BR-101447_RevA_PUB.zip)  
