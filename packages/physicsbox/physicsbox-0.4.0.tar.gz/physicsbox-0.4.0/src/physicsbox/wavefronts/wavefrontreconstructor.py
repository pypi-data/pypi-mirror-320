# -*- coding: utf-8 -*-
"""
Core wavefront reconstruction class.

The class `ZonalWavefrontReconstructor` implements a zonal wavefront reconstruction
with arbitrary mask (circular pupil by parameter or arbitrary by dotmask).

The word wavefront and phasemap are used interchangeably here.

@author: Leonard.Doyle

History
* 2018-05-25 ~LD created file during Master's thesis
* 2023-09-13 ~LD patched in modal (Zernike) reconstrcution code by
  jannik.esslinger@physik.uni-muenchen.de
* 2024-02-23 ~LD removed modal reconstruction for now,
  completely reworked (simplified) matrix building. Based on Janniks
  comment, masking certain lenslets no longer removes affected rows
  and columns from matrix, but simply sets them to 0. The reconstruction
  still seems to work, but code is far simpler.


## Theory

On the camera, a displacement $dx$/$dy$ of the spot centroid is measured
for each lenslet. The distance between the camera should be the focal
length of the lenslets $f$. (NB: If this is not exact, it goes into the
reconstruction as a linear factor, i.e. the phasemap is simply rescaled).
We can call this the slope $s$:

$$s = tan(\alpha) = dx/f$$



## Details on least-squares algorithm:

### scipy vs numpy

According to SO, since some versions the behaviour is identical:
https://stackoverflow.com/questions/29372559/what-is-the-difference-between-numpy-linalg-lstsq-and-scipy-linalg-lstsq

According to docs, numpy should only be preferred if Fortran dependency is
not desired:https://www.scipy.org/scipylib/faq.html#why-both-numpy-linalg-and-scipy-linalg-what-s-the-difference
-> should not really be relevant in modern distributions, but
since we have scipy dependency anyway, use this as might be faster
 on some systems where numpy is compiled without Fortran libs

### optimizing/ choosing engine
 
Finally, according to scipy docs, the Lapack routine can be tuned:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.lstsq.html#scipy.linalg.lstsq
lapack_driver=None: str, optional
Which LAPACK driver is used to solve the least-squares problem.
Options are 'gelsd', 'gelsy', 'gelss'. Default ('gelsd') is a good choice.
However, 'gelsy' can be slightly faster on many problems. 'gelss' was used
historically. It is generally slow but uses less memory.
 (New in version 0.17.0.)

scipy.linalg.lstsq with lapack_driver = None / gelsd (default)
_buildRedAtAinvAt6.59s (NB: function changed and renamed)

scipy.linalg.lstsq with lapack_driver = gelss (historic, should not use)
_buildRedAtAinvAt1.68s

scipy.linalg.lstsq with lapack_driver = gelsy
_buildRedAtAinvAt0.45s

-> major improvement using gelsy driver!
difference in resulting test phase map on the 1e-16 (1e-10um) level, negligible

"""

import numpy as np
import scipy.linalg
SCIPY_LAPACK_DRV = 'gelsy' # 'gelsy', 'gelsd'(default), 'gelss', see top

from ..tictoc import timeit
from .imageevaluation import generate_reference_spots
from .interpnan import blank_outside_mask


class ZonalWavefrontResult:
    #********** Class methods - Class factory ***********************
    
    @classmethod
    def from_config(cls, cfg):
        """Create fresh instance and fill all relevant values from config."""
        res = cls()
        res.M, res.N = cfg.M, cfg.N
        res.lens_f, res.lenspitch = cfg.lens_f, cfg.lenspitch
        res.pupil_diameter = cfg.pupil_diameter
        res.pupil_center = cfg.pupil_center
        # in Result, we don't need direct access to dotmask anymore, but
        # still want to keep two distinct masks:
        # 1. combined mask array, to allow filtering and plotting etc
        # 2. pupil mask array, since we need to treat masked inside and outside
        #    differently (notably when sending data to Deformable Mirr software)
        res.mask = cfg.combined_mask_array
        res.pupil_mask = cfg.pupil_mask_array
        return res

    #********** Instance methods ***********************
    
    def __init__(self):
        self.M, self.N = 0, 0
        self.lens_f, self.lenspitch = 0.0, 0.0
        self.pupil_diameter = 0
        self.pupil_center = (0, 0)
        self.mask = None
        self.pupil_mask = None

        #PhaseEval
        self.slopes = None
        self.invalids = None
        self.phasemap = None

