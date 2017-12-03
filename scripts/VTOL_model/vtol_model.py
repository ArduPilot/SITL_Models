#!/usr/bin/env python
'''
VTOL mission calculator
Based on a matlab script by Paul Riseborough
converted to python by Andrew Tridgell

released under GPLv3
'''

import optparse
from util import *
import propeller
import battery
import motor
import wing
import util
from math import *

parser = optparse.OptionParser("vtol_model.py")
parser.add_option("--prop-model", default='APC11x7', help='prop model name [default: %default]')
parser.add_option("--prop-diameter", type='float', default=11.0, help='prop diameter inches [default: %default]')
parser.add_option("--battery-model", default='5Ah_6S_Nanotech', help='battery model name [default: %default]')
parser.add_option("--cell-series", type='int', default=12, help='cell series count [default: %default]')
parser.add_option("--cell-parallel", type='int', default=2, help='cell parallel count [default: %default]')
parser.add_option("--motor-type", default='MT3520-11-400kV', help='motor type [default: %default]')
parser.add_option("--wing-span", type='float', default=3.0, help='wing span in meters [default: %default]')
parser.add_option("--aspect-ratio", type='float', default=8.0, help='wing aspect ratio [default: %default]')
parser.add_option("--mission-speed", type='float', default=28.0, help='mission min speed in m/s [default: %default]')
parser.add_option("--hover-time", type='float', default=5.0, help='hover time in minutes [default: %default]')
parser.add_option("--mass-payload", type='float', default=0.5, help='payload mass in Kg [default: %default]')
parser.add_option("--mass-avionics", type='float', default=0.15, help='avionics mass in Kg [default: %default]')
parser.add_option("--mass-structure", type='float', default=4.15, help='structure mass in Kg [default: %default]')
parser.add_option("--num-motors-cruise", type='int', default=2, help='number of motors in cruise [default: %default]')
parser.add_option("--num-motors-hover", type='int', default=2, help='number of motors in cruise [default: %default]')
parser.add_option("--num-motors-total", type='int', default=2, help='number of motors total [default: %default]')

opts, args = parser.parse_args()

# get prop, battery, motor and wing models
prop = propeller.propeller(opts.prop_model, opts.prop_diameter)
battery = battery.battery(opts.battery_model, opts.cell_series, opts.cell_parallel)
motor = motor.motor(opts.motor_type)

# get requred performance
mission_speed_min = opts.mission_speed # min mission speed (m/s)
mission_hover_time = opts.hover_time # mission hover time (minutes)

# mass properties
mass_payload = opts.mass_payload # payload mass (Kg) - allowance for camera and TX module
mass_avionics = opts.mass_avionics # mass of autopilot, C2 link, power supply and wiring (doesn't include servos)
mass_structure = opts.mass_structure # airframe mass including servos and linkages (or None)
structure_mass_frac = None # fraction of AUW that is structure plus servos (or None)

# define motor parameters assuming a T-motor MT-3520-11
n_motors_cruise = opts.num_motors_cruise # number of motor/prop units used during cruise
n_motors_hover = opts.num_motors_hover # number of motor/prop units used during hover
n_motors_total = opts.num_motors_total # total number of mtors
if n_motors_total > n_motors_hover + n_motors_cruise:
    error("Total number of motors higher than sum of cruise and hover")

# Correction coefficients from static thrust validation test
CP_correction_factor = 1.00 # CP data from the prop database is multiplied by this factor
CT_correction_factor = 1.00 # CT data from the prop database is multiplied by this factor

# assumed avionics parastic electrical power draw (W)
avionics_power = 10.0

# calculate mass of battery
mass_batt = battery.get_mass()

# calculate propulsion mass which is mass of props, motors and esc's
mass_propulsion = n_motors_total*(motor.get_mass()+prop.get_mass())

# calculate all up mass
if mass_structure is not None:
    mass_auw = mass_batt + mass_avionics + mass_payload + mass_propulsion + mass_structure
