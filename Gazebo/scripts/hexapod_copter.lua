-- Lua "motor driver" for a six legged walking / flying robot
--
-- Adapted from https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_Scripting/examples/quadruped.lua

--[[
  AutoPilot servo connections:
  
  Motors 1 - 6
  SERVO1:  Motor1: mid right cw
  SERVO2:  Motor2: mid left ccw
  SERVO3:  Motor3: front left cw
  SERVO4:  Motor4: back right ccw
  SERVO5:  Motor5: front right ccw
  SERVO6:  Motor6: back left cw

  Leg joints 1 - 18
  SERVO7:  Script1:  front right coxa (hip) servo
  SERVO8:  Script2:  front right femur (thigh) servo
  SERVO9:  Script3:  front right tibia (shin) servo
  SERVO10: Script4:  front left coxa (hip) servo
  SERVO11: Script5:  front left femur (thigh) servo
  SERVO12: Script6:  front left tibia (shin) servo
  SERVO13: Script7:  back left coxa (hip) servo
  SERVO14: Script8:  back left femur (thigh) servo
  SERVO15: Script9:  back left tibia (shin) servo
  SERVO16: Script10: back right coxa (hip) servo
  SERVO17: Script11: back right femur (thigh) servo
  SERVO18: Script12: back right tibia (shin) servo
  NOT ACTUATED       mid left coxa (hip) servo
  SERVO19: Script13: mid left femur (thigh) servo
  SERVO20: Script14: mid left tibia (shin) servo
  NOT ACTUATED       mid right coxa (hip) servo
  SERVO21: Script15: mid right femur (thigh) servo
  SERVO22: Script16: mid right tibia (shin) servo

CAUTION: This script should only be used with ArduPilot firmware
]]

--[[
  Converting from AP_MotorsMatrix:

  Take as an example the Hexa X motor matrix set up in
  AP_MotorsMatrix::setup_hexa_matrix MOTOR_FRAME_TYPE_X

  {   90, AP_MOTORS_MATRIX_YAW_FACTOR_CW,   2 },
  {  -90, AP_MOTORS_MATRIX_YAW_FACTOR_CCW,  5 },
  {  -30, AP_MOTORS_MATRIX_YAW_FACTOR_CW,   6 },
  {  150, AP_MOTORS_MATRIX_YAW_FACTOR_CCW,  3 },
  {   30, AP_MOTORS_MATRIX_YAW_FACTOR_CCW,  1 },
  { -150, AP_MOTORS_MATRIX_YAW_FACTOR_CW,   4 },

  - Each row corresponds to a motor, listed in order of motor number.
  - First column is the angle subtended by the motor from the
    vehicle x-axis (forward).
  - Second column is the yaw_factor: CCW = 1, CW = -1.
  - Third column is the motor test order
  - Fourth (optional) column is the thrust factor 
  - roll_factor  = sin(-angle_rad)
  - pitch_factor = cos(-angle_rad)

  ]]

-- FRAME_CLASS 15 (Scripting Matrix)

-- 1. Hexa X
-- MotorsMatrix:add_motor_raw(0, -1,     0,           -1,  2)
-- MotorsMatrix:add_motor_raw(1,  1,     0,            1,  5)
-- MotorsMatrix:add_motor_raw(2,  0.5,   0.86602540,  -1,  6)
-- MotorsMatrix:add_motor_raw(3, -0.5,  -0.86602540,   1,  3)
-- MotorsMatrix:add_motor_raw(4, -0.5,   0.86602540,   1,  1)
-- MotorsMatrix:add_motor_raw(5,  0.5,  -0.86602540,  -1,  4)

-- assert(MotorsMatrix:init(6), "Failed to init MotorsMatrix")
-- motors:set_frame_string("Hexapod Copter")

-- FRAME_CLASS 17 (Dynamic Scripting Matrix)
Motors_dynamic:add_motor(0, 2)
Motors_dynamic:add_motor(1, 5)
Motors_dynamic:add_motor(2, 6)
Motors_dynamic:add_motor(3, 3)
Motors_dynamic:add_motor(4, 1)
Motors_dynamic:add_motor(5, 4)

