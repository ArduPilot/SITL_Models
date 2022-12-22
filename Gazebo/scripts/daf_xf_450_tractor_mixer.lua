--[[
    Copyright (c) 2020, Rhys Mainwaring

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
--]]

--[[
    Servo mixer for DAF XF 450 Tractor Unit: car steering with
    rear wheel differential drive. The WHEEL_COORDS are particular
    to this vehicle.

    Vehicle control outputs are defined in AP_Vehicle::ControlOutput.

        CONTROL_OUTPUT_THROTTLE = 3
        CONTROL_OUTPUT_YAW = 4

    The output directed to servos using the enum defined in SRV_Channel::Aux_servo_function_t.
    For scripting the following parameters should be set:

        SERVO1_FUNCTION = 94
        SERVO2_FUNCTION = 95
        SERVO3_FUNCTION = 96
        SERVO4_FUNCTION = 97
--]]

-- control outputs
local CONTROL_OUTPUT_THROTTLE = 3
local CONTROL_OUTPUT_YAW = 4

-- servo outputs
local SERVO1_FUNCTION = 94      -- back_left_wheel_joint   (drive no steer)
local SERVO2_FUNCTION = 95      -- back_right_wheel_joint  (drive no steer)
local SERVO3_FUNCTION = 96      -- front_left_steer_joint  (steer no drive)
local SERVO4_FUNCTION = 97      -- front_right_steer_joint (steer no drive)

-- update at 50Hz
local UPDATE_PERIOD = 20

-- wheel geometry for rover (FRD), units are [m]
local WHEEL_COORDS = {}
WHEEL_COORDS[1] = { 0.0, -1.065}   -- back_left_wheel_joint
WHEEL_COORDS[2] = { 0.0,  1.065}   -- back_right_wheel_joint
WHEEL_COORDS[3] = { 3.6, -1.02}   -- front_left_steer_joint
WHEEL_COORDS[4] = { 3.6,  1.02}   -- front_right_steer_joint

local WHEEL_SEP_W = 2.13            -- rear wheel lateral separation
local WHEEL_SEP_H = 3.6             -- front to back wheel separation
local WHEEL_ANGLE_MAX_DEG = 45.0    -- steering angle limit

--[[
    Constrain a value to a range

    Parameters
    ==========
    value : float
        The value to constrain
    min_value : float
        The lower limit of the range
    max_value : float
        The upper limit of the range

    Returns
    =======
    float
        A value constrained to the range
--]]
local function constrain(value, min_value, max_value)
    return math.max(math.min(value, max_value), min_value)
end

--[[
    Scale each element of a 2d array

    Parameters
    ==========
    vector : array
        The input array
    scale : float
        A scalar value

    Returns
    =======
    array
        The scaled array
--]]
local function scale_vector2d(vector, scale)
    local vector_out = {}
    for i=1, #vector do
        vector_out[i] = {vector[i][1] * scale, vector[i][2] * scale}
    end
    return vector_out
end

--[[
    Calculate the Euclidean distance between two points

    Parameters
    ==========
    a : array
        The first point
    b : array
        The second point

    Returns
    =======
    float
        The distance (L2 norm) between the two points
--]]
local function distance_vector2d(a, b)
    local dx = b[1] - a[1]
    local dy = b[2] - a[2]
    local r = math.sqrt(dx * dx + dy * dy)
    return r
end

--[[
    Rescale the wheel coordinates by the half the mid wheel separation

    The saturation limits for steering and throttle control are calculated
    in scaled coordinates assuming a wheel separation of 2.

    Parameters
    ==========
    wheel_coords : array
        The array of wheel coordinates (x, y)
    wheel_sep_w : float
        The lateral distance between the left and right non-steering wheels

    Returns
    =======
    array
        The scaled (normalised) wheel coordinates

--]]
local function normalise_wheel_coordinates(wheel_coords, wheel_sep_w)
    return scale_vector2d(wheel_coords, 2.0 / wheel_sep_w)
end

--[[
    Calculate a wheel's distance from the instantaneous centre of curvature

    Parameters
    ==========
    icc : array
        The coordinates (x, y) of the instantaneous centre of curvature
    wheel_coords : array
        The (x, y) normalised wheel coordinates

    Returns
    =======
    float
        The distance

--]]
local function wheel_turning_radius(icc, wheel_coord)
    return distance_vector2d(icc,  wheel_coord)
end

--[[
    Rescale an array or turning radii so the maximum no greater than 1

    This function returns a normalised array of turning radii for the
    wheels. It ensures that the servo outputs are constainined to [0, 1].
    The radii are assumed positive.

    Parameters
    ==========
    r : array
        An array of turning radii (r[i] >= 0)

    Returns
    =======
    array
        The rescaled turning radii (array).
--]]
local function rescale_turning_radii(r)

    -- determine maximum
    local r_max = 0.0
    for i = 1, #r do
        if r[i] == math.huge then
            r_max = math.huge
            break
        else
            r_max = math.max(r_max, r[i])
        end
    end

    -- rescale
    local r_s = {}
    for i = 1, #r do
        if r_max == math.huge then
            r_s[i] = 1.0
        else
            r_s[i] = r[i] / r_max
        end
    end

    return r_s
end

