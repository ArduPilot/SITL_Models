## DAF XF 450 Tractor

A Gazebo model for a [DAF XF 450 Tractor](https://www.daf.co.uk/api/feature/specsheet/open?container=e702153e-6f24-4b7c-aaa5-f75578e14f17&filename=TSGBEN016G0709AAAA202137.pdf).

https://user-images.githubusercontent.com/24916364/149665138-f921ac8d-1082-4822-a28c-d2c07f98ccaa.mov

The vehicle is configured to have car steering (i.e. different wheel angles for inner and outer front wheels) and differential drive on the rear wheels. This requires a Lua script to control the servo mix for ArduPilot which is supplied in the scripts sub-directory.   

## Usage

**Run Gazebo**

```bash
gz sim -v4 -r daf_truck_runway.sdf
```
**Run ArduPilot SITL**

Copy the script `daf_xf_450_tractor_mixer.lua` to the SITL scripts directory, then start SITL:

```bash
sim_vehicle.py -v Rover --model JSON --add-param-file=$HOME/SITL_Models/Gazebo/config/daf_xf_450_tractor.param --console --map
```

You may need to reboot the autopilot to ensure the additional scripting parameters are loaded.

## Credits

- The model visuals are based on the [Semi-Trailer with Truck ](https://grabcad.com/library/semi-trailer-with-truck-1) published by [Anirudh Bhalekar](https://grabcad.com/anirudh.bhalekar-1)

