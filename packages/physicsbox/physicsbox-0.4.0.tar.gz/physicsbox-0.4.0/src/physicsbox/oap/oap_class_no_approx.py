# -*- coding: utf-8 -*-
"""

Based on the previous work detailed in `oap_class.py` and `oap_focus.py`
this script is a reimplementation using the non-approximated formulas from
the Zeng/Chen paper. This allows calculations also far outside the
focus region, e.g. at a plane far downstream or before focus.

To summarize:
    * Bahk paper: better explanations, more consistent, but only show explicit
      result with several approximations in place
    * Zeng/Chen paper: generally less clear, some steps may contain errors
      but they explicitly list an intermediate result which is useful since
      less/no-at-all approximated.

I confirmed the calculations are correct, see `FormulaNotebook.ipynb`. 

The derivations therein are used to calculate the script below.
Variable naming:
    * Tried to stick close to [1]
    * x,y, ... can sometimes be scalar, or a meshgrid of size NxN!
    * center ray: central ray of incoming circular beam
    * middle ray: half-angle ray between edge rays as in paper

Word on units:
    * at least at 1 point (E/H = vacuum impedance), maybe more, tied to SI 

Created on Tue Jun 20 23:03:24 2023

@author: Leonard.Doyle
"""

__all__ = [
    'UnapproximatedOAP',
]

import numpy as np
from numpy import pi #so common we might as well shorthand it
import scipy.constants as sc
try:
    from numba import njit, prange
except ImportError:
    import warnings
    warnings.warn('Cannot import numba, calculations will be very slow!'
                  ' Consider installing `numba` package.')
    def njit(*args, **kwargs):
        """Dummy njit decorator if numba is missing"""
        def decorator(func):
            return func 
        return decorator 
    prange = range # just use normal Python range

from physicsbox.utils import ImageCoordSys
from physicsbox.oap.utils import wrap, s_OAP, z_OAP, x_OAP, f_parent

@njit(cache=True, parallel=True)
def private_field_at_single(x_Q, y_Q, z_Q,
                     f, lam, dx,
                     z_alpha,
                     x_S, y_S, z_S,
                     E0x, E0y):
    """
    Input coords in global, unrotated coord system
    Output in global, unrotated coord sys
    
    separated from OAP class to allow numba jit, not supposed to be called
    from outside! use OAP class.field_at() instead
    """
    
    # *** scalars
    k = 2*pi/lam
    
    eta = sc.mu_0 * sc.c
    
    prefacE = 1j * dx**2 * np.exp(1j * k * z_alpha) / (2 * lam * f)
    prefacH = prefacE / eta
    
    # *** prefactors which only depend on S (surface) not on Q (observation)
    _exp_ikz = np.exp(-1j * k * z_S)
    
    # *** prefactors which depend on S and Q
    r_QS_x = x_S - x_Q
    r_QS_y = y_S - y_Q
    r_QS_z = z_S - z_Q
    Deltax = r_QS_x # delta is actually same as component of r_QS
    Deltay = r_QS_y
    Deltaz = r_QS_z
    r_QS = np.sqrt(r_QS_x**2 + r_QS_y**2 + r_QS_z**2)
    
    G = np.exp(1j * k * r_QS) / r_QS
    K = (1 - (1/(1j * k * r_QS))) / r_QS
    
    sumfacE = G * _exp_ikz
    sumfacH = sumfacE * K
    
    # *** E(Q) ***
    _Ex1 = (2*f - x_S * K * Deltax) * E0x
    _Ex2 = (y_S * K * Deltax) * E0y
    Ex = _Ex1 - _Ex2
    Ex *= sumfacE
    Ex = Ex.sum()
    Ex *= prefacE
    
    _Ey1 = (2*f - y_S * K * Deltay) * E0y
    _Ey2 = (x_S * K * Deltay) * E0x
    Ey = _Ey1 - _Ey2
    Ey *= sumfacE
    Ey = Ey.sum()
    Ey *= prefacE
    
    _Ez1 = (1 - K * Deltaz)
    _Ez2 = x_S * E0x + y_S * E0y
    Ez = _Ez1 * _Ez2
    Ez *= sumfacE
    Ez = Ez.sum()
    Ez *= prefacE
    
    # *** H(Q) ***
    _Hx1 = (-x_S * Deltay) * E0x
    _Hx2 = (2*f * Deltaz - y_S * Deltay) * E0y
    Hx = _Hx1 + _Hx2
    Hx *= sumfacH
    Hx = Hx.sum()
    Hx *= prefacH
    
    _Hy1 = (x_S * Deltax - 2*f * Deltaz) * E0x
    _Hy2 = (y_S * Deltax) * E0y
    Hy = _Hy1 + _Hy2
    Hy *= sumfacH
    Hy = Hy.sum()
    Hy *= prefacH
    
    _Hz1 = (2*f * Deltay) * E0x
    _Hz2 = (2*f * Deltax) * E0y
    Hz = _Hz1 - _Hz2
    Hz *= sumfacH
    Hz = Hz.sum()
    Hz *= prefacH
    
    return (Ex, Ey, Ez, Hx, Hy, Hz)

