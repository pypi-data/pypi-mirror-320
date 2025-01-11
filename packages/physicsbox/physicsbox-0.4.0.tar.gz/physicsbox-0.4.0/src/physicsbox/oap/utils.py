# -*- coding: utf-8 -*-
"""

Some utility functions shared by the OAP class with and without approximation.

Word on units:
    * at least at 1 point (E/H = vacuum impedance), maybe more, tied to SI 

Created on 2024-07-27

@author: Leonard.Doyle
"""

__all__ = [
    'cross_prod',
    'wrap',
    's_OAP',
    'z_OAP',
    'x_OAP',
    'f_parent',
    'cycle_average_poynting_vector',
    ]

import numpy as np


def cross_prod(Ax, Ay, Az, Bx, By, Bz):
    """Cartesian cross product of two vectors A and B
    with each 3 components x,y,z.
    All inputs can be either scalar or ndarray. If
    array, all six must be identical shape and the
    cross product will be taken element-wise.
    (This is why we are not using the numpy builtins.)

    Parameters
    ----------
    Ax : scalar or ndarray
        x-component of vector A
    Ay : scalar or ndarray
        y-component of vector A
    Az : scalar or ndarray
        z-component of vector A
    Bx : scalar or ndarray
        x-component of vector B
    By : scalar or ndarray
        y-component of vector B
    Bz : scalar or ndarray
        z-component of vector B

    Returns
    -------
    tuple (Cx, Cy, Cz) of scalar or ndarray
        If inputs are scalar, returns scalar tuple,
        else Cx, Cy and Cz each have same dimension
        as input.
    """
    Cx = Ay*Bz-Az*By
    Cy = Az*Bx-Ax*Bz
    Cz = Ax*By-Ay*Bx
    return Cx, Cy, Cz

def wrap(val, lower=0, higher=180):
    #lower = inclusive
    #higher = exclusive
    #needed a bit of trial and error to get there :)
    interval = higher-lower
    newval = (val + interval + lower) % interval + lower
    return newval

def s_OAP(x, y, f):
    return (x**2+y**2)/(4*f**2)

def z_OAP(x, y, f):
    s = s_OAP(x, y, f)
    z = s*f - f
    return z

def x_OAP(phi, f):
    #get x position given an angle phi in xz plane (y==0)
    tt = np.tan(phi-np.pi/2)
    return 2*f*(tt+np.sqrt(1+tt**2))

def f_parent(f_eff, theta_OAP):
    return f_eff/2*(1+np.cos(theta_OAP))

def cycle_average_poynting_vector(Ex, Ey, Ez, Hx, Hy, Hz):
    """
    Inputs:
    * complex E and H fields, x,y,z component each
    each component must have identical shape, but can be 1D, 2D or 3D grid

    Output:
    * 3 components of Sx, Sy, Sz of cycle averaged poynting vector
    """
    r"""
    Definitions:
        * Instantaneous intensity: time-dependence not cycle-averaged
            so displays "instantaneous field strength" but usually one is interested
            in the cycle-averaged intensity.
        * Instantaneous Poynting vector: no cycle-average, but limited physical
            meaning since rotates in space once per period
        * Cycle-average intensity: magnitude of the cycle-average Poynting vector,
            this is usually the definition of intensity
        * Cycle-averaged Poynting vector: take the cycle average (before taking the
            absolute value for intensity) of the Poynting vector

    Following Saleh+Teich - 2019 - Fundamentals of Photonics
    E(r,t) is a vectorial complex field of vector r and time t.
    Er(r,t) is the real part of said field
    E(r) is the complex field with time-dependence factored out with *exp(1j \omega t)
    -> E(r) is precisely what we get from the calculations above
    S is a vectorial but real quantity
    therefore

    S = Er(r,t) x Hr(r,t)
    = Re(E(r,t)) x Re(H(r,t))
    = Re(E(r) exp(j \omega t)) x Re(H(r) exp(j \omega t))
    = 1/2 (E exp(...) + E* exp(-...)) x 1/2 (H exp(...) + H* exp(-...))
    = ...
    = 1/4 [(ExH*) + (E*xH) + (ExH) exp(2j \omega t) + (E*xH*) exp(-2...)]
    = Re(1/2 (ExH*)) + Re(1/2 (ExH) exp(2j \omega t)) # check by reinserting Re()
    take the cycle average, note that first term is not time-dep and second
    term oscillates with (2\omega) so cycle average is zero:
        (<S> is still a vector, not the absolute value)
    <S> = Re(1/2 (ExH*)) + 0
        = Re(1/2 (ExH*))
    and finally the intensity:
    I = |<S>| = |Re(1/2 ExH*)|
    """


    EXHconjx, EXHconjy, EXHconjz = cross_prod(
        Ex, Ey, Ez, np.conj(Hx), np.conj(Hy), np.conj(Hz))

    Savg_x = 1/2 * np.real(EXHconjx)
    Savg_y = 1/2 * np.real(EXHconjy)
    Savg_z = 1/2 * np.real(EXHconjz)
    return (Savg_x, Savg_y, Savg_z)
