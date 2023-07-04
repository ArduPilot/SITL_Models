# X-UAV Mini Talon V-Tail

Model for the X-UAV Mini Talon V-Tail plane for use with ArduPilot.

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
gz sim -v4 -r vtail_runway.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v ArduPlane -f JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/mini_talon_vtail.param --console --map
```

## Specifications

- wingspan: 1300 mm
- length: 830 mm
- wing area: 30 dm^2
- flying weight: 1.0 - 2.0 kg

- 3s 11.1V
  - 10x6 prop
- 4s 14.8V
  - 9x5 prop
  - 3536 930kV motor
  - 40A ESC  

## General

- Mark Qvale's [X-UAV Mini Talon Build Compilation](http://www.itsqv.com/QVM/index.php?title=X-UAV_Mini_Talon_Build_Compilation#Introduction).

## Credits

- Original Mini Talon X-UAV CAD model by Alessandro Bacchini,
retrieved from GrabCAD 04 July 2023.
  - https://grabcad.com/alessandro.bacchini-2
  - https://grabcad.com/library/mini-talon-x-uav-1

- PropDrive 3536 motor model by Seth Schaffer, retrieved from GrabCAD 04 July 2023.
  - https://grabcad.com/seth.schaffer-1
  - https://grabcad.com/library/configurable-propdrive-v2-brushless-motor-with-mount-plate-solidworks-2019-1