def _slope_array_to_vector(slopes, addpiston= True, piston = 0.0):
    """Image results is [y, x, 0:1](slopex, slopey). Return a vector of all
    slopes, x slopes first, column major linearized, including piston if
    addpiston = true."""
    if type(slopes) is tuple:
        slopesx = slopes[0].flatten()
        slopesy = slopes[1].flatten()
    else:
        #probably given as MxNx2 grid, third dimension being (x, then y)
        slopesx = slopes[:,:,0].flatten()
        slopesy = slopes[:,:,1].flatten()
    if addpiston:
        slopes_vec = np.concatenate((slopesx, slopesy, [piston]))
    else:
        slopes_vec = np.concatenate((slopesx, slopesy))
    return slopes_vec

@timeit
def _reduceAByMask(A, mask):
    """Reduce matrix A by mask.
    Steps:
    * determine invalid phase points
    * determine any slopes associated with those invalid points
    * build a mask of same shape as `A` based on the outer product of the
        above vectors.
    * use `numpy.ma` masked array to create a smaller matrix A where all
        rows and columns associated with invalid values are removed.

    Parameters
    ----------
    A : ndarray
        matrix A, shape (2*M*N+1)x(M*N)
    mask : ndarray, bool
        mask array, shape MxN

    Returns
    -------
    ndarray
        reduced matrix A
    """
    maskvec = mask.flatten() #implicit copy
    invalidpoints = ~maskvec #invert, True=1 means invalid
    
    testA = np.zeros_like(A, dtype=bool)
    testA[A!=0]=True
    # determine which slopes are in some connection to invalid points
    invalidslopes_hud = testA @ invalidpoints 
    # reset piston term, always "valid"
    invalidslopes_hud[-1] = False
    
    invalid_in_A = np.outer(invalidslopes_hud, invalidpoints)
    maskedA = np.ma.array(A, mask=invalid_in_A)
    reducedA = np.ma.compress_rowcols(maskedA)
    return reducedA

@timeit
def _reduceDByMask(D, mask):
    """Reduce matrix D by mask.
    Option one: reduce D in input and output dimension. Then we need
        another matrix to convert from "full" southwell to reduced
        southwell vector before feeding in.
    Option two: it is much easier if we also use this matrix as the
        reduction matrix for the input vector: the input dimension
        matches M*N*2, but the output dimensions match the reduced
        system matrix.
    """
    maskvec = mask.flatten() #implicit copy
    invalidpoints = ~maskvec #invert, True=1 means invalid
    
    #for southwell slopes, just double mask since it seems unlogical that
    #slopes in x exist but not in y and vice versa
    invalidslopes_south = np.concatenate((invalidpoints, invalidpoints,
                                          [False])) # + piston

    testD = np.zeros_like(D, dtype=bool)
    testD[D!=0] = True
    invalidslopes_hud = testD @ invalidslopes_south

    invalid_in_D = np.outer(invalidslopes_hud, np.ones_like(invalidslopes_south))
    maskedD = np.ma.array(D, mask=invalid_in_D)
    reducedD = np.ma.compress_rows(maskedD)
    return reducedD

@timeit
def _buildBinv(mask):
    # matrix B from long to short list of points phi
    # matrix Binv from short to long list of points phi
    B = np.eye(mask.size)
    maskvec = mask.flatten() #implicit copy
    invalidpoints = ~maskvec #invert, True=1 means invalid
    
    invalid_in_B = np.zeros_like(B, dtype=bool)
    invalid_in_B[:,0] = invalidpoints # just mark 1 column, others follow
    maskedB = np.ma.array(B, mask=invalid_in_B)
    rB = np.ma.compress_rows(maskedB)
    
    Binv = rB.T # since originally a diagonal matrix, .T is inverse
    return Binv

@timeit
def _buildAtAinvAt(A):
    AtA = A.T @ A #matmul
    sol, resid, rank, sing = scipy.linalg.lstsq(
            AtA, A.T, lapack_driver=SCIPY_LAPACK_DRV)
    AtAinvAt = sol
    return AtAinvAt

