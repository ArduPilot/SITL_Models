# OmniX Mecanum Rover

An Omni rover with 4 [Mecanum wheels](https://en.wikipedia.org/wiki/Mecanum_wheel).

![omni4rover](https://github.com/user-attachments/assets/00775e2c-a651-4902-9493-c272687152c0)


## Usage

#### Run Gazebo

```bash
gz sim -v4 -r omnirover_playpen.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v Rover --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/omni4rover.param --console --map
```

Once armed, set the mode to `MANUAL` and control as follows:

| Channel | Low | High |
| --- | --- | --- |
`rc 1` | yaw left | yaw right |
`rc 2` | not assigned | |
`rc 3` | move back | move forward |
`rc 4` | move left | move right |


## Links

- [Rover wiki: Motor and Servo Connections: Omni-Vehicles](https://ardupilot.org/rover/docs/rover-motor-and-servo-connections.html#omni-vehicles)