elif structure_mass_frac is not None:
    mass_auw = (mass_batt + mass_avionics + mass_payload + mass_propulsion) / (1.0 - structure_mass_frac)
    mass_structure = structure_mass_frac * mass_auw
else:
    error('supply either structure_mass or structure_mass_frac data')

wing = wing.wing(opts.wing_span, opts.aspect_ratio, mass_auw)

# Calculate mission speed and drag
speed_max_endurance = max(wing.lift_coef_stall_margin * wing.get_speed_stall(), wing.get_speed_min_pwr())

# calculate our mission speed as the maximum of the max endurance speed
# and the desired min mission speed
speed_mission = max(speed_max_endurance,mission_speed_min)

# calculate drag parameters
drag = wing.calc_drag(mass_auw, speed_mission)

def calc_cruise_RPM():
    '''
    calculate the RPM required to provide the required thrust for the
    specified prop
    return a structure containing the outputs
    '''
    # find best efficiency operating condition and use as a starting condition
    best_prop_j = prop.find_best_ETA(0.01)

    best_nD = speed_mission / best_prop_j
    best_prop_rpm = 60 * best_nD / prop.get_diameter_m()

    solution_converged = False
    counter = 0
    while not solution_converged:
        # calculate advance ratio
        best_nD = (best_prop_rpm / 60) * prop.get_diameter_m()
        prop_j = speed_mission / best_nD
        prop_j=min(prop_j,prop.get_J_max())
        prop_j=max(prop_j,prop.get_J_min())
        
        # get thrust coefficient
        CT = prop.get_CT(prop_j)
        thrust = CT * (rho * best_nD**2 * prop.get_diameter_m()**2)
        thrust_error = n_motors_cruise * thrust - drag.drag_max_endurance
        best_prop_rpm = best_prop_rpm * (1.0 - 0.01 * thrust_error / thrust)
        
        # check for convergence
        counter += 1
        if abs(thrust_error) < (0.001 * drag.drag_max_endurance):
            solution_converged = True
        elif counter > 10000:
            error('endurance prop calculation could not converge')

    # calculate power required
    CP = prop.get_CP(prop_j)
    power = rho * CP * best_nD**3 * prop.get_diameter_m()**2

    # return a structure containing the outputs
    return struct(RPM = best_prop_rpm,
                  power = power,
                  J = prop_j,
                  thrust = thrust,
                  CP = CP,
                  CT = CT)

def calc_cruise_data(cruise):
    '''
    calculate cruise power and voltage
    '''

    # calcuate torque required
    best_motor_torque = cruise.power / (2.0 * pi * cruise.RPM / 60)

    # Endurance Calculations using simple fixed efficiency values

    # calculate propeller inflow_factor
    prop_area = pi/4.0 * prop.get_diameter_m()**2
    coef_C = - (drag.drag_max_endurance / n_motors_cruise) / (2.0 * rho * prop_area * speed_mission**2)
    inflow_factor = (-1.0 + sqrt(1-4*coef_C))/2

    power_prop = (1.0 / prop.get_efficiency()) * (1.0 + inflow_factor) * speed_mission * (drag.drag_max_endurance / n_motors_cruise)

    power_batt = n_motors_cruise * power_prop / motor.get_efficiency()

    endurance_hours_initial = battery.get_watt_hours() / power_batt

    # update endurance using DC motor theory and manufacturer data

    # calculate motor current at best endurance condition, scaling motor zero
    # load current linearly with RPM
    motor_current = (best_motor_torque / motor.get_torque_constant())
    motor_current += motor.get_io_current_rpm(cruise.RPM)

    # calculate back emf
    motor_emf = cruise.RPM / motor.get_kV()

    # calculate initial motor supply voltage
    motor_voltage_endurance = motor_emf
    motor_voltage_endurance += motor.get_esr() * motor_current
    motor_voltage_endurance += motor.get_supply_esr() * motor_current * n_motors_cruise

    # check if required supply voltage exceeds battery rating.
    if motor_voltage_endurance > battery.get_voltage_min():
        error('insufficient battery voltage or prop too small')

    # optimum current = sqrt(Io*V/R)
    motor_current_best_eff = sqrt((motor.get_io_current_rpm(cruise.RPM) * motor_voltage_endurance) / motor.get_esr())

    # calculate total batery power at best endurance flight condition
    cruise.batt_power = n_motors_cruise * motor_current * motor_voltage_endurance + avionics_power

    # calculate endurance
    cruise.endurance_minutes = 60 * battery.get_watt_hours() / cruise.batt_power

    # calculate still air range at mission speed
    cruise.range_still_air = 60 * cruise.endurance_minutes * speed_mission

    cruise.thrust_power = speed_mission * cruise.thrust
    cruise.motor_power_out = (2.0*pi*cruise.RPM/60) * best_motor_torque
    cruise.motor_power_in = motor_voltage_endurance * motor_current
    cruise.motor_current = motor_current
    cruise.motor_current_best_eff = motor_current_best_eff