@timeit
def _buildA(M, N):
    #Update 2024-02-23: does not contain lenspitch,
    # instead, this scalar factor is applied during
    # evaluation. Therefore, matrix only has to be
    # recalculated if M,N or combinedmask changed.
    
    # updated version, loop only over non-zero entries -> massive speed-up
    sizPhi = M * N
    sizSlopeX = M * (N-1)
    sizSlopeY = (M-1) * N
    A = np.zeros((sizSlopeX + sizSlopeY + 1, sizPhi))

    # components of matrix are related to phi and slopes
    # via linear indexing, but with different grid shapes
    # for slopes (MxN-1 for X, M-1xN for Y). Need this below:
    indices_phi = np.arange(sizPhi).reshape((M,N))
    indices_hx = np.arange(sizSlopeX).reshape((M,N-1))
    indices_hy = np.arange(sizSlopeY).reshape((M-1,N))

    # for Ax
    for ii in range(M):
        for jj in range(N-1):
            # for slope h_i,j, we have contributions:
            # -1 for phi_i,j (except for last j, which
            #   does not exist in slopes, so skipped in
            #   loop bounds)
            # +1 for phi_i,j+1 (except for phi_i,0, also
            #   skipped due to loop range)
            pp = indices_hx[ii, jj]
            qq_minus = indices_phi[ii, jj]
            A[pp, qq_minus] = -1
            qq_plus = indices_phi[ii, jj+1]
            A[pp, qq_plus] = +1
            
    # for Ay
    idx_offset = sizSlopeX # since stacked below each other
    for ii in range(M-1):
        for jj in range(N):
            # for slope h_i,j, we have contributions:
            # -1 for phi_i,j (except for last i, which
            #   does not exist in slopes, so skipped in
            #   loop bounds)
            # +1 for phi_i+1,j (except for phi_0,j, also
            #   skipped due to loop range)
            pp = indices_hy[ii, jj]
            qq_minus = indices_phi[ii, jj]
            A[pp+idx_offset, qq_minus] = -1
            qq_plus = indices_phi[ii+1, jj]
            A[pp+idx_offset, qq_plus] = +1
    
    # NB: piston does not add up to 1, since will be multiplied
    # by 1/lenspitch later, but since we are forcing it 0 don't care.
    A[-1,:] = 1 # piston term
    return A

@timeit
def _buildD(M, N):
    """From southwell to hudgin via s_hud = D*s_south."""
    sizSouthX = M * N
    sizSouthY = M * N
    sizHudX = M * (N-1)
    sizHudY = (M-1) * N
    D = np.zeros((sizHudX + sizHudY + 1, sizSouthX + sizSouthY + 1))

    # map linear/flat indexing for different slopes shape:
    indices_southX = np.arange(sizSouthX).reshape((M,N))
    indices_southY = indices_southX # same shape and content
    indices_hx = np.arange(sizHudX).reshape((M,N-1))
    indices_hy = np.arange(sizHudY).reshape((M-1,N))
    
    # for Dx
    for ii in range(M):
        for jj in range(N-1):
            # for slope h_i,j, we have contributions:
            # +1/2 for phi_i,j (except for last j, which
            #   does not exist in slopes, so skipped in
            #   loop bounds)
            # +1/2 for phi_i,j+1 (except for phi_i,0, also
            #   skipped due to loop range)
            pp = indices_hx[ii, jj]
            qq_minus = indices_southX[ii, jj]
            D[pp, qq_minus] = 0.5
            qq_plus = indices_southX[ii, jj+1]
            D[pp, qq_plus] = 0.5

    # for Dy
    # since Dx+Dy(+piston) are on a block-diagonal matrix
    # need offsets in pp and qq for this block
    idx_offset_Hud = sizHudX # since stacked below each other
    idx_offset_south = sizSouthX # since slopes south_Y come after south_X
    for ii in range(M-1):
        for jj in range(N):
            # for slope h_i,j, we have contributions:
            # +1/2 for phi_i,j (except for last i, which
            #   does not exist in slopes, so skipped in
            #   loop bounds)
            # +1/2 for phi_i+1,j (except for phi_0,j, also
            #   skipped due to loop range)
            pp = indices_hy[ii, jj]
            qq_minus = indices_southY[ii, jj]
            D[pp+idx_offset_Hud, qq_minus+idx_offset_south] = 0.5
            qq_plus = indices_southY[ii+1, jj]
            D[pp+idx_offset_Hud, qq_plus+idx_offset_south] = 0.5
    
    D[-1,-1] = 1 # piston term
    return D

