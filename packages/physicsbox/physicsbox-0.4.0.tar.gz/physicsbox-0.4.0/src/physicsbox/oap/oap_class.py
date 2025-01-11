# -*- coding: utf-8 -*-
"""

Pack all the OAP calculations into a separate class for re-use.

Details see `FormulaNotebook.ipynb`.

Word on units:
    * at least at 1 point (E/H = vacuum impedance), maybe more, tied to SI 

Created on Tue Feb  1 15:21:15 2022

@author: Leonard.Doyle
"""

__all__ = [
    'OAP',
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
    
try:
    from numba_progress import ProgressBar
except ImportError:
    import warnings
    warnings.warn('Cannot import numba_progress, will not show progress bar'
                  ' during simulation. Consider installing `numba-progress` package.')
    ProgressBar = None

from physicsbox.utils import ImageCoordSys
from physicsbox.oap.utils import wrap, s_OAP, z_OAP, x_OAP, f_parent

_eta = sc.mu_0*sc.c #vacuum impedance in SI

@njit(cache=True, parallel=True)
def _numba_field_at_point_unprimed(xpf, ypf, zpf,
                                    lam, dx,
                                    p, q, m,
                                    termEx, termEy, termEz,
                                    termHx, termHy, termHz):
    """For numba optimization, function must not depend
    on Python object class instances like self. Only
    numeric types allowed. Therefore, make this
    function external from class but hopefully call
    it at high speed."""
    # input x', y', z' but output Ex Ey Ez in unprimed coords
    # converted to prime in public methods below.
    k = 2*pi/lam
    
    #coordinates near focus in primary coord sys (not used in calc!)
    # xf = xpf*np.cos(phi) - zpf*np.sin(phi)
    # yf = ypf
    # zf = xpf*np.sin(phi) + zpf*np.cos(phi)
    
    #since distances do not depend on choice of coord sys, use whichever makes
    # most sense, in case of exp(ik phi) this is the rotated one
    
    _kp = k*(xpf*p + ypf*q + zpf*m)
    eikp = np.exp(1j*_kp)
    
    #NB: Paper does integration in dp, dq. These seem the natural choice in
    # "direction cosines", but in fact is just a re-writing (incl. Jacobian)
    # of the integral in dx, dy.
    # Since the grid is non-uniform in dp, dq, but uniform in dx, dy, here we chose
    # to integrate over dx, dy.
    #TODO as a double check, integrate with a rough guess for dp, dq size in p, q
    # or use griddata to go to uniform p, q grid. Should yield same result.
    
    _tEx_eikp = termEx * eikp
    _tEy_eikp = termEy * eikp
    _tEz_eikp = termEz * eikp
    
    _tHx_eikp = termHx * eikp
    _tHy_eikp = termHy * eikp
    _tHz_eikp = termHz * eikp

    #TODO replace with trapz rule for accuracy
    prefac = 1j/lam * dx**2
    Ex = prefac * _tEx_eikp.sum()
    Ey = prefac * _tEy_eikp.sum()
    Ez = prefac * _tEz_eikp.sum()
    
    Hx = prefac * _tHx_eikp.sum()
    Hy = prefac * _tHy_eikp.sum()
    Hz = prefac * _tHz_eikp.sum()
    return (Ex, Ey, Ez, Hx, Hy, Hz)

@njit(cache=True, parallel=True)
def _numba_unprimed_field_on_xy_grid(xpv, ypv, zp0,
                     lam, dx,
                     p, q, m,
                     termEx, termEy, termEz,
                     termHx, termHy, termHz,
                     Exout, Eyout, Ezout,
                     Hxout, Hyout, Hzout,
                     progressbar_proxy,
                     ):
    # Specify input vector x' and y', at distance z'_0 from focus
    # so len(xpv)=M, len(ypv)=N, zp0=scalar
    # returns tuple (E'x, E'y, E'z, H'x, H'y, H'z) each with shape NxM (y first!)
    #E'_foc(x',y') along new optical axis of mid-ray/center-ray
    # (depending on coice above)

    # cannot allocate memory inside numba function, must pass
    # in by reference and modify in-place
    # Ex = np.zeros((len(ypv), len(xpv)), dtype=complex)
    # Ey = np.zeros_like(Ex)
    # Ez = np.zeros_like(Ex)

    # Hx = np.zeros_like(Ex)
    # Hy = np.zeros_like(Ex)
    # Hz = np.zeros_like(Ex)

    for iy in prange(len(ypv)):
        if progressbar_proxy is not None:
            progressbar_proxy.update(1)
        for jx in prange(len(xpv)):
            #coordinates near focus in rotated coord sys
            xpf = xpv[jx]
            ypf = ypv[iy]
            
            _Ex, _Ey, _Ez, _Hx, _Hy, _Hz = _numba_field_at_point_unprimed(
                xpf, ypf, zp0, lam, dx,
                p, q, m, termEx, termEy, termEz,
                termHx, termHy, termHz)
            Exout[iy, jx] = _Ex
            Eyout[iy, jx] = _Ey
            Ezout[iy, jx] = _Ez
            
            Hxout[iy, jx] = _Hx
            Hyout[iy, jx] = _Hy
            Hzout[iy, jx] = _Hz
    
    # Epx, Epy, Epz = self.convert_global_to_prime(Ex, Ey, Ez)
    # Hpx, Hpy, Hpz = self.convert_global_to_prime(Hx, Hy, Hz)
    return None


class OAP:
    def __init__(self, f_eff, theta_deg, r_beam, choose_center_ray=True):
        """Initialize an OAP class instance with the given geometry to
        prepare for focus calculations.
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
        self.r_beam = r_beam
        self.choose_center_ray = choose_center_ray
        self.F_number = f_eff/(2*r_beam)
        self.NA = np.sin(np.arctan(1/(2*self.F_number))) #TODO neglects asymmetry by
        # off-axis angle (which in general will make the required NA larger)
        # as well as edge ray for square beams/optics.
        
        self.theta = np.deg2rad(theta_deg)
        
        self.f_parent = f_parent(f_eff, self.theta)
        f = self.f_parent #shorthand
        self.f = f
        self.f_p = self.f_parent # another shorthand
        h = x_OAP(self.theta, f)
        self.h = h # offset between incoming beam center ray and origin
             
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
        #phicenter=Theta_OAP_deg by definition

        #alternative NA definition:
        # use marginal rays for worst case NA
        # TODO still neglects square beam deviation in corners
        # TODO check if it breaks down if crossing the z axis
        full_opening_cone = np.deg2rad(np.abs(self.phiplus_deg - self.phiminus_deg))
        self.NA2 = np.sin(full_opening_cone/2) # definition only uses half-angle

        
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
        self.zalpha = max(0, self.zplus) + f
        
        self.E0 = None
        self.dx = 1
        self.x = None
        self.y = None
        self.z = None
        self.s = None
        self.p = None
        self.q = None
        self.m = None

    def assign_input_field(self, E0x, E0y, dx):
        #assuming a regular grid which is centered at 0,0 in the center
        # of the image specified and spacing dx in real units (pref. SI)
        # calculate and return the X and Y coordinate for each pixel in the
        # parent parabola frame
        #assert E0x.shape == E0y.shape
        self.E0x = E0x
        self.E0y = E0y
        
        cc = ImageCoordSys(E0x, dx)
        x, y = cc.mgrid_xy #in coordinates of the input beam, not global!
        x += self.h #center of input beam must be at h
        self.x = x
        self.y = y
        self.dx = cc.dx
        
        
        #Precalculate stuff here before loop to save time
        #2D arrays as arguments to 2D xy-Integral:

        f = self.f
        phi = self.phi
        self.s = s_OAP(x, y, f)
        s = self.s
        z = z_OAP(x, y, f)
        self.z = z

        _r_S = f*(1+s) #shorthand used often
        self.p = -(x*np.cos(phi)+z*np.sin(phi))/_r_S
        self.q = -y/_r_S
        self.m = -(-x*np.sin(phi)+z*np.cos(phi))/_r_S
        
        #not necessary if only performing dx, dy integration, see notes below
        # _t1 = (p + np.sin(phi))**2
        # _t2 = (mmm + np.cos(phi))**2
        # _t3 = (p*np.cos(phi) - mmm*np.sin(phi))**2
        # _t4 = (1 + p*np.sin(phi) + mmm*np.cos(phi))**4
        # Jac = 4*f**2*(_t1+_t2-_t3) / (mmm*_t4)
        
        #NB: float division is slower than float multiplication!
        # https://stackoverflow.com/questions/57325403/speed-of-elementary-mathematical-operations-in-numpy-python-why-is-integer-divi

        _tEx_E0x = 1/_r_S - x**2/(2*f*_r_S**2)
        _tEx_E0y = -x*y/(2*f*_r_S**2)
        _tEx = (E0x*_tEx_E0x + E0y*_tEx_E0y) #implicitly complex
        self._tEx = _tEx

        _tEy_E0x = -x*y/(2*f*_r_S**2)
        _tEy_E0y = 1/_r_S - y**2/(2*f*_r_S**2)
        _tEy = (E0x*_tEy_E0x + E0y*_tEy_E0y) 
        self._tEy = _tEy
        
        _tEz = (x*E0x + y*E0y) * 1/_r_S**2
        self._tEz = _tEz
        
        _tH_1 = 1/(_eta*_r_S**2) #SI units!
        _tHx_E0x = -x*y/(2*f)
        _tHx_E0y = (s*f-f-y**2/(2*f))
        _tHx = _tH_1*(E0x*_tHx_E0x + E0y*_tHx_E0y)
        self._tHx = _tHx
        
        _tHy_E0x = (x**2/(2*f)-s*f+f)
        _tHy_E0y = -_tHx_E0x #x*y/(2*f)
        _tHy = _tH_1*(E0x*_tHy_E0x + E0y*_tHy_E0y)
        self._tHy = _tHy
        
        _tHz = _tH_1*(y*E0x + x*E0y)
        self._tHz = _tHz

    def _field_at_point_unprimed(self, xpf, ypf, zpf, lam):
        #private methof! input x', y', z' but output Ex Ey Ez
        # converted in public methods below.
        Ex, Ey, Ez, Hx, Hy, Hz = _numba_field_at_point_unprimed(xpf, ypf, zpf,
                                                                 lam, self.dx,
                                                                 self.p, self.q, self.m,
                                                                 self._tEx, self._tEy, self._tEz,
                                                                 self._tHx, self._tHy, self._tHz)
        return (Ex, Ey, Ez, Hx, Hy, Hz)

    def convert_global_to_prime(self, Ax, Ay, Az):
        # convert any vectorial quantity (which transforms like a normal
        # vector), i.e. coordinates or field strengths
        # from the global coordinate system to the primed coord sys.
        # inputs all must have same shape
        # returns tuple (Apx, Apy, Apz) in K'
        
        Apx = Ax*np.cos(self.phi) + Az*np.sin(self.phi)
        Apy = Ay
        Apz = -Ax*np.sin(self.phi) + Az*np.cos(self.phi)
        
        return Apx, Apy, Apz

    def convert_prime_to_global(self, Apx, Apy, Apz):
        # inverse to `convert_global_to_prime`
        
        Ax = Apx*np.cos(self.phi) - Apz*np.sin(self.phi)
        Ay = Apy
        Az = Apx*np.sin(self.phi) + Apz*np.cos(self.phi)
        
        return Ax, Ay, Az

    def field_at_point(self, xpf, ypf, zpf, lam):
        #in K' coords! both input x', y', z' as well as output Ex' Ey' Ez'
        Ex, Ey, Ez, Hx, Hy, Hz = self._field_at_point_unprimed(xpf, ypf, zpf, lam)

        #E'_foc(x',y') along new optical axis of mid-ray/center-ray
        # (depending on coice above)
        Epx, Epy, Epz = self.convert_global_to_prime(Ex, Ey, Ez)
        Hpx, Hpy, Hpz = self.convert_global_to_prime(Hx, Hy, Hz)
        
        return Epx, Epy, Epz, Hpx, Hpy, Hpz #rotated in K'!

    def field_on_xy_grid(self, xpv, ypv, zp0, lam):
        # Specify input vector x' and y', at distance z'_0 from focus
        # so len(xpv)=M, len(ypv)=N, zp0=scalar
        # returns tuple (E'x, E'y, E'z, H'x, H'y, H'z) each with shape NxM (y first!)
        #E'_foc(x',y') along new optical axis of mid-ray/center-ray
        # (depending on coice above)

        Ex = np.zeros((len(ypv), len(xpv)), dtype=complex)
        Ey = np.zeros_like(Ex)
        Ez = np.zeros_like(Ex)

        Hx = np.zeros_like(Ex)
        Hy = np.zeros_like(Ex)
        Hz = np.zeros_like(Ex)

        # TODO this progress bar does not work in Spyder (at least on Windows)
        # I am not the only one with this problem, fix not known:
        # https://github.com/mortacious/numba-progress/issues/6
        if ProgressBar is not None:
            with ProgressBar(total=len(ypv)) as pbar:
                _numba_unprimed_field_on_xy_grid(xpv, ypv, zp0,
                                                lam, self.dx,
                                                self.p, self.q, self.m,
                                                self._tEx, self._tEy, self._tEz,
                                                self._tHx, self._tHy, self._tHz,
                                                Ex, Ey, Ez, Hx, Hy, Hz,
                                                pbar)
        else:
            # package not present, do not print progress
            _numba_unprimed_field_on_xy_grid(xpv, ypv, zp0,
                                                lam, self.dx,
                                                self.p, self.q, self.m,
                                                self._tEx, self._tEy, self._tEz,
                                                self._tHx, self._tHy, self._tHz,
                                                Ex, Ey, Ez, Hx, Hy, Hz,
                                                None)

        Epx, Epy, Epz = self.convert_global_to_prime(Ex, Ey, Ez)
        Hpx, Hpy, Hpz = self.convert_global_to_prime(Hx, Hy, Hz)
        return (Epx, Epy, Epz, Hpx, Hpy, Hpz)

