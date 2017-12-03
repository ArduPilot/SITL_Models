#!/usr/bin/env python

'''
motor model class
'''

from util import error
from math import *

motors = {}

class motor_data(object):
    def __init__(self, efficiency, supply_esr, i0_current, i0_voltage, kV, esr, mass, esc_mass, current_lim):
        self.efficiency = efficiency # rough motor efficiency
        self.supply_esr = supply_esr # supply resistance Ohms
        self.i0_current = i0_current # zero-load current Amps
        self.i0_voltage = i0_voltage # zero-load voltage
        self.kV = kV                 # RPM/volt unloaded
        self.esr = esr               # motor armature resistance (ohm)
        self.mass = mass             # mass in Kg
        self.esc_mass = esc_mass     # mass of ESC
        self.current_lim = current_lim # current limit in Amps

#############################################
# T-motor MT3520-11 400Kv with YPG HV 14S ESC
motors['MT3520-11-400kV'] = motor_data(
    efficiency = 0.85,
    supply_esr = 0.05,
    i0_current = 1.2,
    i0_voltage = 10.0,
    kV = 400,
    esr = 0.032,
    mass = 0.205,
    esc_mass = 0.170,
    current_lim = 38.0)

###################################################################
# T-motor U5-KV400 with Castle Creations PHOENIX EDGE HV 40 AMP ESC
motors['U5-400'] = motor_data(
    efficiency = 0.85,
    supply_esr = 0.05,
    i0_current = 0.3,
    i0_voltage = 10.0,
    kV = 400,
    esr = 0.116,
    mass = 0.195,
    esc_mass = 0.031,
    current_lim = 30.0)


class motor(object):
    '''model a motor'''

    def __init__(self, motor_type):
        if motor_type not in motors:
            error("Unknown motor type %s. Choices are %s" % (motor_type, motors.keys()))
        self.motor_type = motor_type
        self.data = motors[motor_type]

    def get_type(self):
        '''return motor type string'''
        return self.motor_type
        
    def get_mass(self):
        '''return total mass in Kg'''
        return self.data.mass + self.data.esc_mass

    def get_efficiency(self):
        '''return motor efficiency'''
        return self.data.efficiency

    def get_kV(self):
        '''return motor kV'''
        return self.data.kV

    def get_esr(self):
        '''return motor esr'''
        return self.data.esr

    def get_supply_esr(self):
        '''return motor supply esr'''
        return self.data.supply_esr

    def get_i0_current(self):
        '''return motor i0 current'''
        return self.data.i0_current

    def get_i0_voltage(self):
        '''return motor i0 voltage'''
        return self.data.i0_voltage

    def get_current_lim(self):
        '''return motor current limit'''
        return self.data.current_lim

    def get_io_current_rpm(self, rpm):
        '''return the base current for a motor at a given RPM'''
        return self.get_i0_current() * (rpm / (self.get_i0_voltage() * self.get_kV()))

    def get_torque_constant(self):
        '''return torque constant in Nm/Amp'''
        return 60.0 / (2.0 *  pi * self.get_kV())