@timeit
def _build_system_matrix(mask):
    """Calculate the matrix S which directly converts
    slope measurements to a zonal wavefront/phase map.

    Returns
    -------
    ndarray
        matrix S
    """
    """
    Execution speed:
    for 40x40 lenslet grid, no mask, average workstation
    Time for _buildA:               0.006-0.006s
    Time for _reduceAByMask:        0.012-0.018s
    Time for _buildAtAinvAt:        0.773-1.034s
    Time for _buildD:               0.007-0.011s
    Time for _reduceDByMask:        0.029-0.031s
    Time for _buildBinv:            0.002-0.004s
    Time for _build_system_matrix:  1.235-1.406s

    for 40x40 grid, 30 diam pupil, same PC
    Time for _buildA:               same
    Time for _reduceAByMask:        0.023-0.033s
    Time for _buildAtAinvAt:        0.060-0.070s
    Time for _buildD:               same
    Time for _reduceDByMask:        0.037-0.060s
    Time for _buildBinv:            0.008-0.013s
    Time for _build_system_matrix:  0.317-0.377s
    
    -> re-introducing the row-deletion to reduce matrix
        was a very valuable improvement.
    """

    M, N = mask.shape # shape also caches M,N
    A = _buildA(M, N)
    rA = _reduceAByMask(A, mask)
    rAtAinvAt = _buildAtAinvAt(rA)
    D = _buildD(M, N)
    rD = _reduceDByMask(D, mask)
    rS = rAtAinvAt @ rD # combined system matrix S
    Binv = _buildBinv(mask)
    S = Binv @ rS # expansion to non-reduced S
    return S

