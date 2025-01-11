# -*- coding: utf-8 -*-
r"""


Some forumlae:
    Etot = m c**2 = \gamma m_0 c**2 = sqrt((p c)**2+(m_0 c**2)**2)
    Ekin = Etot- m_0 c**2 (rest mass energy) = (\gamma-1) m_0 c**2
    \gamma = sqrt(1+(|p|/(m_0 c))**2) = 1/sqrt(1-\beta**2)
    \beta = v/c
"""


import numpy as np
import scipy.constants as sc
from scipy.constants import c

def Ekin_from_p(vec_p, mass):
    """For a single 3-vector momentum and particle mass, return the kinetic
    energy in Joule. using relativistic formula."""
    gamma = gamma_from_p(vec_p, mass)
    Ekin = (gamma-1)*mass*c**2
    return Ekin

def p_from_Ekin(Ekin, mass):
    E0 = mass*c**2
    Etot = Ekin + E0
    p_squared = 1/c**2*(Etot**2-E0**2)
    return np.sqrt(p_squared)

def v_from_p(vec_p, mass):
    p_abs = np.linalg.norm(vec_p)
    aa = (mass*c**2)**2 + (p_abs*c)**2 #derived via total Energy E=ymc^2
    vec_v = vec_p*c**2 / np.sqrt(aa)
    return vec_v

def beta_from_p(vec_p, mass):
    return v_from_p(vec_p, mass) / c

def gamma_from_p(vec_p, mass):
    p_abs = np.linalg.norm(vec_p)
    return np.sqrt(1+(p_abs/(mass*c))**2)

def Ekin_from_p_arr(vec_p, mass):
    """For a single 3-vector momentum and particle mass, return the kinetic
    energy in Joule. using relativistic formula."""
    gamma = gamma_from_p_arr(vec_p, mass)
    Ekin = (gamma-1)*mass*c**2
    return Ekin

def v_from_p_arr(vec_p, mass):
    p_abs = np.linalg.norm(vec_p, axis =1)
    aa = (mass*c**2)**2 + (p_abs*c)**2 #derived via total Energy E=ymc^2
    vec_v = vec_p*c**2 / np.sqrt(aa[:,np.newaxis])
    return vec_v

def gamma_from_p_arr(vec_p, mass):
    p_abs = np.linalg.norm(vec_p, axis=1)
    return np.sqrt(1+(p_abs/(mass*c))**2)