class UnapproximatedOAP:
    def __init__(self, f_eff, theta_deg, r_beam, choose_center_ray=True):
        """Initialize an OAP class instance with the given geometry to
        prepare for focus calculations.
        In contrast to the main "OAP" class of this package, one less
        approximation is made in this code. While the main class is
        limited to calculations "close to focus", this restriction
        should not apply here. (At least in terms of the maths,
        actually numerically it was challenging to get results away
        from focus simple because huge input grids are necessary and
        some similar troubles.)
        This initialization does not compute anything big, so is fast.
        The main purpose is to have all important aspects of the
        geometry pre-defined so we can make use of helper functions and
        so on.

        Parameters
        ----------
        f_eff : float
            effective focal length
        theta_deg : float
            off-axis angle in degrees
        r_beam : float
            beam radius of input beam
        choose_center_ray : bool, optional
            If True, geometry aligned to center ray, else to mid ray,
            by default True
        """
        self.f_eff = f_eff
        self.theta_deg = theta_deg
        self.theta = np.deg2rad(theta_deg)
        self.r_beam = r_beam
        self.choose_center_ray = choose_center_ray
        
        
        self.f_parent = f_parent(f_eff, self.theta)
        f = self.f_parent #shorthand
        self.f = f
        h = x_OAP(self.theta, f)
        self.h = h
        
        self.f_number = f_eff/(2*r_beam)
             
        xplus = h+r_beam
        xminus = h-r_beam
        xcenter = h
        zplus =  z_OAP(xplus, 0, f)
        zminus =  z_OAP(xminus, 0, f)
        zcenter =  z_OAP(xcenter, 0, f)
        #want positive angle if z negative and x pos:
        self.phiplus_deg = wrap(np.rad2deg(np.arctan(-xplus/zplus))) 
        self.phiminus_deg = np.rad2deg(np.arctan(-xminus/zminus))
        if xminus > 0:
            #if beam completely at x > 0, angles all positive
            #if (partially) on-axis parabola, xminus will be negative and angle
            # is supposed to be negative, no wrap!
            self.phiminus_deg = wrap(self.phiminus_deg)
        self.phimid_deg = (self.phiplus_deg+self.phiminus_deg)/2 #mean
        self.phimid = np.deg2rad(self.phimid_deg)
        self.phicenter=self.theta # by definition
        self.phicenter_deg=self.theta_deg
        
        self.xplus = xplus
        self.xminus = xminus
        self.xcenter = xcenter
        self.zplus = zplus
        self.zminus = zminus
        self.zcenter = zcenter
        
        
        self.xmid = x_OAP(self.phimid, f)
        self.zmid = z_OAP(self.xmid, 0, f)
        
        if choose_center_ray:
            phi = self.theta
        else:
            phi = self.phimid
        self.phi = phi
        
        #alpha = plane of incident wave, must be above OAP
        self.z_alpha = max(0, self.zplus) + f
        
        self.E0x = None
        self.E0y = None
        self.dx = 1
        self.x = None
        self.y = None
        self.z = None
        self.s = None
        self.p = None
        self.q = None
        self.m = None

    def assign_input_field(self, E0x, E0y, dx, lam):
        #assuming a regular grid which is centered at 0,0 in the center
        # of the image specified and spacing dx in real units (pref. SI)
        # calculate and return the X and Y coordinate for each pixel in the
        # parent parabola frame
        #assert E0x.shape == E0y.shape
        self.E0x = E0x
        self.E0y = E0y
        self.lam = lam
        self.k = 2*pi/lam
        
        cc = ImageCoordSys(E0x, dx)
        x, y = cc.mgrid_xy #in coordinates of the input beam, not global!
        x += self.h #center of input beam must be at h
        self.x = x
        self.y = y
        self.dx = dx
        
        f = self.f
        phi = self.phi
        self.s = s_OAP(x, y, f)
        s = self.s
        z = z_OAP(x, y, f)
        self.z = z
        self.p = -(x*np.cos(phi)+z*np.sin(phi))/(1+s)/f
        self.q = -y/(1+s)/f
        self.m = -(x*np.sin(phi)-z*np.cos(phi))/(1+s)/f
        
        #NB: float division is slower than float multiplication!
        # https://stackoverflow.com/questions/57325403/speed-of-elementary-mathematical-operations-in-numpy-python-why-is-integer-divi

    def field_at(self, xp, yp, zp, callback=None):
        """
        Calculate the complex fields Ex', Ey', Ez', Hx', Hy', Hz'
        in the primed frame of reference given the array of input coordinates
        x' and y' at distance z' from focus.

        Parameters
        ----------
        xp : scalar or ndarray
            Position at which to evaluate the field.
        yp : scalar or ndarray
            Like x, must have same shape.
        zp : scalar
            Distance z' from focus.
        callback : method
            If calculating many xp,yp, will emit callback for every calculated
            coordinate. Use e.g. with tqdm.update()

        Returns
        -------
        None.

        """
        # check inputs
        assert np.isscalar(zp) # restrict to 2D plane in output coord sys for now
        if np.isscalar(xp):
            assert np.isscalar(yp)
        else:
            assert xp.shape == yp.shape

        x = xp * np.cos(self.phi) - zp * np.sin(self.phi)
        y = yp
        z = xp * np.sin(self.phi) + zp * np.cos(self.phi)
        
        if np.isscalar(xp):
            Ex, Ey, Ez, Hx, Hy, Hz = self._field_at_single(x, y, z)
        else:
            # since the input field E0x, E0y is already a matrix,
            # it seems to complicated (and maybe not even feasible)
            # to use numpy vectorization. Instead, to avoid headaches,
            # use a python loop and get the field for each individual
            # coordinate in the target plane.
            # Optimization can always be done even without vectorization    
            
            Ex = np.zeros(x.shape, dtype=complex)
            Ey = np.zeros_like(Ex)
            Ez = np.zeros_like(Ex)
            Hx = np.zeros_like(Ex)
            Hy = np.zeros_like(Ex)
            Hz = np.zeros_like(Ex)
            
            N_y, N_x = x.shape # row-major means y coordinate first usually
            for iy in range(N_y):
                for jx in range(N_x):
                    _x = x[iy, jx]
                    _y = y[iy, jx]
                    _z = z[iy, jx]
                    
                    _Ex, _Ey, _Ez, _Hx, _Hy, _Hz = self._field_at_single(_x, _y, _z)
                    
                    Ex[iy, jx] = _Ex
                    Ey[iy, jx] = _Ey
                    Ez[iy, jx] = _Ez
                    
                    Hx[iy, jx] = _Hx
                    Hy[iy, jx] = _Hy
                    Hz[iy, jx] = _Hz
                    if callback:
                        callback()
            
        Epx =  Ex * np.cos(self.phi) + Ez * np.sin(self.phi)
        Epy =  Ey
        Epz = -Ex * np.sin(self.phi) + Ez * np.cos(self.phi)
        
        Hpx =  Hx * np.cos(self.phi) + Hz * np.sin(self.phi)
        Hpy =  Hy
        Hpz = -Hx * np.sin(self.phi) + Hz * np.cos(self.phi)
        return (Epx, Epy, Epz, Hpx, Hpy, Hpz) #rotated in K'!

    def _field_at_single(self, x_Q, y_Q, z_Q):
        assert np.isscalar(x_Q)
        assert np.isscalar(y_Q)
        assert np.isscalar(z_Q)
        
        return private_field_at_single(x_Q, y_Q, z_Q,
                                self.f, self.lam, self.dx,
                                self.z_alpha,
                                self.x, self.y, self.z,
                                self.E0x, self.E0y)