class ZonalWavefrontReconstructor:
    """Take slope data and make a phase map from it. Some auxiliary functions
    to create the used matrices etc.
    Rule: Slope vectors are x-values first, y-values next, total piston (can be 0) last
    """
    def __init__(self, cfg, buildmatrix = True):
        """
        Initialize a new PhaseEvaluator object.
        Nowadays, the matrix building was optimized to only contain parameters
        which are absolutely necessary. These are M,N and the mask pattern.
        If these change, matrix must be rebuilt to be useful again.
        If any other changes (lenspitch) etc these can be applied on the fly.
        Therefore the matrix does not store its own copy of the config anymore,
        but only the 3 values necessary.

        If `buildmatrix=True`, matrix is built immediately based on the given
        `cfg` object. If `buildmatrix=False`, config is nowadays ignored.
        """
        
        # in order to check if matrix is valid, we need to cache
        # the key parameters to compare them
        self._current_mask = None
        self.S = None
        if buildmatrix:
            self.S = _build_system_matrix(cfg.combined_mask_array) # shape also caches M,N

    def to_dict(self):
        """Build a dictionary containing all parameters
        fully describing this object. Restricted to basic Python and numpy
        types to be easy to `pickle`.

        Returns
        -------
        dict
            dictionary of all relevant parameters in simplistic format
        """
        out = {
            'S': self.S, # may be None
            'mask': self._current_mask, # may be None
        }
        return out

    def apply_dict(self, values):
        """Reapply the given settings to this reconstructor.
        In the future, this might become more generic, when more things
        are added. For now, it simply applies the matrix `S` and the
        matching `mask`. If something seems off, the function will raise
        an error.
        """
        if not 'S' in values or not 'mask' in values:
            raise KeyError('Must supply at least `S` and `mask`.')
        S = values['S']
        mask = values['mask']
        if S is not None and mask is None:
            raise ValueError('Invalid settings given, if `S` is not None,'
                             ' `mask` must be an `ndarray`.')
        # however if S is None, this means matrix is not built, so don't
        # care about mask
        self.S = S
        self._current_mask = mask

    @property
    def is_matrix_built(self):
        # use self.S as proxy check to indicate others None, too
        return (self.S is not None)

    def check_matrix_valid(self, cfg):
        """Return True if matrix is built and matches configured
        M, N, pupil and dotmask. False otherwise."""
        if not self.is_matrix_built:
            return False
        
        current_M, current_N = self._current_mask.shape

        if (cfg.M != current_M or
            cfg.N != current_N):
            return False
        
        current_mask = self._current_mask
        if np.array_equiv(current_mask,True):
            # a mask of all 1s is no mask
            current_mask = None
        
        new_mask = cfg.combined_mask_array #will never be None
        if np.array_equiv(new_mask, True):
            # a mask of all 1s is no mask
            new_mask = None
        changed_mask = not np.array_equal(current_mask, new_mask)
        # none and none is OK, or same mask, all others fail
        
        return not changed_mask

    def update_matrix(self, cfg):
        """If matrix is not built or not up to date with global settings,
        needs a re-build. Since this can take several seconds, let user decide
        when to trigger it."""
        if not self.check_matrix_valid(cfg):
            self.reset_matrix()
            mask = cfg.combined_mask_array
            self.S = _build_system_matrix(mask)
            self._current_mask = mask
    
    def reset_matrix(self):
        """Delete matrix, e.g. if out of sync with global parameters.
        Centroids and slopes can still be calculated, but evaluation results
        will not contain a reconstructed wavefront."""
        self.S = None
        self._current_mask = None

    def evaluate_spots(self,
                       cfg,
                       centroids,
                       strict=True):
        """
        Evaluate spot pattern. Spot pattern is input as
        MxNx2 array with [y_pos, x_pos, 0:1] (x_spot, y_spot)
        and x_spot/y_spot being in global coordinates,
        i.e. not relative to each lenslet
        """
        reference_spots = generate_reference_spots(cfg)
        deltas = centroids - reference_spots
        return self.evaluate_spot_deltas(cfg, deltas, strict=strict)

    def evaluate_spot_deltas(self,
                             cfg,
                             centroid_deltas,
                             strict=True):
        """Evaluate spot pattern where spot coordinates
        are relative to each lenslet center.

        Parameters
        ----------
        centroid_deltas : ndarray
            MxNx2 ndarray with [y_pos, x_pos, 0:1] (x_spot, y_spot)

        Returns
        -------
        WavefrontResult
            The reconstructed wavefront along with configured mask etc.
        """
        slopes = centroid_deltas/cfg.lens_f
        return self.evaluate_slopes(cfg, slopes, strict=strict)

    def evaluate_slopes(self,
                        cfg,
                        slopes,
                        strict=True):
        #slopes is [y_pos, x_pos, 0:1] (x_slope, y_slope)
        assert slopes.ndim == 3
        #full res: 0.5ms

        # Slopes are NOT angles. They are geometric
        # Dx/f = s = dz/lenspitch
        # if you want a slope in angles, use
        # tan(alpha) = s -> alpha = arctan(s)
        
        res = ZonalWavefrontResult.from_config(cfg)
        res.slopes = slopes

        #NB: old behaviour: if matrix was reset/None, was seen
        # as an indication that user did not want to have a matrix
        # reconstruction, so simply pass on a result without phase.
        # New behaviour: the notion of resetting the matrix
        # seems not practical in the real world. Also, calculation
        # times have been improved over time. Instead, the `strict`
        # parameter controls the behaviour:
        # if strict=True, raise an error on any problem encountered
        # if strict=False, return a NaN-wavefront instead.
        #   This allows analysis of the other aspects of the result
        #   object to figure out what is going wrong.
        if strict:
            if not self.is_matrix_built:
                raise RuntimeError('Matrix not built, reconstruction not possible')
            if not self.check_matrix_valid(cfg):
                raise RuntimeError('Matrix built, but invalid. Reset or update')
        
        if self.is_matrix_built and self.check_matrix_valid(cfg):
            res.phasemap = self._evaluate(cfg.lenspitch, slopes, strict=strict)
        else:
            # only reached in non-strict mode
            res.phasemap = np.nan * np.zeros_like(slopes[:,:,0])
        return res
    
    def _evaluate(self, lenspitch, slopes, strict):
        """Evaluate a given slope data to phase map. Dimensions etc have to match current 
        config.
        Matrix must be built and valid, needs to be checked before calling this function
        even in strict mode.
        If strict=True, an error will be raised if the data contains NaNs.
        If strict=False, simply return an all-NaN wavefront to indicate the problem
            (even if only 1 number is NaN, the matrix multiplication would lead to
            all-NaN anyway.)
        """
        assert self.is_matrix_built
        _mask = self._current_mask
        assert slopes.shape[0:2] == _mask.shape
        
        ssouth_x2d = blank_outside_mask(slopes[:,:,0], _mask, 0.0)
        ssouth_y2d = blank_outside_mask(slopes[:,:,1], _mask, 0.0)
        if (np.isnan(ssouth_x2d).any() or np.isnan(ssouth_y2d).any()):
            if strict:
                raise ValueError('Slope data must not contain NaN inside mask.')
            else:
                # in non-strict mode, indicate error by all-NaN
                return np.nan * np.zeros_like(self._current_mask)
        
        slopes_southwell = _slope_array_to_vector((ssouth_x2d, ssouth_y2d)) #southwell geometry
        
        phasemap_flat = self.S @ slopes_southwell # this is where the magic happens!
        phasemap_flat *= lenspitch # not part of matrix A anymore, applied on the fly
        putNaNs_outside_mask = True
        if putNaNs_outside_mask:
            phasemap_flat[~self._current_mask.flatten()] = np.nan
        M, N = self._current_mask.shape
        phasemap = phasemap_flat.reshape((M, N))
        phasemap *= -1 #invert sign to match Phasics SID4!
        
        return phasemap
