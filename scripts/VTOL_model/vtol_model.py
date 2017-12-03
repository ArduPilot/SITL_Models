#!/usr/bin/env python

'''
TVBS mission calculator
Based on a matlab script by Paul Riseborough
converted to python by Andrew Tridgell
'''

import optparse
from util import error
import propeller
import battery
import motor
from math import *

parser = optparse.OptionParser("vtol_obc.py")
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
parser.add_option("--num-motors-cruise", type='int', default=1, help='number of motors in cruise [default: %default]')
parser.add_option("--num-motors-hover", type='int', default=3, help='number of motors in cruise [default: %default]')
parser.add_option("--num-motors-total", type='int', default=3, help='number of motors total [default: %default]')

opts, args = parser.parse_args()

prop = propeller.propeller(opts.prop_model, opts.prop_diameter)
battery = battery.battery(opts.battery_model, opts.cell_series, opts.cell_parallel)
motor = motor.motor(opts.motor_type)

# physical constants
gravity = 9.80665 # acceleration due to gravity (m/s^2)
rho = 1.225 # air density Kg/m^3

# performance
mission_speed_min = opts.mission_speed # min mission speed (m/s)
mission_hover_time = opts.hover_time # mission hover time (minutes)

# mass properties
mass_payload = opts.mass_payload # payload mass (Kg) - allowance for camera and TX module
mass_avionics = opts.mass_avionics # mass of autopilot, C2 link, power supply and wiring (doesn't include servos)
mass_structure = opts.mass_structure # airframe mass including servos and linkages (or None)
structure_mass_frac = None # fraction of AUW that is structure plus servos (or None)

# aerodynamic properties
wing_span = opts.wing_span # If no wing span is specified, then the wing loading target will be used to calculate the required span (m)
lift_coef_stall_margin = 1.5 # margin between level flight stall speed and mission speed
aspect_ratio = opts.aspect_ratio # wing aspect ratio (span/MAC)
CL_max = 1.2 # maximum lift coefficient
span_efficiency = 0.85 # span efficiency factor
CD0_wing = 0.015 # typical zero lift drag coefficient for a wing section at a Reynolds number around 300000
fus_front_area = 0.1*0.1 # frontal area of the fuselage and motor pods(m^2)
fus_drag_coef = 0.7 # assume front faired bluff body drag


# define motor parameters assuming a T-motor MT-3520-11
n_motors_cruise = opts.num_motors_cruise # number of motor/prop units used during cruise
n_motors_hover = opts.num_motors_hover # number of motor/prop units used during hover
n_motors_total = opts.num_motors_total # total number of mtors
if n_motors_total > n_motors_hover + n_motors_cruise:
    error("Total number of motors higher than sum of cruise and hover")

# Correction coefficients from static thrust validation test
CP_correction_factor = 1.00 # CP data from the prop database is multiplied by this factor
CT_correction_factor = 1.00 # CT data from the prop database is multiplied by this factor

avionics_power = 10.0 # avionics parastic electrical power draw (W)

# load prop lookup table data
# J = V/nD, where V is airspeed, n is revs/sec and D is diameter
# CT = T / (rho * n^2 * D^4) where T is thrust in N
# CP = P / (rho * n^3 * D^5) where P is power in W


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


# calculate mass of airframe

# calculate bettery energy density allowig for packaging efficiency and
# ageing
batt_energy_density = battery.get_energy_density()

# aerodynamic parameters
wing_area = wing_span**2 / aspect_ratio
MAC = wing_span / aspect_ratio
x_cg = 0.33 * MAC
x_ac = 0.25 * MAC
speed_stall = sqrt((2 * mass_auw * gravity)/(rho * wing_area * CL_max)) # minimum flying speed
Re = 69000*wing_span/aspect_ratio*speed_stall*1.5 # Wing Reynolds number at typical mission endurance speed
CD0 = CD0_wing + fus_drag_coef*(fus_front_area/wing_area) # zero lift drag coefficient of wing + body + tail

mass_non_battery = mass_auw - mass_batt