# calculate cruise RPM
cruise = calc_cruise_RPM()

# and calculate cruise data
calc_cruise_data(cruise)


def calc_climb(battery_voltage):
    '''
    calculate max sustained climb rate for given battery voltage
    perform iterative solution to calculate thrust at with specified supply voltage
    TODO - add a basic thermal model
    '''
    rpm = cruise.RPM
    supply_voltage = battery_voltage
    solution_converged = False
    counter = 0
    while not solution_converged:
        # calculate propeller torque load
        nD_climb = (rpm / 60) * prop.get_diameter_m()
        J_climb = speed_mission / nD_climb
        J_climb=min(J_climb,prop.get_J_max())
        J_climb=max(J_climb,prop.get_J_min())
        CP_climb = prop.get_CP(J_climb)
        prop_power_climb = CP_climb * (rho * nD_climb**3 * prop.get_diameter_m()**2)
        prop_torque_climb = prop_power_climb / (2.0 * pi * rpm / 60)
    
        # calculate motor torque
        emf_climb = rpm / motor.get_kV()
        motor_current_climb = (supply_voltage - emf_climb) / (motor.get_esr() + n_motors_cruise * motor.get_supply_esr())
    
        # limit motor current if necessary by adjusting supply voltage downwards
        if motor_current_climb > motor.get_current_lim():
            motor_current_climb = motor.get_current_lim()
    
        # calculate excess torque - assume motor i0 varies linearly with back emf
        excess_torque = (motor_current_climb - motor.get_i0_current() * emf_climb / motor.get_i0_voltage()) * motor.get_torque_constant() - prop_torque_climb
        excess_CQ = excess_torque / (rho * nD_climb**2 * prop.get_diameter_m()**2)
    
        # check for convergence
        counter += 1
        if abs(excess_torque / prop_torque_climb) < 0.001:
            solution_converged = True
        elif counter > 1000:
            error('full battery climb calculation failed to converge')
    
        # increment RPM proportional to excess torque coefficient
        rpm = rpm + 1000 * (speed_mission / prop.get_diameter_m()) * excess_CQ

    # record power supply requirements for climb
    motor_current = motor_current_climb
    motor_voltage = motor_current_climb * (motor.get_esr() + n_motors_cruise * motor.get_supply_esr()) + emf_climb
    motor_power = motor_current * motor_voltage

    # calculate climb rate using mission speed
    CT = prop.get_CT(J_climb)
    thrust_climb = n_motors_cruise * CT * (rho * nD_climb**2 * prop.get_diameter_m()**2)
    if thrust_climb <= (drag.drag_max_endurance + (mass_auw * gravity)):
        excess_thrust_power = (thrust_climb - drag.drag_max_endurance) * speed_mission
        climb_rate = excess_thrust_power / (mass_auw * gravity)
    else:
        climb_rate = speed_mission

    return struct(RPM = rpm,
                  climb_rate = climb_rate,
                  motor_current = motor_current)
                  

# calculate max and min climb
climb_max = calc_climb(battery.get_voltage_max())
climb_min = calc_climb(battery.get_voltage_min())

