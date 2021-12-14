-- This script loads the 6DoF mixer matrix for a 6 motor frame
-- https://youtu.be/QUDhnYvH66k

Motors_6DoF:add_motor(0,  0.02,   0.5, -0.04, 0.84, 0.54,   0,    true, 1)
Motors_6DoF:add_motor(1, -0.45, -0.23, -0.04, 0.84, -0.27,  0.47, true, 2)
Motors_6DoF:add_motor(2,  0.45, -0.23,  0.04, 0.84, -0.27, -0.47, true, 3)
Motors_6DoF:add_motor(3, -0.19, -0.23, -0.4,  0,     0.87, -0.5,  true, 4)
Motors_6DoF:add_motor(4, -0.29, -0.04,  0.4,  0,     0,    -1,    true, 5)
Motors_6DoF:add_motor(5,  0.11, -0.28,  0.4,  0,     0.87,  0.5,  true, 6)

assert(Motors_6DoF:init(6),'unable to setup 6 motors')