# Drag Polar Calculations
# drag = coef_A*speed^2 + coef_B/speed^2
coef_A = 0.5 * rho * CD0 * wing_area
coef_B = 1.0 / (pi * wing_span**2 * span_efficiency) * (mass_auw * gravity)**2 / (0.5 * rho)

speed_min_drag = (coef_B/coef_A)**0.25
speed_min_pwr = 0.76 * speed_min_drag

# sanity check for best L/D
drag_best_LD = coef_A*speed_min_drag**2 + coef_B/speed_min_drag**2
LD_max = mass_auw*gravity/drag_best_LD

# Calculate mission speed and drag
speed_max_endurance = max(lift_coef_stall_margin * speed_stall , speed_min_pwr)
speed_max_endurance = max(speed_max_endurance,mission_speed_min)
drag_max_endurance = coef_A*speed_max_endurance**2 + coef_B/speed_max_endurance**2

# Calculate operating point for the prop

prop_data_J_min = prop.get_J_min()
prop_data_J_max = prop.get_J_max()

# find best efficiency operating condition and use as a starting condition
best_prop_j = prop.find_best_ETA(0.01)

best_nD = speed_max_endurance / best_prop_j
best_prop_rpm = 60 * best_nD / prop.get_diameter_m()

# calculate the RPM required to provide the required thrust for the
# specified prop
solution_converged = False
counter = 0
while not solution_converged:
    # calculate advance ratio
    best_nD = (best_prop_rpm / 60) * prop.get_diameter_m()
    prop_j = speed_max_endurance / best_nD
    prop_j=min(prop_j,prop_data_J_max)
    prop_j=max(prop_j,prop_data_J_min)
    
    # get thrust coefficient
    
    CT = prop.get_CT(prop_j)
    thrust_endurance = CT * (rho * best_nD**2 * prop.get_diameter_m()**2)
    thrust_error_endurance = n_motors_cruise * thrust_endurance - drag_max_endurance
    best_prop_rpm = best_prop_rpm * (1.0 - 0.01 * thrust_error_endurance / thrust_endurance)
    
    # check for convergence
    counter = counter + 1
    if abs(thrust_error_endurance) < (0.001 * drag_max_endurance):
        solution_converged = True
    elif counter > 10000:
        error('endurance prop calculation could not converge')


# calculate power required
CP = prop.get_CP(prop_j)
best_prop_power = rho * CP * best_nD**3 * prop.get_diameter_m()**2

# calcuate torque required
best_motor_torque = best_prop_power / (2.0 * pi * best_prop_rpm / 60)

# Endurance Calculations using simple fixed efficiency values

# calculate propeller inflow_factor
prop_area = pi/4.0 * prop.get_diameter_m()**2
coef_C = - (drag_max_endurance / n_motors_cruise) / (2.0 * rho * prop_area * speed_max_endurance**2)
inflow_factor = (-1.0 + sqrt(1-4*coef_C))/2

power_prop = (1.0 / prop.get_efficiency()) * (1.0 + inflow_factor) * speed_max_endurance * (drag_max_endurance / n_motors_cruise)

power_batt = n_motors_cruise * power_prop / motor.get_efficiency()

batt_watt_hours = mass_batt * batt_energy_density

endurance_hours_initial = batt_watt_hours / power_batt

# update endurance using DC motor theory and manufacturer data

motor_torque_constant = 60.0 / (2.0 *  pi * motor.get_kV()) # Nm/Amp

# calculate motor current at best endurance condition, scaling motor zero
# load current linearly with RPM
motor_current_endurance = (best_motor_torque / motor_torque_constant)
motor_current_endurance += motor.get_i0_current() * (best_prop_rpm / (motor.get_i0_voltage() * motor.get_kV()))

# calculate back emf
motor_emf = best_prop_rpm / motor.get_kV()

# calculate initial motor supply voltage
motor_voltage_endurance = motor_emf
motor_voltage_endurance += motor.get_esr() * motor_current_endurance
motor_voltage_endurance += motor.get_supply_esr() * motor_current_endurance * n_motors_cruise