--[[
    Calculate the wheel angle for a turn about a given ICC

    This function calculates the unconstrained steering angle for
    a wheel given and instantaneous centre of curvature (ICC). The
    output steering angle is in [-pi, pi]

    Parameters
    ==========
    icc : array
        An array (x, y) containing x and y coordinates of the ICC
    wheel_coord : array
        An array (x, y) containing x and y coordinates of a wheels axis

    Returns
    =======
    float
        The steering angle in radians. The angle is in [-pi, pi]
--]]
local function calc_wheel_angle(icc, wheel_coord)
    local dx = icc[1] - wheel_coord[1]
    local dy = icc[2] - wheel_coord[2]
    local theta = math.atan(dx, dy)
    return theta
end

--[[
    Calculate the servo outputs for a rover from steering and throttle control

    This function calculates the wheel speed and steering angle for the
    drive wheels and steering servos on a rover. The servo outputs are
    normalised to [-1, 1].

    The steering angles are constrained [-WHEEL_ANGLE_MAX_DEG, WHEEL_ANGLE_MAX_DEG].

    NB: in this version the rear drive wheels are diff-locked (i.e. both are given
    the same throttle command)

    Parameters
    ==========
    steering : float
        The normalised steering rate in [-1, 1]
    throttle : float
        The normalised throttle in [-1, 1]

    Returns
    =======
    wheels, steers : array, array
        Return the normalised servo outputs for 4 wheels and 4 steers
--]]
local function servo_outputs(steering, throttle)
    -- reverse steering when throttle reversed
    if throttle < 0  then
        steering = -steering
    end

    -- capture the sign of steering and throttle as main calc assumes steering, throttle > 0
    local steering_sign = 1
    if steering < 0 then
        steering_sign = -1
        steering = -steering
    end

    local wheels = {0.0, 0.0, 0.0, 0.0}
    local steers = {0.0, 0.0, 0.0, 0.0}

    -- instantaneous centre of curvature
    local r = {0.0, 0.0, 0.0, 0.0}

    -- calc steering
    local wheel_angle_max_rad = math.rad(WHEEL_ANGLE_MAX_DEG)
    local wheel_angle_rad = wheel_angle_max_rad * steering
    local r_p = math.huge
    if wheel_angle_rad > 0 then
        r_p = WHEEL_SEP_H / math.tan(wheel_angle_rad) + WHEEL_SEP_W * 0.5
    end
    local icc = {0.0, r_p}

    -- wheel speed and steering angles
    for i = 1, #r do

        -- calc throttle - all wheels driven at same speed
        wheels[i] = throttle
        
        -- calc steering - angles specific to each wheel
        steers[i] = calc_wheel_angle(icc, WHEEL_COORDS[i])

        -- apply steering limits
        steers[i] = constrain(steers[i], -wheel_angle_max_rad, wheel_angle_max_rad)

        -- enforce constraints
        wheels[i] = constrain(wheels[i], -1.0, 1.0)
        steers[i] = constrain(steers[i], -1.0, 1.0)
    end

    -- flip wheel speeds and steering angles and signs if steering < 0
    if steering_sign < 0 then
        for i = 1, #steers/2 do
            local tmp = wheels[2 * i - 1]
            wheels[2 * i - 1] = wheels[2 * i]
            wheels[2 * i] = tmp

            tmp = steers[2 * i - 1]
            steers[2 * i - 1] = -steers[2 * i]
            steers[2 * i] = -tmp
        end
    end

    -- debug output
    --[[
    gcs:send_text(6, string.format("STR:%.2f THR:%.2f RP:%.2f S[1]:%.2f, S[2]:%.2f S[2]:%.2f S[4]:%.2f",
        steering, throttle, r_p, math.deg(steers[1]), math.deg(steers[2]), math.deg(steers[3]), math.deg(steers[4])))
    --]]

    return wheels, steers
end

--[[
    Main update loop

    Poll the control outputs every UPDATE_PERIOD milli seconds,
    compute the servo outputs for wheels and steeing and send
    them to the servo channels.
--]]
local function update()
    -- retrieve high level steering and throttle control outputs
    local steering = vehicle:get_control_output(CONTROL_OUTPUT_YAW)
    local throttle = vehicle:get_control_output(CONTROL_OUTPUT_THROTTLE)

    -- compute servo outputs
    local wheels = {0.0, 0.0, 0.0, 0.0}
    local steers = {0.0, 0.0, 0.0, 0.0}

    wheels, steers = servo_outputs(steering, throttle)

    -- always allow steering (the back two wheels do not steer)
    SRV_Channels:set_output_norm(SERVO3_FUNCTION, steers[3])
    SRV_Channels:set_output_norm(SERVO4_FUNCTION, steers[4])

    -- wheel servos only set when armed
    if not arming:is_armed() then
        -- if not armed move throttle to mid
        SRV_Channels:set_output_norm(SERVO1_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO2_FUNCTION, 0)
    else
        SRV_Channels:set_output_norm(SERVO1_FUNCTION, wheels[1])
        SRV_Channels:set_output_norm(SERVO2_FUNCTION, wheels[2])
    end

    return update, UPDATE_PERIOD
end

gcs:send_text(6, "car_steer_mixer.lua is running")
return update(), 3000

