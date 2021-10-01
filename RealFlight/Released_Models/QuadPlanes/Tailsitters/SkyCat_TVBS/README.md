# SkyCat Twin Motor Vectored Belly Sitter (TVBS) QuadPlane

Aircraft Model: Original by Otto (lorbass)

![JPG](https://github.com/ArduPilot/SITL_Models/raw/master/RealFlight/Released_Models/QuadPlanes/Tailsitters/SkyCat_TVBS/SkyCat.jpg)

Model modifications by : Mark Whitehorn and Andrew Tridgell


* Wing Span....... 55 (in)
* Length............60 (in)
* Weight............5.8 (lbs)
* Power............. 2x MT4108 370KV
* Prop.............. APC Sport 10x5.5
* Battery.......... 8 Cell - 4000mAh - Li - Poly


## ArduPilot Servo Functions:
* Servo1		Left elevon
* Servo2		Right elevon
* Servo3		Left Motor tilt
* Servo4		Right Motor tilt
* Servo5		Left Motor
* Servo6		Right Motor



## Parameter file/setup notes:

* AETR normal control order, full span aileron control
* RC8(SwB) is mode: QSTABILIZE,QLOITER,FBWA


tested in RealFlight9 using ArduPlane 4.10dev in Sim_vehicle.py