# check if required supply voltage exceeds battery rating.
if motor_voltage_endurance > battery.get_voltage_min():
    error('insufficient battery voltage or prop too small')

# optimum current = sqrt(Io*V/R)
temp = motor.get_i0_current() * (best_prop_rpm / (motor.get_i0_voltage() * motor.get_kV()))
motor_current_best_eff = sqrt((temp * motor_voltage_endurance) / motor.get_esr())

# calculate total batery power at best endurance flight condition
batt_power_endurance = n_motors_cruise * motor_current_endurance * motor_voltage_endurance + avionics_power

# calculate endurance
best_endurance_minutes = 60 * batt_watt_hours / batt_power_endurance

# calculate still air range at mission speed
range_still_air = 60 * best_endurance_minutes * speed_max_endurance

thrust_power = speed_max_endurance * thrust_endurance
motor_power_out = (2.0*pi*best_prop_rpm/60) * best_motor_torque
motor_power_in = motor_voltage_endurance * motor_current_endurance

# calculate max sustained climb rate (charged battery)

# perform iterative solution to calculate thrust at with specified supply voltage
# TODO - add a basic thermal model
rpm_climb = best_prop_rpm
supply_voltage = battery.get_voltage_max()
solution_converged = False
counter = 0
while not solution_converged:
    # calculate propeller torque load
    nD_climb = (rpm_climb / 60) * prop.get_diameter_m()
    J_climb = speed_max_endurance / nD_climb
    J_climb=min(J_climb,prop_data_J_max)
    J_climb=max(J_climb,prop_data_J_min)
    CP_climb = prop.get_CP(J_climb)
    prop_power_climb = CP_climb * (rho * nD_climb**3 * prop.get_diameter_m()**2)
    prop_torque_climb = prop_power_climb / (2.0 * pi * rpm_climb / 60)
    
    # calculate motor torque
    emf_climb = rpm_climb / motor.get_kV()
    motor_current_climb = (supply_voltage - emf_climb) / (motor.get_esr() + n_motors_cruise * motor.get_supply_esr())
    
    # limit motor current if necessary by adjusting supply voltage downwards
    if motor_current_climb > motor.get_current_lim():
        motor_current_climb = motor.get_current_lim()
    
    # calculate axcess torque - assume motor i0 varies linearly with
    # back emf
    excess_torque = (motor_current_climb - motor.get_i0_current() * emf_climb / motor.get_i0_voltage()) * motor_torque_constant - prop_torque_climb
    
    excess_CQ = excess_torque / (rho * nD_climb**2 * prop.get_diameter_m()**2)
    
    # check for convergence
    counter = counter + 1
    if abs(excess_torque / prop_torque_climb) < 0.001:
        solution_converged = True
    elif counter > 1000:
        error('full battery climb calculation failed to converge')
    
    # increment RPM proportional to excess torque coefficient
    rpm_climb = rpm_climb + 1000 * (speed_max_endurance / prop.get_diameter_m()) * excess_CQ

# record power supply requirements for climb
motor_current_max_climb = motor_current_climb
motor_voltage_max_climb = motor_current_climb * (motor.get_esr() + n_motors_cruise * motor.get_supply_esr()) + emf_climb
motor_power_max_climb = motor_current_max_climb * motor_voltage_max_climb

# calculate climb rate using endurance mission speed
CT = prop.get_CT(J_climb)
thrust_climb = n_motors_cruise * CT * (rho * nD_climb**2 * prop.get_diameter_m()**2)
if thrust_climb <= (drag_max_endurance + (mass_auw * gravity)):
    excess_thrust_power = (thrust_climb - drag_max_endurance) * speed_max_endurance
    climb_rate_max = excess_thrust_power / (mass_auw * gravity)
else:
    climb_rate_max = speed_max_endurance

# calculate min sustained climb rate (discharged battery)

