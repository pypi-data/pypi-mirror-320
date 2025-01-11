# -*- coding: utf-8 -*-
"""
from:
    https://stackoverflow.com/questions/21690608/numpy-inpaint-nans-interpolate-and-extrapolate

only works under the assumption of reasonably contiguous data
UPDATE 2024-03-01: Improved NaN-inpainting at mask edges significantly.

Created on Sun May 27 12:14:57 2018

@author: Leonard.Doyle
"""
import warnings

import numpy as np
import scipy.spatial
from scipy import interpolate

def inpaint_nan_inside_mask(values, mask=None, clip_min=None, clip_max=None,
                            strict=True):
    """Fill in blanks (marked with NaN) in the input array by interpolation
    / extrapolation. Where possible, i.e. for points lying in between valid
    source points ("inside the convex hull" in scipy speak), a scipy linear
    interpolator will be used. For the rest, the value will be extrapolated
    based on the method detailed below.
    If `mask` is supplied, only fill values inside mask, but keep NaNs outside
    the mask. Masked source points are also not used for the interpolation
    / extrapolation.
    To clarify:
    Inside mask (where mask is True), keep the original value
        or fill in with interpolated value where NaN.
    outside mask (where mask is False), keep the original value
        even if it is NaN.
    For the application in Shack-Hartmann images, we exclude the
    possibility that an extrapolated point lies outside of its grid
    region, since that would mean it overlaps with the next neighbour.
    To enforce this safeguard, clipping limits can be supplied and any
    extrapolated value will be clipped to the given interval.
    
    Limits:
    * If all points are NaN, there is nothing to fill, raising an error
    * If many extrapolation steps have to be taken, the method used
      produces unstable/weird results. By design we do not throw an error,
      but there is a warning when a point more than 5 points away from
      a source point is extrapolated.
    
    Returns an array where all NaN-values (inside mask if given) are
    replaced. Design decision: this function will not return an array
    with potentially NaNs still present (inside the mask region).

    Parameters
    ----------
    values : ndarray
        input data
    mask : ndarray, optional
        mask of True (valid) or False (ignore) or None to skip, default is None
    clip_min: float, optional
        if supplied, any interpolated value
        lower than this value will be clipped to this value.
    clip_max: float, optional
        like clip_min, but upper limit.
    strict: bool, option
        if True, raise error if interpolation/extrapolation fails, else
        instead return partially filled array (default True).
    """

    """
    IMPLEMENTATION DETAILS

    It seems there are no good options available online (in scipy or stackoverflow)
    for 2D extrapolation of data. Our problem should be simple because
    we have a regular, equidistant grid of X,Y coordinates, but is hard because
    there are NaNs in between so it is not really equidistant.
    The following is my own idea of how to approach the problem, with no claim
    of efficiency/ cleverness.

    Strategy:
    * if point is outside of mask, do not use it for interpolation
      since user determined it is not trustworthy
      -> for interpolation source points, set all outside mask to NaN
    * if point inside mask is inside Qhull of remaining points, can use
      scipy to do a linear interpolation between neighbours (even if distant).
    * if point inside mask is not inside Qhull, scipy will fill it with NaN
      (i.e. remain NaN). In this case, we must use a custom strategy to find
      a suitable value:
      * fill with 0.0 -> bad idea, not really useful
      * fill with average of non-nan direct neigbours -> should yield
        good results for 0-mean data like slopes and deltas, but break down
        for e.g. spot coordinates which follow a linear trend
      * extrapolate from direct and next-to-next neighbours
        in a 5x5 grid with NaN point in center, there are 1-4 slopes determined
        by neighbours and next neighbours in up, down, left, right direction.
        In theory, we can also use diagonals for extra measurements.
        The average of 1-4 values extrapolated by this method should
        be a good approximation for the filled value.
        Since spot displacements measure the derivative of the wavefront,
        this should even be accurate to second derivate in wavefront.
    * the last step must then be repeated iteratively until all values are
        extrapolated.
    There may still be pathological examples like only 2 non-Nan values
    not spanning a convex hull, but also more than 2 neighbours apart.
    While this should raise an error in scipy (which is converted to
    ValueError here), we still limit the iteration as a safeguard.
    """
    if mask is None:
        mask = np.ones_like(values, dtype=bool)
    
    invalid_mask = np.isnan(values)
    # if outside of mask, don't count as invalid since will not interpolate/extrapolate
    invalid_mask = invalid_mask & mask
    invalid_coords = np.array(np.nonzero(invalid_mask)).T

    # for first step of interpolation, use only valid AND inside mask
    valid_mask = ~np.isnan(values)
    valid_mask = valid_mask & mask
    valid_coords = np.array(np.nonzero(valid_mask)).T
    valid_value_list = values[valid_mask]
    
    if valid_value_list.size == 0:
        raise ValueError('Interpolation impossible: all points NaN')

    values_filled = values.copy()
    try:
        interp = interpolate.LinearNDInterpolator(valid_coords, valid_value_list, fill_value=np.nan)
        # fill_value=NaN is default, but we want to guarantee that explicitly here
        
        interp_list = interp(invalid_coords)
        values_filled[invalid_mask] = interp_list
    except scipy.spatial._qhull.QhullError as ex:
        if strict:
            # at least one occasion for this error observed:
            # * on beam edge, several consecutive pixels in a (diagonal) line
            #  -> all linearly dependent, do not span a surface
            #  cannot determine by e.g. number of points alone, simply try and except here
            msg = f'{ex}'.split('\n')[0] #slightly ugly, but outout for QH6154="simplex" far too long otherwise
            raise ValueError('Qhull error during interpolation'
                            f' (check mask regions are contiguous): {msg}') from None
        else:
            # in non-strict mode, simply continue and try to fill by alternative method
            pass

    # values_filled may still
    # * contain valid points inside and outside of mask
    # * contain invalid points inside and outside of mask
    # next, use neighbour-based extrapolation (but only using values inside mask!)
    # to make all points inside the mask valid. Apply recursively, if necessary.

    # as before, determine invalids (inside mask) for now filled array
    invalid_mask = np.isnan(values_filled) & mask
    invalid_coords = np.array(np.nonzero(invalid_mask)).T

    iteration_counter = 0
    WARN_iteration_counter = 5
    MAX_iteration_counter = np.ceil(np.sqrt(
        values.shape[0]**2 + values.shape[1]**2)) # worst case is diagonal
    """
    NB: With each iteration, we can fill more and more neighbours, eventually
    filling the entire grid.
    The first implementation had an `iteration_counter` and limited
    the number of iterations to an arbitrary value (=5). The rationale was
    that probably something is really badly wrong if we need to extrapolate
    so many neighbours and user should be informed of this.
    On second thought however, it seems more robust that this function simply
    continues and the caller has to figure out if something is unusual.
    The MAX_iteration_counter simply prevents an endless loop now.
    One can always make the MAX_iteration_counter a kwarg of this function to
    bring back the explained behaviour.
    
    Performance consideration: on a decent workstation, extrapolating
    a circlular pupil all the way to the edges took ~0.2s on a 40x50 grid
    with more than 60% points to fill (>1200 points).
    `iteration_counter` was 24 then.
    This seems still acceptable in delay, so no action necessary for now.
    
    Stability consideration: extrapolating so far does however yield very
    strange reults. When extrapolating the circular mask to the entire grid,
    (with no clipping) after ~10 neighbours, suddenly negative values appear
    in an all-positive source image. Therefore the arbitrary cutoff of e.g.
    5 points does not seem too bad after all. Maybe a warning is a good
    compromise.
    """
    while len(invalid_coords) > 0:
        if iteration_counter == WARN_iteration_counter:
            warnings.warn(f'Extrapolating more than {WARN_iteration_counter}'
                          ' neighbours, values will not be trustworthy.')
        if iteration_counter >= MAX_iteration_counter:
            if strict:
                raise ValueError(f'Extrapolating data over more than {MAX_iteration_counter}'
                                    ' neighbours, something might be wrong. Check mask'
                                    ' domains are contiguous.')
            else:
                # in non-strict mode, simply return how far we got
                break
        values_filled_masked = blank_outside_mask(values_filled, mask, fill_value=np.nan)
        for _Y, _X in invalid_coords:
            extrapolated1 = _extrapolate_from_array_linear(values_filled_masked, _Y, _X, 'top', clip_min, clip_max)
            extrapolated2 = _extrapolate_from_array_linear(values_filled_masked, _Y, _X, 'bottom', clip_min, clip_max)
            extrapolated3 = _extrapolate_from_array_linear(values_filled_masked, _Y, _X, 'left', clip_min, clip_max)
            extrapolated4 = _extrapolate_from_array_linear(values_filled_masked, _Y, _X, 'right', clip_min, clip_max)
            all_directions = np.array([extrapolated1, extrapolated2, extrapolated3, extrapolated4])
            if np.isnan(all_directions).sum() == 4:
                """
                None of the 4 directions yielded a possible extrapolation
                value (no direction has 2 consecutive neighbours). As a 
                fallback solution, use the average of any direct neighbours.
                While this is even worse than simplistic linear extrapolation,
                it is guaranteed to fill the grid eventually (except for
                all-NaN case already tested above).
                """
                newval = _extrapolate_from_array_const(values_filled_masked, _Y, _X, clip_min, clip_max)
            else:
                newval = np.nanmean(all_directions)
            values_filled[_Y, _X] = newval
        # update list of invalid coords:
        invalid_mask = np.isnan(values_filled) & mask
        invalid_coords = np.array(np.nonzero(invalid_mask)).T
        iteration_counter += 1
    return values_filled

