# Alti Transition QuadPlane


![JPG](https://github.com/ArduPilot/SITL_Models/raw/master/RealFlight/Released_Models/QuadPlanes/Alti_Transition_QuadPlane/AltiTransition.png)

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

## Alti with FPV Gimbal

A second model is provided that includes a simple 2 axis servo gimbal on the nose, typical for FPV use. It has no effect on aerodynamics and is intended to allow testing of the ArduPilot Mount Functions in a restricted range mount (+20/-90 Tilt and -90/+180 Pan) and can be used with the three position switches available with the Interlink controller. Its view is available under Gimbal Camera selection.

* Servo9        Pan  
* Servo10       Tilt

Manual control is via the CH6/7 switches on the left side of the InterLink controller.
Parameters

## Alti with Unrestricted Gimbal

A third model provides a 3-axis gimbal with wide movement range as would be desirable to test POI tracking ans stabilization with ArduPilot for a servo controlled gimbal.

* Servo9        Pan  (+/-180deg)
* Servo10       Tilt (+/-90deg)
* Servo11       Roll (+/-90deg)

Manual control is via the CH5/6/7 switches on the left side of the InterLink controller.
Note: SERVO11_MIN is set to 1500 to allow normal view with InterLink switch used for Roll, and will need to be changed if Roll stabilization is activated.