# perform iterative solution to calculate thrust at with specified supply voltage
# TODO - add a basic thermal model
supply_voltage = battery.get_voltage_min()
solution_converged = False
counter = 0
while not solution_converged:
    # calculate propeller torque load
    nD_climb = (rpm_climb / 60) * prop.get_diameter_m()
    J_climb = speed_max_endurance / nD_climb
    J_climb=min(J_climb,prop_data_J_max)
    J_climb=max(J_climb,prop_data_J_min)
    CP_climb = prop.get_CP(J_climb)
    prop_power_climb = CP_climb * (rho * nD_climb**3 * prop.get_diameter_m()**2)
    prop_torque_climb = prop_power_climb / (2 * pi * rpm_climb / 60)
    # calculate motor torque
    emf_climb = rpm_climb / motor.get_kV()
    motor_current_climb = (supply_voltage - emf_climb) / (motor.get_esr() + n_motors_cruise * motor.get_supply_esr())
    
    # limit motor current if necessary by adjusting supply voltage downwards
    if motor_current_climb > motor.get_current_lim():
        motor_current_climb = motor.get_current_lim()
    
    # calculate axcess torque - assume motor i0 varies linearly with
    # back emf
    excess_torque = (motor_current_climb - motor.get_i0_current() * emf_climb / motor.get_i0_voltage()) * motor_torque_constant - prop_torque_climb
    
    excess_CQ = excess_torque / (rho * nD_climb**2 * prop.get_diameter_m()**2)
    
    # check for convergence
    counter = counter + 1
    if abs(excess_torque / prop_torque_climb) < 0.001:
        solution_converged = 1
    elif counter > 1000:
        error('low battery climb calculation failed to converge')
    
    # increment RPM proportional to excess torque coefficient
    rpm_climb = rpm_climb + 1000 * (speed_max_endurance / prop.get_diameter_m()) * excess_CQ

# record power supply requirements for climb
motor_current_min_climb = motor_current_climb
motor_voltage_min_climb = motor_current_climb * (motor.get_esr() + n_motors_cruise * motor.get_supply_esr()) + emf_climb
motor_power_min_climb = motor_current_min_climb * motor_voltage_min_climb

# calculate climb rate using endurance mission speed
CT = prop.get_CT(J_climb)
thrust_climb = n_motors_cruise * CT * (rho * nD_climb**2 * prop.get_diameter_m()**2)
if thrust_climb <= (drag_max_endurance + (mass_auw * gravity)):
    excess_thrust_power = (thrust_climb - drag_max_endurance) * speed_max_endurance
    climb_rate_min = excess_thrust_power / (mass_auw * gravity)
else:
    climb_rate_min = speed_max_endurance

# Hover condition
# perform iterative solution to calculate specified supply voltage and
# armature current required to hover
# TODO - add a basic thermal model
supply_voltage = battery.get_voltage_min()
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
        motor_current_hover = (supply_voltage - emf_test) / motor.get_esr()
        
        # limit motor current if necessary by adjusting supply voltage downwards
        if motor_current_hover > motor.get_current_lim():
            motor_current_hover = motor.get_current_lim()
        
        # calculate axcess torque - assume motor i0 varies linearly with
        # back emf
        excess_torque = (motor_current_hover - motor.get_i0_current() * emf_test / motor.get_i0_voltage()) * motor_torque_constant - prop_torque_test

        excess_CQ = excess_torque / (rho * nD_test**2 * prop.get_diameter_m()**2)
        
        # check for convergence
        torque_loop_counter = torque_loop_counter + 1
        if abs(excess_torque / prop_torque_test) < 0.001:
            torque_converged = 1
        elif torque_loop_counter > 1000:
            error('hover test torque failed to converge')
        
        # increment RPM proportional to excess torque coefficient
        rpm_test = rpm_test + 1000 * (speed_max_endurance / prop.get_diameter_m()) * excess_CQ
    
    # calculate thrust from test
    thrust_test = CT_test * (rho * nD_test**2 * prop.get_diameter_m()**2)
    
    thrust_error = (thrust_test * n_motors_hover) - (mass_auw * gravity)
    supply_voltage = supply_voltage * (1.0 - 0.1*thrust_error/(mass_auw * gravity))
    
    # check for convergence
    thrust_loop_counter = thrust_loop_counter + 1
    if abs(thrust_error) < (0.01 * mass_auw * gravity):
        thrust_converged = True
    elif thrust_loop_counter > 1000:
        error('hover test thrust failed to converge')

