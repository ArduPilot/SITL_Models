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
    Motor mixer for a Sawppy rover

    Vehicle control outputs are defined in AP_Vehicle::ControlOutput.

        CONTROL_OUTPUT_THROTTLE = 3
        CONTROL_OUTPUT_YAW = 4

    The output directed to servos using the enum defined in SRV_Channel::Aux_servo_function_t.
    For scripting the following parameters should be set:

        SERVO1_FUNCTION = 94
        SERVO2_FUNCTION = 95
        ...
        SERVO10_FUNCTION = 103

    To enable in-place (pivot) turns we also need to set two servo function slots
    to Throttle L and Throttle R. These are not used on the rover or in the script.

        SERVO11_FUNCTION = 73
        SERVO12_FUNCTION = 74
--]]

-- control outputs
local CONTROL_OUTPUT_THROTTLE = 3
local CONTROL_OUTPUT_YAW = 4

-- servo outputs
local SERVO1_FUNCTION = 94      -- front_left_wheel_joint
local SERVO2_FUNCTION = 95      -- front_right_wheel_joint
local SERVO3_FUNCTION = 96      -- mid_left_wheel_joint
local SERVO4_FUNCTION = 97      -- mid_right_wheel_joint
local SERVO5_FUNCTION = 98      -- back_left_wheel_joint
local SERVO6_FUNCTION = 99      -- back_right_wheel_joint

local SERVO7_FUNCTION = 100     -- front_left_steer_joint
local SERVO8_FUNCTION = 101     -- front_right_steer_joint
local SERVO9_FUNCTION = 102     -- back_left_steer_joint
local SERVO10_FUNCTION = 103    -- back_right_steer_joint

-- update at 50Hz
local UPDATE_PERIOD = 20

-- wheel geometry for a Sawppy rover (NED), units are [m]
local WHEEL_COORDS = {}
WHEEL_COORDS[1] = { 0.28, -0.235}   -- front_left
WHEEL_COORDS[2] = { 0.28,  0.235}   -- front_right
WHEEL_COORDS[3] = { 0.00, -0.260}   -- mid_left
WHEEL_COORDS[4] = { 0.00,  0.260}   -- mid_right
WHEEL_COORDS[5] = {-0.25, -0.235}   -- back_left
WHEEL_COORDS[6] = {-0.25,  0.235}   -- back_right

local MID_WHEEL_SEP = 0.52          -- mid-right - mid-left

--[[
    Return true if the value is negative

    Parameters
    ==========
    value : float
        The value to test if negative

    Returns
    =======
    boolean
        True if the value is negative
--]]
local function is_negative(value)
    return value < 0.0
end

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
    Linearly interpolate within an output range given a value from an input range

    Parameters
    ==========
    low_out : float
        The lower limit of the output range
    high_out : float
        The upper limit of the output range
    val_in : float
        The value to interpolate
    low_in : float
        The lower limit of the input range
    high_in : float
        The upper limit of the input range

    Returns
    =======
    float
        The interpolated value constrained to the output range
--]]
local function linear_interpolate(low_out, high_out, val_in, low_in, high_in)
    local slope = (high_out - low_out) / (high_in - low_in)
    local intercept = low_out - slope * low_in
    local val_out = slope * val_in + intercept
    return val_out
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
    Apply skid-steering saturation limits to the scaled steering and throttle

    Adapted from ardupilot/Rover/AP_MotorsUGV::output_skid_steering

    Parameters
    ==========
    steering : float
        The steering control output in [-1, 1]
    throttle : float
        The throttle control output in [-1, 1]

    Returns
    =======
    steering, throttle : float, float
        The saturation limited scaled control outputs

--]]
local function apply_skid_steer_saturation_limits(steering, throttle)
    local steering_scaled = steering
    local throttle_scaled = throttle

    -- check for saturation and scale back steering and throttle
    local saturation_value = math.abs(steering_scaled) + math.abs(throttle_scaled)
    if saturation_value > 1.0 then
        local fair_scaler = 1.0 / saturation_value
        steering_scaled = steering_scaled * fair_scaler
        throttle_scaled = throttle_scaled * fair_scaler
    end

    return steering_scaled, throttle_scaled
end

--[[
    Calculate the motor outputs for skid steering from saturation limited control outputs

    Adapted from ardupilot/Rover/AP_MotorsUGV::output_skid_steering

    Parameters
    ==========
    steering : float
        The saturation limited steering control output in [-1, 1]
    throttle : float
        The saturation limited throttle control output in [-1, 1]

    Returns
    =======
    motor_left, motor_right : float, float
        The scaled left and right motor outputs in [-1, 1]
--]]
local function output_skid_steering(steering, throttle)
    local motor_left = throttle + steering
    local motor_right = throttle - steering
    return motor_left, motor_right
end

--[[
    Calculate the turning radius and rate about the instantaneous centre of curvature

    This calculation is in normalised coordinates. The origin of the body frame {B}
    is assumed to lie at the mid-point between the two wheels and the distance from
    the origin of {B} to each wheel is 1.

    IMPORTANT NOTE: this function assumes the steering and throttle are POSITIVE

    Parameters
    ==========
    steering : float
        The saturation limited steering control output in [0, 1]
    throttle : float
        The saturation limited throttle control output in [0, 1]

    Returns
    =======
    radius, rate : float, float
        The distance from the origin of the body frame {B} to the
         instantaneous centre of curvature frame P and the rate of turn
        of {B} about P.
--]]
local function turning_radius_and_rate(steering, throttle)
    -- left and right wheel velocities
    local v_l = throttle + steering
    local v_r = throttle - steering

    -- turning radius is infinite if steering is zero
    local r_p = math.huge
    local omega_p = 0
    if v_l ~= v_r then
        r_p = (v_l + v_r) / (v_l - v_r)
        omega_p = v_l / (r_p + 1)
    end

    return r_p, omega_p
