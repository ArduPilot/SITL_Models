-- This script loads the 6DoF mixer matrix for a 6 motor frame
-- https://youtu.be/QUDhnYvH66k

Motors_6DoF:add_motor(0, -0.000000,  0.500000, -0.000000,  0.787038,  0.587785, -0.000000, true, 1)
Motors_6DoF:add_motor(1, -0.433013, -0.250000,  0.000000,  0.787038, -0.293893,  0.509037, true, 2)
Motors_6DoF:add_motor(2,  0.433013, -0.250000,  0.000000,  0.787038, -0.293893, -0.509037, true, 3)
Motors_6DoF:add_motor(3, -0.136160, -0.235836, -0.407943,  0.000000,  0.866025, -0.500000, true, 4)
Motors_6DoF:add_motor(4, -0.272320,  0.000000,  0.407943, -0.000000, -0.000000, -1.000000, true, 5)
Motors_6DoF:add_motor(5,  0.136160, -0.235836,  0.407943, -0.000000,  0.866025,  0.500000, true, 6)

assert(Motors_6DoF:init(6),'unable to setup 6 motors')