def _extrapolate_from_array_linear(values, Y, X, direction, clip_min, clip_max):
    if direction == 'top':
        if Y-2 < 0:
            return np.nan # at edge, nothing to calculate
        neighbour = values[Y-1, X]
        nneighbour = values[Y-2, X]
        newval = neighbour + (neighbour - nneighbour) # linear slope with delta_X = 1
        return _clip(newval, clip_min, clip_max)
    elif direction == 'bottom':
        if Y+2 >= values.shape[0]:
            return np.nan # at edge, nothing to calculate
        neighbour = values[Y+1, X]
        nneighbour = values[Y+2, X]
        newval = neighbour + (neighbour - nneighbour)
        return _clip(newval, clip_min, clip_max)
    elif direction == 'left':
        if X-2 < 0:
            return np.nan # at edge, nothing to calculate
        neighbour = values[Y, X-1]
        nneighbour = values[Y, X-2]
        newval = neighbour + (neighbour - nneighbour)
        return _clip(newval, clip_min, clip_max)
    elif direction == 'right':
        if X+2 >= values.shape[1]:
            return np.nan # at edge, nothing to calculate
        neighbour = values[Y, X+1]
        nneighbour = values[Y, X+2]
        newval = neighbour + (neighbour - nneighbour)
        return _clip(newval, clip_min, clip_max)
    else:
        raise ValueError(f'Unknown direction value {direction}')

