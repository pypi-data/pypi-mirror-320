# -*- coding: utf-8 -*-
"""

Simple field definitions to use in simulations.
To make the code more universal, all should follow the same structure:
    The constructor takes any parameters that define the field, these will
    stay unchanged.
    Each field should implement a method "field_at" which takes a xyz tuple and
    possibly a time t and returns the vecorial field value at the given
    coordinates.
    All units in SI
    All functions should accept either a tuple, list or numpy array of
        length 3. Support for a numpy 2d array with size Nx3 is not given.
    Return values will always be simple python tuples for now.

Created on Mon Nov 11 16:06:35 2019

@author: Leonard.Doyle
"""

import numpy as np
    
class ConstantVectorialField:
    """Vectorial field of constant value (inside given box region).
    If box of size 0 is specified, inside value will be used globally,
    else "value" is used inside and "outvalue" outside of bounds.
    limits have to be ordered (min, max)."""
    def __init__(self, value = (0.0, 0.0, 0.0),
                 xlim = (0.0, 0.0), ylim = (0.0, 0.0), zlim = (0.0, 0.0),
                 outvalue=(0.0, 0.0, 0.0)):
        self.fieldvalue = value
        self.outvalue = outvalue
        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim
        self.polarization = 1#dummy
    
    def field_at(self, xyz, t=0):
        """Return the vectorial field quantity at [x,y,z] and t (omit t if
        time-independent), all in SI units. Time given for compatibility with
        potentially time-dependent fields.
        """
        x,y,z = xyz #unpack vector into x, y and z
        retval = self.fieldvalue #default return is inside value
        
        if (self.xlim[1]-self.xlim[0] > 0 and
            self.ylim[1]-self.ylim[0] > 0 and
            self.zlim[1]-self.zlim[0] > 0): #limits valid
            if (x < self.xlim[0] or x > self.xlim[1] or
                y < self.ylim[0] or y > self.ylim[1] or
                z < self.zlim[0] or z > self.zlim[1]):
                #if any one coordinate lies outside, others don't matter
                retval = self.outvalue
        #else: box is of size 0 or invalid (limits swapped) -> use inside val
        
        return retval
    
    def real_field_at(self, xyz, t):
        """Return the physical (real valued) field at cartesian point (x,y,z)
        at time t."""
        return np.real(self.field_at(xyz, t))