# -*- coding: utf-8 -*-
"""

Add functionality to average wavefront data,
subtract tip/tilt
and in the future allow a Zernike decomposition

Created on Tue Jan 21 22:34:30 2020

@author: Lenny
"""

import numpy as np
import scipy.linalg
SCIPY_LAPACK_DRV = 'gelsy' # 'gelsy', 'gelsd'(default), 'gelss', see phaseeval

import numpy as np


def filter_tip_tilt(phasemap):
    """Remove the tip and tilt of the given phasemap result.
    If phasemap is all-NaN, returned value will be all-NaN, too.
    """
    if np.isnan(phasemap).all():
        # nothing to do, save some effort since would be all-NaN anyway
        return phasemap.copy()
    # to make the fit work, also need to fit piston term.
    mappiston = np.ones_like(phasemap)
    maptiltx = np.cumsum(np.ones_like(phasemap),1)
    maptilty = np.cumsum(np.ones_like(phasemap),0)
    
    mapvalidflat = phasemap[~np.isnan(phasemap)]
    mappistonflat = mappiston[~np.isnan(phasemap)]
    maptiltxflat = maptiltx[~np.isnan(phasemap)]
    maptiltyflat = maptilty[~np.isnan(phasemap)]
    
    fits = np.column_stack([mappistonflat,maptiltxflat,maptiltyflat])
    
    sol, resid, rank, sing = scipy.linalg.lstsq(
            fits, mapvalidflat.reshape(-1,1),
            lapack_driver=SCIPY_LAPACK_DRV)
    piston, tiltx, tilty = sol[0][0], sol[1][0], sol[2][0]
    filtered_phase = phasemap.copy()
    filtered_phase -= piston * mappiston
    filtered_phase -= tiltx * maptiltx
    filtered_phase -= tilty * maptilty
    return filtered_phase

def compute_ptv(phasemap):
    """Given the phasemap result, calculate the
    Peak to Valley deviation of the wavefront.
    Since mask is applied by setting values outside to NaN, only use
    non-NaN values for the calculation. If phasemap is all-NaN, return
    NaN for the metrics."""
    if np.all(np.isnan(phasemap)):
        ptv = np.nan
    else:
        ptv = np.nanmax(phasemap) - np.nanmin(phasemap)
    return ptv

def compute_rms(phasemap):
    """Given the phasemap result, calculate the RMS
    (root mean square) deviation of the wavefront.
    Since mask is applied by setting values outside to NaN, only use
    non-NaN values for the calculation. If phasemap is all-NaN, return
    NaN for the metrics."""
    if np.all(np.isnan(phasemap)):
        rms = np.nan
    else:
        target = np.zeros_like(phasemap) #target is a flat phase front
        target_list = target[~np.isnan(phasemap)]
        pmap_list = phasemap[~np.isnan(phasemap)]
        rms = np.sqrt(((pmap_list - target_list)**2).mean())
    return rms

class AveragingEvaluator:
    """This evaluator stores a set number of wavefronts and can return
    a moving average phasemap. If the averaging setting is changed, the list
    of last results is truncated/extended on the fly.
    """
    def __init__(self, averaging=1):
        self._averaging = 1
        self.averaging = averaging
        self.last_values = []

    @property
    def averaging(self):
        return self._averaging

    @averaging.setter
    def averaging(self, value):
        self._averaging = max(1, value) # ensure >= 1

    def evaluate(self, data):
        """Create a moving average based on the previously evaluated results
        by this object and return the new average.
        Caution: no safeguards to match data shapes etc, will raise errors
        when attempting to combine these.
        
        Since we changed the evaluation to be non-strict and simply return
        all-NaN arrays for e.g. completely dark images, we need to safeguard
        here:
        If we include it in the average, we would have to wait for `averaging`
        iterations to get rid of it again.
        But if we simply ignore it, we may have very old frames in the buffer
        if all-NaN for a long time.
        To keep the code simple, we do add them to the buffer, but ignore
        all-NaNs when forming the average!
        If there is no single valid datapoint, all-Nan is returned, too."""
        if self.averaging <= 1:
            self.last_values.clear()
            self.last_values.append(data) # mirror for user
            return data
        else:
            self.last_values.append(data)

            #pop first items in list if too many:
            if len(self.last_values) > self.averaging:
                self.last_values = self.last_values[-self.averaging:]
            
            avg_data = np.zeros_like(data)
            count = 0
            for old_data in self.last_values: # already includes new data!
                if not np.all(np.isnan(old_data)):
                    avg_data += old_data
                    count += 1
            if count > 0:
                avg_data /= count
            else:
                avg_data *= np.nan
            return avg_data
    
    def reset(self):
        """In case M, N or mask change, averaging is not sensible and e.g.
        changing M/N will even result in error (mismatch in phasemap size).
        Reset the list of previous averages in this case to prevent error."""
        self.last_values.clear()
