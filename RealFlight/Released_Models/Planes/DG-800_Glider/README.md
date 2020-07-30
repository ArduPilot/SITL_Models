# DG-800 Glider

Aircraft Model: DG-800-A

![JPG](https://github.com/ArduPilot/SITL_Models/raw/master/RealFlight/Released_Models/Planes/DG-800_Glider/DG-800-A-G4.png)

Original Aircraft - Design: DG Flugzeugbau GmbH

3D - Model: maxkop

Physical Aircraft Model: maxkop, opjose

* Wing Span....... 13.12 (ft)
* Length............5.12 (ft)
* Weight............10.35 (lbs)
* Power............. Kontronik Fun 600-18 (12 V)
* Prop.............. Standard Folding Prop
* Battery.......... 12 Cell - 2100 mAh - Li - Poly


## ArduPilot Servo Functions:
* Servo1		passthru RC7 for Motor Deploy
* Servo2		Elevator
* Servo3		Throttle
* Servo4		Rudder
* Servo5		Left inner dspoiler (flap)
* Servo6		Left outer dspoiler (aileron)
* Servo7		Right inner dspoiler (flap)
* Servo8		Right outer dspoiler (aileron)
* Servo9		Landing Gear Retract

Note: the glider will apply wheel brake gradually increasing with nose down from mid elevator stick

## Parameter file/setup notes:

* AETR normal control order, full span aileron control
* RC5(swC) is flaps, full throw progressive crow
* RC6(swD) is landing gear, automatic altitude control enabled
* RC7(swA) is arm/disarm and motor deploy/retract
* RC8(SwB) is mode: MANUAL,FBWA,CRUISE

tested in RealFlight9 using ArduPlane 4.10dev in Sim_vehicle.py