local factors = motor_factor_table()

-- Roll for motors 1 - 6
factors:roll(0, -1.0)
factors:roll(1,  1.0)
factors:roll(2,  0.5)
factors:roll(3, -0.5)
factors:roll(4, -0.5)
factors:roll(5,  0.5)

-- pitch for motors 1 - 6
factors:pitch(0,  0)
factors:pitch(1,  0)
factors:pitch(2,  0.86602540)
factors:pitch(3, -0.86602540)
factors:pitch(4,  0.86602540)
factors:pitch(5, -0.86602540)

-- yaw for motors 1 - 6
factors:yaw(0, -1)
factors:yaw(1,  1)
factors:yaw(2, -1)
factors:yaw(3,  1)
factors:yaw(4,  1)
factors:yaw(5, -1)

-- throttle for motors 1 - 6
factors:throttle(0,  1.0)
factors:throttle(1,  1.0)
factors:throttle(2,  1.0)
factors:throttle(3,  1.0)
factors:throttle(4,  1.0)
factors:throttle(5,  1.0)

-- must load factors before init
Motors_dynamic:load_factors(factors)

-- expecting 6 motors
assert(Motors_dynamic:init(6), "Failed to init MotorsDynamic")

-- at any time we can then re-load new factors
Motors_dynamic:load_factors(factors)

motors:set_frame_string("Hexapod Copter")

-- if doing changes in flight it is a good idea to us pcall to protect
-- the script from crashing see 'protected_call.lua' example

-- servo angles when robot is disarmed and resting body on the ground
local disarmed_leg_angles = {
  45, -90, 40, -- front right leg (coxa, femur, tibia)
 -45, -90, 40, -- front left leg (coxa, femur, tibia)
 -45, -90, 40, -- back left leg (coxa, femur, tibia)
  45, -90, 40, -- back right leg (coxa, femur, tibia)
      -90, 40, -- mid left leg (femur, tibia)
      -90, 40  -- mid right leg (femur, tibia)
}

local armed_leg_angles = {
 0, -25, -60, -- front right leg (coxa, femur, tibia)
 0, -25, -60, -- front left leg (coxa, femur, tibia)
 0, -25, -60, -- back left leg (coxa, femur, tibia)
 0, -25, -60,  -- back right leg (coxa, femur, tibia)
    -25, -60, -- mid left leg (femur, tibia)
    -25, -60  -- mid right leg (femur, tibia)
}

local leg_servo_direction = {
  1, -1,  1, -- front right leg (coxa, femur, tibia)
  1,  1, -1, -- front left leg (coxa, femur, tibia)
 -1, -1,  1, -- back left leg (coxa, femur, tibia)
 -1,  1, -1, -- back right leg (coxa, femur, tibia)
      1, -1, -- mid left leg (femur, tibia)
      1, -1  -- mid right leg (femur, tibia)
}

function update()

  -- update motor mixer
  Motors_dynamic:load_factors(factors)

  -- update legs
  local leg_angles
  if arming:is_armed() then
    leg_angles = armed_leg_angles
  else
    leg_angles = disarmed_leg_angles
  end

  for i = 1, 16 do
    -- normalised angle is in [-1, 1]
    local norm_angle = leg_angles[i] * leg_servo_direction[i] / 90
    -- ensure pwm is in [1000, 2000]
    local pwm = math.floor(norm_angle * 500 + 1500)

    -- Q: is index for assigned channel or absolute?
    -- A: it is absolute (so offset for the 6 motors)
    SRV_Channels:set_output_pwm_chan_timeout(i + 5, pwm, 1000)
  end

  return update, 10
end

-- turn off rudder based arming/disarming
param:set_and_save('ARMING_RUDDER', 0)
gcs:send_text(0, "Hexapod Copter")
return update()
