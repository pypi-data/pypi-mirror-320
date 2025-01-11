# -*- coding: utf-8 -*-
"""

Routines to fit a list of Zernike polynomials onto given wavefront.

Adapted from the LightPipes package.

"""
import numpy as np

from ..utils import ImageCoordSys

def noll_to_zern(j):
    """
    *Convert linear Noll index to tuple of Zernike indices.*
    
    :param j: the linear Noll coordinate, n is the radial Zernike index and m is the azimuthal Zernike index.
    :type j: int, float
    :return: name of Noll Zernike term
    :rtype: string (n, m) tuple of Zernike indices
    
    .. seealso::
    
        * :ref:`LightPipes Manual: Zernike polynomials.<Zernike polynomials.>`
        * `https://oeis.org <https://oeis.org/A176988>`_
        * `Tim van Werkhoven, https://github.com/tvwerkhoven <https://github.com/tvwerkhoven>`_
    """

    if (j == 0):
        raise ValueError("Noll indices start at 1, 0 is invalid.")

    n = 0
    j1 = j-1
    while (j1 > n):
        n += 1
        j1 -= n

    m = (-1)**j * ((n % 2) + 2 * int((j1+((n+1)%2)) / 2.0 ))
    return (n, m)

def zernike(n,m,rho,phi):
    """
    Zernike polynomial 

       +-m
      R    as in Born and Wolf, p. 465, sixth edition, Pergamon
         n
    
    The implementation have not been optimized for speed.

    Parameters
    ----------
    n : int
        DESCRIPTION.
    m : int
        DESCRIPTION.
    rho : rho
        DESCRIPTION.
    phi : phi
        DESCRIPTION.

    Returns
    -------
    double.

    """
    mabs = np.abs(m)
    prod = 1.0
    sign = 1
    summ = 0.0
    for s in range(int((n-mabs)/2) + 1):
        if n-2*s != 0:
            prod = np.power(rho, n-2*s)
        else:
            prod = 1.0
        prod *= np.math.factorial(n-s)*sign
        prod /= (np.math.factorial(s)
                * np.math.factorial(int(((n+mabs)/2))-s)
                * np.math.factorial(int(((n-mabs)/2))-s))
        summ += prod
        sign = -sign
    if m>=0:
        return summ*np.cos(m*phi)
    else:
        return (-1)*summ*np.sin(m*phi)

def ZernikeFit(wavefront, j_terms, pupil_center, pupil_diameter,  norm=True):
    """
    *Fit the first N terms (Noll indexing) to the given Field.*
    
    :param wavefront: input field, should be NaN outside pupil, can be NaN inside in places
    :param j_terms: if j_terms is a number, first j_terms terms will be fitted if j_terms is a collection (list, array), each number should represent one noll index to fit.
    :type j_terms: int, float, list array
    :param pupil_center: tuple (cx, cy) of pupil center
    :param pupil_diameter: beam diameter on which the Zernike coefficients should be defined.
    :param norm: if True normalization (default = True)
    
    :return: (j_terms, A_fits) 
    :rtype: tuple of int, float
    
    Piston term (j=1 / n,m=0) is always necessary for fitting but generally
    meaningless in the result.
    """
    if not pupil_diameter > 0.0:
        raise ValueError('Pupil diameter must not be 0.0')
    Ph = wavefront
    R = pupil_diameter/2
    cc = ImageCoordSys(wavefront, dx=1, cx=pupil_center[0], cy=pupil_center[1])
    r, phi = cc.mgrid_polar

    A = 1 #[a.u.] since reference amplitude is 1, coeffs from leastsq will
        # automatically have the correct units
    
    j_terms = np.asarray(j_terms)
    if j_terms.ndim == 0:
        j_terms = np.arange(1,j_terms+1)
    else:
        if not 1 in j_terms:
            j_terms = np.array([1, *j_terms]) #always need the piston
    
    zerns_to_fit = []
    for j_noll in j_terms:
        n, m = noll_to_zern(j_noll)
        if norm:
            if m==0:
                # wikipedia has modulo Pi? -> ignore for now
                # keep backward compatible and since not dep. on n/m irrelevant
                Nnm = np.sqrt(n+1)
            else:
                Nnm = np.sqrt(2*(n+1))
        else:
            Nnm = 1
        
        rho = r/R
        #Update 2024-05-31: compared to LightPipes, the sign was flipped here:
        PhZ = A*Nnm*zernike(n,m, rho, phi)
        zerns_to_fit.append(PhZ)
    b = Ph[~np.isnan(Ph)] #select only non-NaN
    AA = np.column_stack([PhZ[~np.isnan(Ph)] for PhZ in zerns_to_fit])
    A_fits, res, rank, s = np.linalg.lstsq(AA, b, rcond=None)
    # assert rank==j_terms.size #since Zernikes orthogonal by definition
    # assert np.alltrue(s>1) #again, since always orthogonal
    # return (j_terms, A_fits, res, rank, s)
    return (j_terms, A_fits)