# record power supply requirements for test
motor_voltage_hover = motor_current_hover * motor.get_esr() + emf_test
motor_power_hover = motor_current_hover * motor_voltage_hover

thrust_grams = thrust_test / 9.80665 * 1000

batt_watt_hours = batt_watt_hours - motor_power_hover * n_motors_hover * mission_hover_time / 60.0
best_endurance_minutes = 60 * batt_watt_hours / batt_power_endurance
range_still_air = 60 * best_endurance_minutes * speed_max_endurance


# print report
print('############################################################')
print('# Dimensions                                               #')
print('############################################################')
print('wing span = %.1f m , AR = %.1f' % (wing_span, aspect_ratio))
print('wing chord = %.1f m, AR = %.1f' % (wing_span/aspect_ratio,aspect_ratio))

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
print('non-battery mass = %.2f Kg' % mass_non_battery)

print(' ')
print('############################################################')
print('# Aerodynamic Performance                                  #')
print('############################################################')
print('stall speed = %.2f m/s' % speed_stall)
print('minimum power speed = %.2f m/s' % speed_min_pwr)
print('minimum drag speed = %.2f m/s' % speed_min_drag)
print('mission speed = %.1f m/s' % speed_max_endurance)
print('Reynolds number = %.2e m/s' % (69000 * MAC * speed_max_endurance))
print('L/D max = %.3f at %.2f m/s' % (LD_max, speed_min_drag))
print('L/D at mission speed  = %.2f' % (mass_auw*gravity/(coef_A*speed_max_endurance**2 + coef_B/speed_max_endurance**2)))

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
print('power used by specified prop = %.0f' % best_prop_power)
print('mission RPM = %.0f' % best_prop_rpm)
print('mission advance ratio = %.3f' % prop_j)
print('mission CT = %.4f' % CT)
print('mission CP = %.4f' % CP)

print(' ')
print('############################################################')
print('# Flight Performance                                       #')
print('############################################################')
print('mission speed = %.1f m/s' % speed_max_endurance)
print('endurance = %.1f min' % best_endurance_minutes)
print('still air range = %.2f km' % (range_still_air/1000.0))
print('batt power draw = %.0f W' % batt_power_endurance)
print('prop efficiency = %.1f %%' % (100*thrust_power/motor_power_out))
print('motor efficiency = %.1f %%' % (100*motor_power_out/motor_power_in))
print('motor current = %.1f Amps' % motor_current_endurance)
print('ideal motor current = %.1f Amps' % motor_current_best_eff)
print('fully charged climb rate = %.2f m/s at %.1f motor Amps' % (climb_rate_max,motor_current_max_climb))
print('fully discharged climb rate = %.2f m/s at %.1f motor Amps' % (climb_rate_min, motor_current_min_climb))

print(' ')
print('############################################################')
print('# Hover Performance Prediction - Fully Discharged          #')
print('############################################################')
print('wind tunnel data set used = %s' % prop.get_prop_model())
print('prop diameter used = %.1f in' % prop.get_diameter_in())
print('prop pitch used = %.2f in' % prop.get_pitch_in())
print('ESC throttle = %.1f %%' % (100*supply_voltage/battery.get_voltage_min()))
print('motor current = %.1f Amps' % (motor_current_hover))
print('battery power = %.0f Watts' % (motor_power_hover*n_motors_hover))
print('cell current = %.2f Amps' % battery.get_cell_current(motor_power_hover*n_motors_hover, battery.get_voltage_min()))
print('prop speed = %.0f RPM' % rpm_test)
print('prop speed safety limit = %.0f RPM' % (145000/(prop.get_diameter_in())))
print('prop thrust = %.0f g' % (thrust_grams))
print('mission radius adjusted for %.1f min hover time %.3f km' % (mission_hover_time,0.5*range_still_air/1000))
