#!/usr/bin/env python

'''
battery model class
'''

from util import error

batteries = {}

class battery_cell(object):
    def __init__(self, energy_density, mass, voltage_max, voltage_min, packaging_factor, age_factor):
        self.energy_density = energy_density     # Wh/Kg
        self.mass = mass                         # Kg
        self.voltage_max = voltage_max           # Volts
        self.voltage_min = voltage_min           # Volts
        self.packaging_factor = packaging_factor # extra mass ratio due to packaging
        self.age_factor = age_factor             # reduction in Gravimetric energy due to aging

###################################
# battery setup for 5Ah 6S nanotech
batteries['5Ah_6S_Nanotech'] = battery_cell(
    energy_density = 194,
    mass = 0.095,
    voltage_max = 4.15,
    voltage_min = 3.1,
    packaging_factor = 1.0,
    age_factor = 0.85)

###########################################
# cell model for Panasonic NCR18650GA cells
batteries['NCR18650GA'] = battery_cell(
    energy_density = 224,
    mass = 0.048,
    voltage_max = 4.15,
    voltage_min = 2.7,
    packaging_factor = 0.9,
    age_factor = 0.85)


class battery(object):
    '''model a battery setup'''

    def __init__(self, battery_type, n_series, n_parallel):
        if battery_type not in batteries:
            error("Unknown battery type %s. Choices are %s" % (battery_type, batteries.keys()))
        self.battery_type = battery_type
        self.cell_series_count = n_series
        self.cell_parallel_count = n_parallel
        self.cell = batteries[self.battery_type]
        self.cell_count_total = self.cell_parallel_count*self.cell_series_count
        
    def get_mass(self):
        '''return total mass in Kg'''
        return self.cell_count_total * self.cell.mass / self.cell.packaging_factor

    def get_energy_density(self):
        '''return energy density in Wh/Kg'''
        return self.cell.energy_density * self.cell.packaging_factor * self.cell.age_factor

    def get_voltage_min(self):
        '''return overall voltage at min charge'''
        return self.cell.voltage_min * self.cell_series_count

    def get_voltage_max(self):
        '''return overall voltage at max charge'''
        return self.cell.voltage_max * self.cell_series_count

    def get_cell_total(self):
        '''return total cell count'''
        return self.cell_count_total

    def get_cell_current(self, power_watts, voltage):
        '''return cell current for a given power level'''
        amps = power_watts / voltage
        return amps / self.cell_parallel_count

    def get_description(self):
        '''return battery type string'''
        return "%s (%uS %uP) " % (self.battery_type, self.cell_series_count, self.cell_parallel_count)

    def get_watt_hours(self):
        '''return battery capacity in Watt hours'''
        return self.get_mass() * self.get_energy_density()