def calc_hover(battery_voltage):
    '''
    Hover condition
    perform iterative solution to calculate specified supply voltage and
    armature current required to hover with given battery voltage
    TODO - add a basic thermal model
    '''
    supply_voltage = battery_voltage
    thrust_converged = False
    thrust_loop_counter = 0
    CP_test = prop.get_CP(0)
    CT_test = prop.get_CT(0)
    rpm_test = (2/3.0) * supply_voltage * motor.get_kV()
    while not thrust_converged:
        torque_converged = False
        torque_loop_counter = 0
        while not torque_converged:
            # calculate propeller torque load
            nD_test = (rpm_test / 60) * prop.get_diameter_m()
            prop_power_test = CP_test * (rho * nD_test**3 * prop.get_diameter_m()**2)
            prop_torque_test = prop_power_test / (2 * pi * rpm_test / 60)
        
            # calculate motor torque
            emf_test = rpm_test / motor.get_kV()
            motor_current = (supply_voltage - emf_test) / motor.get_esr()
        
            # limit motor current if necessary by adjusting supply voltage downwards
            if motor_current > motor.get_current_lim():
                motor_current = motor.get_current_lim()
        
            # calculate excess torque - assume motor i0 varies linearly with back emf
            excess_torque = (motor_current - motor.get_i0_current() * emf_test / motor.get_i0_voltage()) * motor.get_torque_constant() - prop_torque_test
            excess_CQ = excess_torque / (rho * nD_test**2 * prop.get_diameter_m()**2)
        
            # check for convergence
            torque_loop_counter += 1
            if abs(excess_torque / prop_torque_test) < 0.001:
                torque_converged = 1
            elif torque_loop_counter > 1000:
                error('hover test torque failed to converge')
        
            # increment RPM proportional to excess torque coefficient
            rpm_test = rpm_test + 1000 * (speed_mission / prop.get_diameter_m()) * excess_CQ
    
        # calculate thrust from test
        thrust_test = CT_test * (rho * nD_test**2 * prop.get_diameter_m()**2)
    
        thrust_error = (thrust_test * n_motors_hover) - (mass_auw * gravity)
        supply_voltage = supply_voltage * (1.0 - 0.1*thrust_error/(mass_auw * gravity))
    
        # check for convergence
        thrust_loop_counter += 1
        if abs(thrust_error) < (0.01 * mass_auw * gravity):
            thrust_converged = True
        elif thrust_loop_counter > 1000:
            error('hover test thrust failed to converge')

    # record power supply requirements for test
    motor_voltage = motor_current * motor.get_esr() + emf_test
    motor_power = motor_current * motor_voltage

    thrust_grams = thrust_test / gravity * 1000

    batt_watt_corrected_hours = battery.get_watt_hours() - motor_power * n_motors_hover * mission_hover_time / 60.0
    corrected_endurance_minutes = 60 * batt_watt_corrected_hours / cruise.batt_power
    corrected_range = 60 * corrected_endurance_minutes * speed_mission

    return struct(RPM = rpm_test,
                  thrust_grams = thrust_grams,
                  voltage = supply_voltage,
                  motor_voltage = motor_voltage,
                  motor_current = motor_current,
                  motor_power = motor_power,
                  corrected_endurance_minutes = corrected_endurance_minutes,
                  corrected_range = corrected_range)
                       

# calculate hover parameters for min voltage
hover = calc_hover(battery.get_voltage_min())

# print report
print('############################################################')
print('# Dimensions                                               #')
print('############################################################')
print('wing span = %.1f m,  AR = %.1f' % (wing.get_wing_span(), wing.get_aspect_ratio()))
print('wing chord = %.3f m, AR = %.1f' % (wing.get_MAC(),wing.get_aspect_ratio()))

print(' ')
print('############################################################')
print('# Mass                                                     #')
print('############################################################')
print('total mass = %.2f Kg' % mass_auw)
print('airframe structure mass = %.2f Kg' % mass_structure)
print('avionics mass = %.2f Kg' % mass_avionics)
print('propulsion mass = %.2f Kg' % mass_propulsion)
print('battery mass = %.2f Kg' % mass_batt)
print('payload mass = %.2f Kg' % mass_payload)
print('non-battery mass = %.2f Kg' % (mass_auw - mass_batt))

