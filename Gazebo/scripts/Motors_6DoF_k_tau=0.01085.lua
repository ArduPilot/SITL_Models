-- This script loads the 6DoF mixer matrix for a 6 motor frame
-- https://youtu.be/QUDhnYvH66k

Motors_6DoF:add_motor(0,  0.003817,  0.500000, -0.036946,  0.800918,  0.561626,  0.024300, true, 1)
Motors_6DoF:add_motor(1, -0.452580, -0.277281,  0.020489,  0.730687, -0.234176,  0.493098, true, 2)
Motors_6DoF:add_motor(2,  0.448763, -0.222719,  0.016457,  0.767900, -0.327450, -0.517399, true, 3)
Motors_6DoF:add_motor(3, -0.171323, -0.230612, -0.398279,  0.001580,  0.883490, -0.463366, true, 4)
Motors_6DoF:add_motor(4, -0.255615, -0.030959,  0.417607, -0.035365,  0.009037, -1.000000, true, 5)
Motors_6DoF:add_motor(5,  0.167723, -0.241059,  0.433131, -0.034046,  0.813576,  0.440443, true, 6)

assert(Motors_6DoF:init(6),'unable to setup 6 motors')
