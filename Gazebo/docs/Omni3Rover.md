# Omni3 Mecanum Rover

An Omni rover with 3 [Mecanum wheels](https://en.wikipedia.org/wiki/Mecanum_wheel).

![omni3rover](https://github.com/user-attachments/assets/53d5d0bf-e4e3-4f03-a50a-4004a9865309)


## Usage

#### Run Gazebo

Edit the `omnirover_playpen.sdf` to include the `omni3rover` model.

```bash
gz sim -v4 -r omnirover_playpen.sdf
```

#### Run ArduPilot SITL

```bash
sim_vehicle.py -v Rover --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/omni3rover.param --console --map
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
