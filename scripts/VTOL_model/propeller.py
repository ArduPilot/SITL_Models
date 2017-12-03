#!/usr/bin/env python

'''
propeller model class
'''

import prop_data
from util import error

class propeller(object):
    '''model a single propeller'''

    def __init__(self, prop_model, prop_diameter):
        self.prop_eff = 0.65 # prop efficiency as a fraction of an ideal momentum disc
        self.prop_mass = 0.025
        self.prop_model = prop_model # select propeller model for efficiency curves
        self.data_pitch_ratio = 7.0/11.0 # pitch to diameter ratio of the prop used to generate the wind tunnel data
        self.prop_dia_m = prop_diameter*0.0254 # prop diameter specified (m).
        self.prop_pitch_m = self.prop_dia_m*self.data_pitch_ratio # Prop pitch calculated to match ratio of prop used to generate coef data.

        if prop_model not in prop_data.propellers:
            error("propeller %s not found in prop_data.py")

        self.raw_prop_data = prop_data.propellers[prop_model]

        # fit polynomials to the prop data
        self.poly_CT = self.fit_polynomial(self.raw_prop_data, 1, 5)
        self.poly_CP = self.fit_polynomial(self.raw_prop_data, 2, 6)
        self.poly_ETA = self.fit_polynomial(self.raw_prop_data, 3, 8)

    def fit_polynomial(self, data, column, order):
        '''fit and return a poly1d for a set of data, fitting column with an polynomial of the given order'''
        import numpy as np
        x = np.array([xx[0] for xx in data])
        y = np.array([xx[column] for xx in data])
        z = np.polyfit(x, y, order)
        return np.poly1d(z)

    def get_CT(self, J):
        '''return CT value'''
        return self.poly_CT(J)

    def get_CP(self, J):
        '''return CP value'''
        return self.poly_CP(J)

    def get_ETA(self, J):
        '''return ETA value'''
        return self.poly_ETA(J)

    def get_J_min(self):
        '''return smallest J in data'''
        return self.raw_prop_data[0][0]

    def get_J_max(self):
        '''return largest J in data'''
        return self.raw_prop_data[-1][0]

    def get_diameter_m(self):
        '''return prop diameter in meters'''
        return self.prop_dia_m

    def get_diameter_in(self):
        '''return prop diameter in inches'''
        return self.prop_dia_m/0.0254

    def get_pitch_in(self):
        '''return prop pitch in inches'''
        return self.prop_pitch_m/0.0254

    def get_mass(self):
        '''return propeller mass in Kg'''
        return self.prop_mass

    def get_efficiency(self):
        '''return prop efficiency'''
        return self.prop_eff

    def get_prop_model(self):
        '''return prop model string'''
        return self.prop_model

    def find_best_ETA(self, step):
        '''return the J corresponding to highest ETA'''
        J = self.get_J_min()
        max_J = self.get_J_max()
        best_J = J
        highest_ETA = self.get_ETA(J)
        while J < max_J:
            if self.get_ETA(J+step) > highest_ETA:
                best_J = J
            J += step
        return best_J