def _extrapolate_from_array_const(values, Y, X, clip_min, clip_max):
    """extrapolate using nearest neighbour averages"""
    neighbours = []
    # top
    if Y-1 >= 0:
        neighbours.append(_clip(values[Y-1, X], clip_min, clip_max))
    else:
        neighbours.append(np.nan)
    # bottom
    if Y+1 < values.shape[0]:
        neighbours.append(_clip(values[Y+1, X], clip_min, clip_max))
    else:
        neighbours.append(np.nan)
    # left
    if X-1 >= 0:
        neighbours.append(_clip(values[Y, X-1], clip_min, clip_max))
    else:
        neighbours.append(np.nan)
    # right
    if X+1 < values.shape[1]:
        neighbours.append(_clip(values[Y, X+1], clip_min, clip_max))
    else:
        neighbours.append(np.nan)
    if np.isnan(neighbours).sum() == 4:
        # prevent all-NaN warning by directly returning NaN
        return np.nan
    else:
        return np.nanmean(neighbours)

def _clip(value, clip_min, clip_max):
    if clip_min is not None and value <= clip_min:
        return clip_min
    if clip_max is not None and value >= clip_max:
        return clip_max
    return value

def blank_outside_mask(values, mask, fill_value = 0.0):
    """Outside masked region, replace all by fill_value. Inside mask, do not 
    touch data. Mask is bool array where True=keep."""
    values = values.copy() #do not modify original data
    maskedpoints = ~mask #select those *outside* of mask
    values[maskedpoints] = fill_value #avoid NaNs, but only in area where masked out!
    return values


if __name__=='__main__':
    # UNIT TEST of methods above
    import matplotlib.pyplot as plt
    from physicsbox import tictoc
    
    M, N = 40, 50
    beam_R = 15
    
    X, Y = np.meshgrid(np.arange(N),np.arange(M))
    X -= N//2 # make coords centered
    Y -= M//2
    R = np.sqrt(X**2 + Y**2)
    image = R**4 + 0.03*X**3
    image[R>beam_R] = np.nan
    
    derivY = image[1:,:] - image[:-1,:]
    derivX = image[:,1:] - image[:,:-1]
    
    derivY = np.concatenate([derivY, np.nan*np.zeros((1,N))])
    derivX = np.concatenate([derivX, np.nan*np.zeros((M,1))], axis=1)
    
    #image = derivX
    
    mask = np.ones_like(image, dtype=bool)
    maskR = R = np.sqrt((X-2)**2 + Y**2) # shifted in X by 2
    #mask[maskR>12] = False
    
    image_blank = blank_outside_mask(image, mask, fill_value=np.nan)
    
    # Destroy some values
    randmask = np.random.random(image.shape) > 0.80
    image_corrupt = image.copy()
    image_corrupt[randmask] = np.nan
    
    tictoc.tic()
    filled = inpaint_nan_inside_mask(image, mask)
    tictoc.printtoc()
    #filled = it(list(np.ndindex(image.shape))).reshape(image.shape)
    
    f, ax = plt.subplots(2, 2)
    
    vmin, vmax = np.nanmin(image), np.nanmax(image)
    #vmin, vmax = np.nanmin(filled), np.nanmax(filled)
    vmin *= 1
    vmax *= 2 # customize color scale
    
    ax[0,0].imshow(image, cmap='plasma', interpolation='nearest',
                   vmin=vmin, vmax=vmax)
    ax[0,0].set_title('Input image')
    ax[0,1].imshow(image_blank, cmap='plasma', interpolation='nearest',
                   vmin=vmin, vmax=vmax)
    ax[0,1].set_title('Input data blanked')
    ax[1,0].imshow(image_corrupt, cmap='plasma', interpolation='nearest',
                   vmin=vmin, vmax=vmax)
    ax[1,0].set_title('Input data corrupt')
    ax[1,1].imshow(filled, cmap='plasma', interpolation='nearest',
                   vmin=vmin, vmax=vmax)
    ax[1,1].set_title('Filled image')
    plt.show()
