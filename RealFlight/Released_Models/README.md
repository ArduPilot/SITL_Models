# Released Models
Models of vehicles for ArduPilot SITL in Realflight8/9

These models have been tested and conform to a set of standards to insure ease of use.
Each model has a readme.md file describing its configuration, capabilities, and sim controller mapping

Minimum requirements for inclusion:

1. Documentation:
    README.md file for model including description, model .png file,attributions, basic physical properties (size,weight,etc.), output mapping to actuators (ArduPilot currently only supports SERVO1-12 outputs to flightaxis), RC in mapping/switches (AETR is standard,mode channel should be ch8 to match Interlink controller mapping), version of RealFlight and ArduPilot tested.
2. The above documentation be included in the RealFlight RFX model's description page.
3. RealFight entire model RFX archive and ArduPilot parameter file. Parameter file should be a complete set of params for the vehicle to allow easy changes between models. Flight modes for three ch8 positions should be:


Plane   |   QuadPlane |  Copter    |   Rover  | TradHeli
-----   |  ---------  | ------     |  -----   | --------
Manual  |  QSTABILIZE | Stabilize  | Manual   |  Stabilize
FBWA    |  QLOITER    |  AltHold   | Acro     |  Loiter
Cruise  |  FBWA       |  Loiter    | RTL      |  Acro
4. The model must use the InterLink controller default mapping. Note that ArduPilot currently only supports CH1-8 on flight-axis input.

Controller | Output
---------- | ------
Aileron | Ch1
Elevator | Ch2
Throttle | Ch3
Rudder  | Ch4
SwA  | Ch7
SwB  | Ch8 (always mode)
SwC  | Ch5
SwD  | Ch6
5. The model has been verified by a third party as meeting these requirements and flying well.
