# Titan Dynamics Cobra VTOL

Aircraft Model: Titan Cobra VTOL

![JPG](https://github.com/robertlong13/SITL_Models/raw/titan_cobra_vtol/RealFlight/Released_Models/QuadPlanes/Titan_Cobra_VTOL/TitanCobraVTOL.jpg)

- Original Aircraft - Design: Mohammad Adib
- RealFlight 3D Model: Robert Long

|           |                                   |
|-----------|-----------------------------------|
| Wing Span | 6.6 (ft)                          |
| Length    | 3.8 (ft)                          |
| Weight    | 7.0 (lbs)                         |
| Power     | GARRT 620kV Fwd, GARRT 700kV VTOL |
| Prop      | 13x8x2 Fwd, 12x6x2 VTOL           |
| Battery   | 4 Cell - 12000 mAh - LiPoly       |


## ArduPilot Servo Functions:
| Servo   | Function                      |
|---------|-------------------------------|
| Servo1  | Aileron                       |
| Servo2  | Left A-Tail (VTailRight)      |
| Servo3  | Pusher Throttle               |
| Servo4  | Right A-Tail (VTailLeft)      |
| Servo5  | Motor1                        |
| Servo6  | Motor2                        |
| Servo7  | Motor3                        |
| Servo8  | Motor4                        |

## Parameter file/setup notes:

* AETR normal control order
* RC8(SwB) is mode: 0:QSTABLIZE, 1:QLOITER, 2:FBWA

Tested in RealFlight 9.5S using ArduPlane 4.1.1