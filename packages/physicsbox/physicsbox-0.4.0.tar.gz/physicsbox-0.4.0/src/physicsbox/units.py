# -*- coding: utf-8 -*-
"""
Handfull of prefixes and units meant to be star-imported in other files.
Example usage:
    
    from physicsbox.units import *
    
    L = 200*um
    V = L**3
    
    plt.plot(x/um,...) #to get plot scale in [um]
    plt.set_xlim(0,L/um) #to get plot scale in [um]

Atlernative usage to avoid polluting namescpace:
    
    from physicsbox import units as u
    
    L = 200*u.um
    V = L**3
    
    plt.plot(x/u.um,...) #to get plot scale in [um]
    plt.set_xlim(0,L/u.um) #to get plot scale in [um]

Created on Mon Nov 11 15:48:32 2019

@author: Leonard.Doyle
"""

from math import pi
import scipy.constants as _sc #avoid unnoticed re-import

m = 1 #caution, do not use m again for mass, loop index, ...!
cm = 1e-2*m
mm = 1e-3*m
um = 1e-6*m
nm = 1e-9*m
pm = 1e-12*m
fm = 1e-15*m

inch = 25.4*mm

rad = 1
mrad = 1e-3*rad
urad = 1e-6*rad
deg = 2*pi/360

s = 1
ms = 1e-3*s
us = 1e-6*s
ns = 1e-9*s
ps = 1e-12*s
fs = 1e-15*s

Pa = 1 #in SI
hPa = 100*Pa
mbar = hPa
bar = 1e3*mbar
# bar=1e5         #Bar in Pascal=SI units
# mbar=1e-3*bar

J = 1 #Joule in SI units
mJ = 1e-3*J
uJ = 1e-6*J
nJ = 1e-9*J

W = 1
kW = 1e3*W
MW = 1e6*W
GW = 1e9*W
TW = 1e12*W
PW = 1e15*W

V = 1
uV = 1e-6*V
mV = 1e-3*V
kV = 1e3*V
MV = 1e6*V

T = 1 # Tesla
uT = 1e-6*T
mT = 1e-3*T

eV = _sc.e*V #eV in SI units
meV = 1e-3*eV
keV = 1e3*eV
MeV = 1e6*eV
GeV = 1e9*eV

K = 1 # Kelvin
