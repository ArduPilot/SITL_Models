# ARACE Griffin Tilt-Rotor QuadPlane


![JPG](https://github.com/ArduPilot/SITL_Models/raw/master/RealFlight/Released_Models/QuadPlanes/Griffin/Griffin.png)

Original Aircraft - Design: Andrew Tridgell and Brandon MacDougall
Graphics Updates: Adrain Hinst


* Wing Span....... 74.2 (in)
* Length............46.4 (in)
* Weight............37.7 (lbs)
* Power............. Custom, 16lb thrust at 23.6V/88.7A
* Prop.............. 14x8.5
* Battery.......... 6S4P Cell - 22000 mAh - Li - Poly


## ArduPilot Servo Functions:
* Servo1		Aileron
* Servo2		Elevator
* Servo3        Camera Pan
* Servo4        Rudder
* Servo5		Motor1
* Servo6		Motor2
* Servo7		Motor3
* Servo8		Motor4
* Servo9        Tilt Motor Left
* Servo10       Tilt Motor Right
* Servo11       Camera Tilt
* Servo12       Camera Zoom

## Parameter file/setup notes:

* AETR normal control order, full span aileron control
* RC8(SwB) is mode: FBWA,QSTABLIZE,QHOVER
* Camera Gimbal uses Realflight stabilization and ArduPilot RC Targetting by default
* Pan = RC6
* Tilt = RC7

tested in RealFlight9 using ArduPlane 4.10dev in Sim_vehicle.py
