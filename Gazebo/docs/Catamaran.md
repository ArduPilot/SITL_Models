# Catamaran

Sailing Catamaran designed by Andy Little ([@kwikius](https://github.com/kwikius))

![catarmaran_rigged_3](https://github.com/ArduPilot/SITL_Models/assets/24916364/f0a65fc0-f25b-43ea-8690-f7eb979ed455)

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

#### Sail, foil, wind sensor and wind plugins

A number of additional plugins are required to support sailing vessels. These can be found at [asv_sim](https://github.com/srmainwaring/asv_sim). Installation instructions are in the repository README.

#### Run Gazebo

```bash
gz sim -v4 -r catamaran_waves.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v Rover --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/catamaran.param --console --map --custom-location='51.566151,-4.034345,10.0,-135'
```
 
#### Wave and wind settings

To run the simulation in calm seas modify the wave settings in `asv_wave_sim/gz-waves-models/world_models/waves/model.sdf`. There are two occurrences of the parameter block:

```xml
<wave>
  <!-- `fft` wave parameters -->
  <algorithm>fft</algorithm>
  <tile_size>256</tile_size>
  <cell_count>256</cell_count>
  <wind_speed>5.0</wind_speed>
  <wind_angle_deg>135</wind_angle_deg>
  <steepness>2</steepness>
</wave>
``` 
Update both blocks when making changes (one is for the physics, one for the visuals).

- Set `<wind_speed>` to 0 for calm seas.
- Set  `<cell_count>` to 4 to reduce the compute load if waves are not required.

The `catamaran_waves.sdf` world file is configured to load a wind plugin that responds to service requests to set the wind. For ease of gyro and accelerometer calibration the wind is initially set to zero. Once the vehicle is initialised and armed the wind can be set using:

```bash
gz topic -t /wind -m  gz.msgs.Vector3d -p "x:{wind_vel_x}, y:{wind_vel_y}, z:0"
```

where `{wind_vel_x}` and `{wind_vel_y}` should be replaced by the desired components of the wind velocity in `m/s`. A good choice is `"x:0, y:5, z:0"` to get the boat moving, then once out of irons switch to `"x:5.5, y:5.5, z:0"`

The [sail module](https://ardupilot.org/mavproxy/docs/modules/sail.html) in MAVProxy is useful for determining the current true and apparent wind direction.

## Links

- Discussion on the ArduPilot Discourse [Sailboat Support](https://discuss.ardupilot.org/t/sailboat-support/32060/884?u=rhys) page.
