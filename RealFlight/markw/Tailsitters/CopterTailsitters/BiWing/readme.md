These models are quad X-frame copter tailsitters contributed by Otto Kueng.

The copter tailsitter quad-X frame class and type are specified by:
Q_FRAME_CLASS = 1
Q_FRAME_TYPE = 1
and
Q_TAILSIT_MOTMX = 15 to enable all 4 motors in FW modes
or
Q_TAILSIT_MOTMX = 5 to enable only the bottom wing motors
or
Q_TAILSIT_MOTMX = 10 to enable only the top wing motors


PR https://github.com/ArduPilot/ardupilot/pull/12869 is required for multicopter frame yaw control (body-frame roll) to work correctly when hovering.

Model BiWing_JWL065_EA.RFX has airfoil and CG similar to the actual flying model by Pierre Losa.

Model BiWing_MH106_EA.RFX has a symmetrical airfoil with CG moved further back for comparison of aerodynamic characteristics. 