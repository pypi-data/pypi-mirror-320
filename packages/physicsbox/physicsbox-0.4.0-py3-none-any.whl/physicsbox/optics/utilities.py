# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:56:49 2019

@author: Leonard.Doyle

"""

import numpy as np
import scipy.constants as sc

lam2k = lambda lam: 2*np.pi/lam
k2lam = lambda k: 2*np.pi/k
lam2omega = lambda lam: 2*np.pi*sc.c/lam
lam2nu = lambda lam: sc.c/lam


def tauFWHM2delta_nu(tauFWHM):
    """Given the tau_FWHM duration in intensity, give FWHM power spectral
    bandwidth (of specturm squared!) useful to estimate wavelength bandwidth.
    """
    delta_nu_FWHM = 4*np.log(2)/(2*np.pi)/tauFWHM
    return delta_nu_FWHM

def delta_nu2delta_lam(delta_nu, lam0):
    """Given frequency bandwidth delta_nu_FWHM in intensity/power spectrum
    (squared of field spectrum/Fourier transform!) and center wavelength lam0,
    approximate delta lambda FWHM (power spectrum). Approximated by error
    propagation assumption
    delta_x = del(f)/del(y)*delta_y.
    """
    #not my original source, but result comparable to
    # http://toolbox.lightcon.com/tools/tbconverter/
    delta_lam = lam0**2/sc.c*delta_nu #actually has -1, but here use abs()
    return delta_lam


def Ppeak_from_Etot(Etot, tauFWHM, pulse='gauss'):
    """
    Calculate the peak laser pulse power from the total pulse energy Etot [J],
    and the pulse FWHM duration tauFWHM [s] (measured in intensity FWHM).
    If pulse='gauss' is used, a correction factor is applied to correctly 
    calculate Ppeak via
    Etot = Integrate[Ppeak * Exp[-4 ln2 t^2/tauFWHM^2],{t,-Inf,Inf}]
         = Ppeak * tauFWHM * sqrt(pi/(4 ln2))
    -> Ppeak ~~ 0.94 * Etot / tauFWHM
    If pulse='rect' is used, a step pulse is assumed with power Ppeak and
    duration tauFWHM, such that
    Ppeak = Etot / tauFWHM

    Parameters
    ----------
    Etot : float
        Total pulse energy in [J]
    tauFWHM : float
        FWHM pulse duration (measured in intensity FWHM)
    pulse : str, optional
        'gauss' or 'rect'. The default is 'gauss'.

    Returns
    -------
    Ppeak in [W]

    """
    if pulse=='gauss':
        Ppeak = Etot / tauFWHM
        Ppeak /= np.sqrt(np.pi/4/np.log(2))
    elif pulse=='rect':
        Ppeak = Etot / tauFWHM
    else:
        raise ValueError(f'Invalid argument for pulse: {pulse}')
    return Ppeak

def Ipeak_from_Ppeak(Ppeak, lam, f, D):
    """
    For a flat top intensity beam of diameter D, focused to the
    diffraction limited spot size (airy disk) by a focusing optic of
    focal length f, calculate the peak intensity Ipeak.
    The focal spot size and therefore Ipeak depends on the wavelength lam.
    
    Instead of using the airy disk area pi*r0^2, use exact analytical integral
    relation for Ipeak of the airy disk.
    In focal plane (airy disk):
        P = Integrate[I dA] = Integrate[Iairy(r) * r dr dphi]
             = 2pi * Integrate[Iairy(r) * r,{r,0,Inf}]
        where P = total in area, peak in time -> call it Ppeak
    and equate this with Ipeak = Iairy(r=0):
        Ipeak = pi/4 * Ppeak * (D/(lam*f))^2
    
    Parameters
    ----------
    Ppeak : float
        Peak power of pulse in [W = J/s]
    lam : float
        Central wavelength of the pulse [m]
    f : float
        Focal length of focussing optic [m]
    D : float
        Beam diameter of flat top input beam [m]

    Returns
    -------
    Ipeak in [W/m^2] (SI units)

    """
    Ipeak = np.pi/4 * Ppeak * (D / (lam*f))**2
    return Ipeak
    

def E_from_Ipeak(Ipeak):
    """E0 amplitude for complex notation E(r,t)=E0 exp(i(k r-omega t))"""
    return np.sqrt(2/(sc.epsilon_0 * sc.c)*Ipeak)


def f_number2airy_radius(f_num, lam):
    """Calculate the airy disk radius (radius at first minimum!) assuming
    flat top irradiation with wavelength lam of a lens of given f_number."""
    return 1.22*lam*f_num

def airy_rad2airy_FWHM(r_airy):
    """Calculate airy disk FWHM (in intensity) given the radius of
    first minimum r_airy"""
    #airy rad= 1.22 lam f/D
    #airy FWHM=1.03 lam f/D
    return r_airy / 1.22 * 1.03


def f_number(f, beam_diam):
    """Calculate the f-Number for a given focal length and beam diameter.
    Read as f/(returned number)"""
    return f / beam_diam

def NA_from_fNo(f_num):
    """Return the Numerical aperture (NA) for a given f_number"""
    return np.sin(np.arctan(1/(2*f_num)))

f_number2NA = NA_from_fNo

def airyRad_from_fNo(f_num, lam):
    """Calculate the airy disk radius (radius at first minimum!) assuming
    flat top irradiation with wavelength lam of a lens of given f_number."""
    return 1.22*lam*f_num

def airyFWHM_from_airyRad(r_airy):
    #airy rad= 1.22 lam f/D
    #airy FWHM=1.03 lam f/D
    return r_airy / 1.22 * 1.03

def I_from_E(E_field):
    """Input number or vector as real E-field [V/m] and calculate
    "instantaneous" intensity."""
    return 1/2*sc.epsilon_0*sc.c*E_field**2

def a0_from_E(E0, lam):
    omega_L = lam2omega(lam)
    return sc.e*E0 / (omega_L*sc.m_e*sc.c)

def Nphotons_from_Etot(Etot, lam):
    """Assuming all photons have an energy corresponding to the central
    wavelength lambda, the number of of photons is just Etot/Ephot.
    """
    Ephot = sc.h*sc.c/lam
    return Etot/Ephot

