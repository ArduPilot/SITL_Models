# Convergence Tilt Tri QuadPlane

Aircraft Model: Derivative of RealFlight Mini-Convergence

![JPG](https://github.com/ArduPilot/SITL_Models/raw/master/RealFlight/Released_Models/QuadPlanes/Convergence_Tilt_Tri_QuadPlane/Convergence.png)

Model modifications by : Mark Whitehorn and Henry Wurzburg


* Wing Span....... 30 (in)
* Length............27.8 (in)
* Weight............2.12 (lbs)
* Power............. 2x E-Flite 2210-1459kv, E-flite 2730-1550kv rear
* Prop.............. APC 7x6
* Battery.......... 3 Cell - 2200 mAh - Li - Poly


## ArduPilot Servo Functions:
* Servo1		Left elevon
* Servo2		Right elevon
* Servo3		Left Motor tilt
* Servo4		Right Motor tilt
* Servo5		Motor 1
* Servo6		Motor 2
* Servo7		Motor 4


## Parameter file/setup notes:

* AETR normal control order, full span aileron control
* RC8(SwB) is mode: MANUAL,FBWA,CRUISE


tested in RealFlight9 using ArduPlane 4.10dev in Sim_vehicle.py