print(' ')
print('############################################################')
print('# Aerodynamic Performance                                  #')
print('############################################################')
print('stall speed = %.2f m/s' % wing.get_speed_stall())
print('minimum power speed = %.2f m/s' % wing.get_speed_min_pwr())
print('minimum drag speed = %.2f m/s' % wing.get_speed_min_drag())
print('mission speed = %.1f m/s' % speed_mission)
print('Reynolds number = %.2e m/s' % (69000 * wing.get_MAC() * speed_mission))
print('L/D max = %.3f at %.2f m/s' % (drag.LD_max, wing.get_speed_min_drag()))
print('L/D at mission speed  = %.2f' % drag.LD_mission)

print(' ')
print('############################################################')
print('# Propulsion                                               #')
print('############################################################')
print('Battery type = %s' % battery.get_description())
print('Motor type = %s' % motor.get_type())
print('prop shape used = %s' % prop.get_prop_model())
print("num motors cruise = %u" % n_motors_cruise)
print("num motors hover = %u" % n_motors_hover)
print("num motors total = %u" % n_motors_total)
print('prop diameter specified = %.1f in' % (prop.get_diameter_in()))
print('prop pitch specified = %.1f in' % prop.get_pitch_in())
print('power used by specified prop = %.0f' % cruise.power)
print('mission RPM = %.0f' % cruise.RPM)
print('mission advance ratio = %.3f' % cruise.J)
print('mission CT = %.4f' % cruise.CT)
print('mission CP = %.4f' % cruise.CP)

print(' ')
print('############################################################')
print('# Flight Performance                                       #')
print('############################################################')
print('mission speed = %.1f m/s' % speed_mission)
print('endurance = %.1f min (no hover)' % cruise.endurance_minutes)
print('endurance = %.1f min (with hover)' % hover.corrected_endurance_minutes)
print('still air range = %.2f km (no hover)' % (cruise.range_still_air/1000.0))
print('still air range = %.2f km (with hover)' % (hover.corrected_range/1000.0))
print('batt power draw = %.0f W' % cruise.batt_power)
print('prop efficiency = %.1f %%' % (100*cruise.thrust_power/cruise.motor_power_out))
print('motor efficiency = %.1f %%' % (100*cruise.motor_power_out/cruise.motor_power_in))
print('motor current = %.1f Amps' % cruise.motor_current)
print('ideal motor current = %.1f Amps' % cruise.motor_current_best_eff)
print('fully charged climb rate = %.2f m/s at %.1f motor Amps' % (climb_max.climb_rate, climb_max.motor_current))
print('fully discharged climb rate = %.2f m/s at %.1f motor Amps' % (climb_min.climb_rate, climb_min.motor_current))

print(' ')
print('############################################################')
print('# Hover Performance Prediction - Fully Discharged          #')
print('############################################################')
print('wind tunnel data set used = %s' % prop.get_prop_model())
print('prop diameter used = %.1f in' % prop.get_diameter_in())
print('prop pitch used = %.2f in' % prop.get_pitch_in())
print('ESC throttle = %.1f %%' % (100*hover.voltage/battery.get_voltage_min()))
print('motor current = %.1f Amps' % (hover.motor_current))
print('battery power = %.0f Watts' % (hover.motor_power*n_motors_hover))
print('cell current = %.2f Amps' % battery.get_cell_current(hover.motor_power*n_motors_hover, battery.get_voltage_min()))
print('prop speed = %.0f RPM' % hover.RPM)
print('prop speed safety limit = %.0f RPM' % (145000/(prop.get_diameter_in())))
print('prop thrust = %.0f g' % hover.thrust_grams)
print('mission radius adjusted for %.1f min hover time %.3f km' % (mission_hover_time,0.5*hover.corrected_range/1000))
