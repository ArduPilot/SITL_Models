#!/usr/bin/env python

'''
wing model class
'''

from util import *
from math import *

class wing(object):
    '''model a wing'''

    def __init__(self, wing_span, aspect_ratio, mass_auw):
        self.wing_span = wing_span
        self.aspect_ratio = aspect_ratio
        self.lift_coef_stall_margin = 1.5 # margin between level flight stall speed and mission speed
        self.CL_max = 1.2 # maximum lift coefficient
        self.span_efficiency = 0.85 # span efficiency factor
        self.CD0_wing = 0.015 # typical zero lift drag coefficient for a wing section at a Reynolds number around 300000
        self.fus_front_area = 0.1*0.1 # frontal area of the fuselage and motor pods(m^2)
        self.fus_drag_coef = 0.7 # assume front faired bluff body drag

        # x_cg = 0.33 * MAC
        # x_ac = 0.25 * MAC
        # Re = 69000*wing_span/aspect_ratio*speed_stall*1.5 # Wing Reynolds number at typical mission endurance speed
        self.CD0 = self.CD0_wing + self.fus_drag_coef*(self.fus_front_area/self.get_wing_area()) # zero lift drag coefficient of wing + body + tail
        self.speed_stall = sqrt((2 * mass_auw * gravity)/(rho * self.get_wing_area() * self.CL_max)) # minimum flying speed

        self.coef_A = 0.5 * rho * self.CD0 * self.get_wing_area()
        self.coef_B = 1.0 / (pi * self.wing_span**2 * self.span_efficiency) * (mass_auw * gravity)**2 / (0.5 * rho)

        self.speed_min_drag = (self.coef_B/self.coef_A)**0.25
        self.speed_min_pwr = 0.76 * self.speed_min_drag
        self.mass_auw = mass_auw

    def get_wing_area(self):
        '''return wing areas in m^2'''
        return self.wing_span**2 / self.aspect_ratio

    def get_wing_span(self):
        '''return wing span in meters'''
        return self.wing_span

    def get_aspect_ratio(self):
        '''return wing aspect ratio'''
        return self.aspect_ratio

    def get_MAC(self):
        '''return the mean aerodynamic chord'''
        return self.wing_span / self.aspect_ratio

    def get_speed_stall(self):
        '''return stall speed in m/s'''
        return self.speed_stall

    def get_speed_min_pwr(self):
        '''return speed at min power'''
        return self.speed_min_pwr

    def get_speed_min_drag(self):
        '''return speed at min drag'''
        return self.speed_min_drag

    def calc_drag(self, mass_auw, speed_mission):
        '''Drag Polar Calculations given weight and mission speed'''

        # drag = coef_A*speed^2 + coef_B/speed^2

        # sanity check for best L/D
        drag_best_LD = self.coef_A*self.speed_min_drag**2 + self.coef_B/self.speed_min_drag**2
        LD_max = mass_auw*gravity/drag_best_LD

        drag_max_endurance = self.coef_A*speed_mission**2 + self.coef_B/speed_mission**2

        LD_mission = self.mass_auw*gravity/(self.coef_A*speed_mission**2 + self.coef_B/speed_mission**2)

        return struct(drag_best_LD = drag_best_LD,
                      LD_max = LD_max,
                      drag_max_endurance = drag_max_endurance,
                      LD_mission = LD_mission)

