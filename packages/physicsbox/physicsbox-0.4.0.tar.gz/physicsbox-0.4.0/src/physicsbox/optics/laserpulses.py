# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 18:03:45 2021

@author: Leonard.Doyle
"""

import numpy as np
import scipy.constants as sc

from ..units import m, cm, mm, um, nm, J, s, ms, us, ps, fs

from .gaussbeams import z_Rayleigh, fwhm2waist, fwhm2tau
from .utilities import lam2nu, lam2omega, f_number, NA_from_fNo, \
    airyFWHM_from_airyRad, airyRad_from_fNo, Ppeak_from_Etot, \
        Ipeak_from_Ppeak, E_from_Ipeak, Nphotons_from_Etot, a0_from_E

class LaserPulseParameters:
    """
    This class provides a simple structure to generate an object holding
    the laser pulse parameters necessary to completely characterize a 
    high intensity laser pulse. Some attributes are read/write, while others
    will be only the resulting parameters given the base parameters.
    """
    def __init__(self, lam=800*nm, tauFWHM= 25*fs, beam_diam=280*mm, f=1500*mm,
                 Etot=1*J):
        
        """All in SI"""
        
        """Pulse parameters"""
        self.lam = lam            #[m] central wavelength
        self.tauFWHM = tauFWHM    #[s] Gaussian FWHM pulse duration
        self.tau = fwhm2tau(self.tauFWHM) #[s]
        
        self.nu = lam2nu(lam)        #[Hz] optical frequency
        self.omega = lam2omega(lam)  #[2piHz] angular frequency
        self.period = 1/self.nu      #[s] one optical cycle duration
        
        """Spatial parameters"""
        #first we can calc diffraction limit for flat top beam diam
        self.beam_diam = beam_diam
        self.f = f
        
        self.f_no = f_number(self.f, self.beam_diam)
        self.NA = NA_from_fNo(self.f_no)
        
        self.airy_radius = airyRad_from_fNo(self.f_no, self.lam)
        self.airy_fwhm = airyFWHM_from_airyRad(self.airy_radius)
        self.gauss_fwhm = self.airy_fwhm #half reasonable assumption...
        self.gauss_w0 = fwhm2waist(self.gauss_fwhm)
        self.z_R = z_Rayleigh(self.gauss_w0, self.lam)
        
        #given a waist, we can give Rayleigh range, divergence angle (F-#)
        # w0 = 3*um #[m] for 800nm, this is f/5 focussing or so, nothing unbelievable
        self.focal_area = np.pi*(self.gauss_fwhm/2)**2 #simplified power-over-area estimate
        
        """Power and intensity parameters"""
        #from Ipeak to Epeak, Power
        self.Etot = Etot
        self.Ppeak = Ppeak_from_Etot(self.Etot, self.tauFWHM)
        self.Ipeak = Ipeak_from_Ppeak(self.Ppeak, self.lam, self.f,
                                      self.beam_diam)

        self.E0 = E_from_Ipeak(self.Ipeak)
        self.B0 = self.E0/sc.c
        self.a0 = a0_from_E(self.E0, self.lam)
        self.Nphot = Nphotons_from_Etot(self.Etot, self.lam)
        
        