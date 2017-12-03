#!/usr/bin/env python

import sys

# physical constants
gravity = 9.80665 # acceleration due to gravity (m/s^2)
rho = 1.225 # air density Kg/m^3

def error(msg):
    '''display an error and exit'''
    print("Error: %s" % msg)
    sys.exit(1)

# a simple structure class
# see https://stackoverflow.com/questions/2280334/shortest-way-of-creating-an-object-with-arbitrary-attributes-in-python
class struct:
   def __init__(self, **kwargs):
       self.__dict__.update(kwargs)

