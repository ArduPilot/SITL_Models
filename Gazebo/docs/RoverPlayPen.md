# Rover Playpen

A model for a rover environment containing a variety of obstacles.

![rover_playpen_1_small](https://user-images.githubusercontent.com/24916364/144513412-1b0661f1-fdf8-4aed-a745-e8bb73ffca91.jpg)

The rover playpen model is a composite model that includes a number of other assets. Many are available from the [Gazebo Fuel](https://app.gazebosim.org/fuel/models) online collection of models. Unfortunately some of the online models are not rendering correctly and in those cases replacement versions derived from the originals have been included in this PR. They include:

- [construction_barrel](https://app.gazebosim.org/OpenRobotics/fuel/models/Construction%20Barrel)
- [construction_cone](https://app.gazebosim.org/OpenRobotics/fuel/models/Construction%20Cone)
- [dumpster](https://app.gazebosim.org/OpenRobotics/fuel/models/Dumpster)
- [fire_hydrant](https://app.gazebosim.org/OpenRobotics/fuel/models/Fire%20hydrant)

## Usage

The model may be included in a world sdf file using the `<include>` element:

```xml
<include>
  <uri>model://rover_playpen</uri>
</include>
```

An example world containing a wild thumper rover is provided as an example:

```bash
gz sim -v4 -r wildthumper_playpen.sdf
```

For details on controlling the wild thumper rover with SITL see: [Wild Thumper 6WD](./WildThumper.md).