end

--[[
    Rescale the wheel coordinates by the half the mid wheel separation

    The saturation limits for steering and throttle control are calculated
    in scaled coordinates assuming a wheel separation of 2.

    Parameters
    ==========
    wheel_coords : array
        The array of wheel coordinates (x, y)
    mid_wheel_sep : float
        The lateral distance between the left and right mid wheels

    Returns
    =======
    array
        The scaled (normalised) wheel coordinates

--]]
local function normalise_wheel_coordinates(wheel_coords, mid_wheel_sep)
    return scale_vector2d(wheel_coords, 2.0 / mid_wheel_sep)
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
local function wheel_angle(icc, wheel_coord)
    local dx = icc[1] - wheel_coord[1]
    local dy = icc[2] - wheel_coord[2]
    local theta = math.atan(dx, dy)
    return theta
end

--[[
    Calculate the servo outputs for a Sawppy rover from steering and throttle control

    This function calculates the wheel speed and steering angle for each of the
    six drive wheels and four steering servos on a Sawppy rover. The servo outputs are
    normalised to [-1, 1].

    The steering angles are constrained [-pi/2, pi/2], and if a the required steering
    is out of range the direction of the steering servo and wheel is reversed. This means
    a servo must have a range of at least [0, 180] deg with the mid point aligned
    forward for the front servos and back for the back servos.

    Parameters
    ==========
    steering : float
        The normalised steering rate in [-1, 1]
    throttle : float
        The normalised throttle in [-1, 1]

    Returns
    =======
    wheels, steers : array, array
        Return the normalised servo outputs for 6 wheels and 3 steers
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
    local throttle_sign = 1
    if throttle < 0 then
        throttle_sign = -1
        throttle = -throttle
    end

    -- saturation limited control outputs
    local steering_scaled, throttle_scaled = apply_skid_steer_saturation_limits(steering, throttle)

    -- skid steering motor outputs in normalised corrdinates
    local motor_left, motor_right = output_skid_steering(steering_scaled, throttle_scaled)
    local motor_out = math.max(math.abs(motor_left), math.abs(motor_right)) * throttle_sign

    local wheels = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
    local steers = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0}

    -- instantaneous centre of curvature
    local r = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
    local r_p, omega_p = turning_radius_and_rate(steering, throttle)
    local icc = {0.0, r_p}

    -- normalised wheel coordinates
    local wheel_coords = normalise_wheel_coordinates(WHEEL_COORDS, MID_WHEEL_SEP)

    -- normalised turning radius for each wheel
    for i = 1, #r do
       r[i] = wheel_turning_radius(icc, wheel_coords[i])
    end
    r = rescale_turning_radii(r)

    -- wheel speed and steering angles
    for i = 1, #r do
        wheels[i] = motor_out * r[i]
        steers[i] = wheel_angle(icc, wheel_coords[i])

        -- apply steering constraints (rotate by 180 and reverse direction)
        if steers[i] > math.pi / 2.0 then
            wheels[i] = -wheels[i]
            steers[i] = steers[i] - math.pi
        end
        if steers[i] < -math.pi / 2.0 then
            wheels[i] = -wheels[i]
            steers[i] = steers[i] + math.pi
        end

        -- rescale steer outputs to [0, 1]
        steers[i] = steers[i] / math.pi

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

    return wheels, steers
end

--[[
    Main update loop

    Poll the control outputs every UPDATE_PERIOD milli seconds,
    compute the servo outputs for wheels and steeing and send
    them to the servo channels.
--]]
local function update()
    if not arming:is_armed() then
        -- if not armed move steering and throttle to mid

        -- wheel servos
        SRV_Channels:set_output_norm(SERVO1_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO2_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO3_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO4_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO5_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO6_FUNCTION, 0)

        -- steer servos
        SRV_Channels:set_output_norm(SERVO7_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO8_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO9_FUNCTION, 0)
        SRV_Channels:set_output_norm(SERVO10_FUNCTION, 0)

    else
        -- retrieve high level steering and throttle control outputs
        local steering = vehicle:get_control_output(CONTROL_OUTPUT_YAW)
        local throttle = vehicle:get_control_output(CONTROL_OUTPUT_THROTTLE)

        local wheels = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
        local steers = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
        if (steering and throttle) then
            -- compute servo outputs
            wheels, steers = servo_outputs(steering, throttle)
        end

        -- wheel servos
        SRV_Channels:set_output_norm(SERVO1_FUNCTION, wheels[1])
        SRV_Channels:set_output_norm(SERVO2_FUNCTION, wheels[2])
        SRV_Channels:set_output_norm(SERVO3_FUNCTION, wheels[3])
        SRV_Channels:set_output_norm(SERVO4_FUNCTION, wheels[4])
        SRV_Channels:set_output_norm(SERVO5_FUNCTION, wheels[5])
        SRV_Channels:set_output_norm(SERVO6_FUNCTION, wheels[6])

        -- steer servos (the middle two wheels do not steer)
        SRV_Channels:set_output_norm(SERVO7_FUNCTION, steers[1])
        SRV_Channels:set_output_norm(SERVO8_FUNCTION, steers[2])
        SRV_Channels:set_output_norm(SERVO9_FUNCTION, steers[5])
        SRV_Channels:set_output_norm(SERVO10_FUNCTION, steers[6])

    end

    return update, UPDATE_PERIOD
end

gcs:send_text(6, "sawppy_motor_driver.lua is running")
return update(), 3000

