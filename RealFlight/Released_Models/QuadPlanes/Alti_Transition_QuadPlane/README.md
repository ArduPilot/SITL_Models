# Alti Transition QuadPlane


![JPG](https://github.com/ArduPilot/SITL_Models/raw/master/RealFlight/Released_Models/Planes/Alti_Transition_QuadPlane/AltiTransition.png)

Original Aircraft - Design: ??
Modifications by Andrew Tridgell and Brandon MacDougall

* Wing Span....... 9.3 (ft)
* Length............5.12 (ft)
* Weight............37.7 (lbs)
* Power............. 5x Tmotor U7 420KV
* Prop.............. 18x12x3 Forward, 18x6x2 VTOL
* Battery.......... 8 Cell - 9000 mAh - Li - Poly


## ArduPilot Servo Functions:
* Servo1		Aileron
* Servo2		Elevator
* Servo3		Throttle
* Servo4                Rudder (not used except for arm/disarm)
* Servo5		Motor1
* Servo6		Motor2
* Servo7		Motor3
* Servo8		Motor4

## Parameter file/setup notes:

* AETR normal control order, full span aileron control
* RC8(SwB) is mode: FBWA,QSTABLIZE,QHOVER

tested in RealFlight9 using ArduPlane 4.10dev in Sim_vehicle.py
