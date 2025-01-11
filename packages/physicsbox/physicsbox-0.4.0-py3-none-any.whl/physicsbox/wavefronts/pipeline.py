# -*- coding: utf-8 -*-
#
# This file is part of the Physicsbox project
#
# (c) 2024 Leonard Doyle
#
# Distributed under the terms of the MIT license.
# See LICENSE.txt for more info.

"""
# Shack-Hartmann Wavefront Reconstruction module #

Based on previous work, this module contains a boiled down version of
the wavefront reconstruction algorithm written in Leonards master's 
thesis.

Some useful hints were provided by Jannik Esslinger.


## Regarding the reference: ##

There are two potential ways to define a reference:
1. reference image: The spot pattern is "the ground truth" so any
    time a config parameter changes (e.g. rotation, pitch, ...)
    the reference should be recalculated.
2. reference wavefront: The reconstructed wavefront from a reference
    image is "the ground truth". When changing e.g. the offset,
    the reference should not be recalculated.
In code, it is impossible to know which the user wants.

Mathematically speaking, both are described by the reference spots
shifting with respect to their nominal position at the center of
each lenslet. Since the entire reconstruction is based on linear
algebra, and in particular the inversion of the system of equations
is done with the constructed matrix, but without actual data,
there is no difference in applying the shift of reference first
or later (after reconstruction).
Therefore the possibility to add a reference early was omitted
completely! Instead, a reference wavefront can be subtracted later.
The user then has to take care to make sure it is based on the same
valid geometry parameters.

"""
import pickle

import numpy as np

from .baseclasses import GlobalConfig
from .helpers import suggest_MN
from .imageevaluation import image_to_centroids, get_extent_rectangle
from .wavefrontreconstructor import ZonalWavefrontReconstructor
from .postprocessing import compute_ptv, compute_rms, filter_tip_tilt, AveragingEvaluator
from .zernikefit import ZernikeFit


class PipelineResult:
    """Full result with non-existent fields filled with None. Can be passed
    along and partially filled by eval pipeline."""
    
    #********** Class methods - Class factory ***********************
    
    @classmethod
    def load_binary(cls, uri):
        """Reload the previously saved result in binary format."""
        res = None
        with open(uri, 'rb') as pkl_file:
            res = pickle.load(pkl_file)
        return res
    
    #********** Instance methods ***********************
    
    def __init__(self):
        self.image_result = None
        self.wavefront_result = None
        self.averaging = 0
        self.remove_tiptilt = False
        self.processed_phasemap = None
        self.metrics = {}

    def save_binary(self, uri, overwrite=False):
        """Save the result in binary (pickled) format. This format includes all
        information necessary to redo the analysis of the contained raw images
        in the future."""
        fmode = 'wb' if overwrite else 'xb'
        with open(uri, fmode) as fout:
            pickle.dump(self, fout, -1) # use highest protocol

class WavefrontPipeline:
    """
    Main handling class for complete image reconstruction.
    Wraps more detailed classes and methods to provide a clean,
    easy-to-use interface.

    Once initialized, an instance of the Analysis class can take an image,
    evaluate it and return the analysis result.

    Methods are provided for loading and saving of the analysis settings, matrix
    and individual results

    This class is not thread safe! Changing a config parameter
    while evaluate_img() is running may cause unexpected errors.
    """
    #********** Class methods - Class factory ***********************

    @classmethod
    def load_instance(cls, fname):
        """Create a pipeline object and apply the settings from pickle binary
        file saved earlier.
        
        Remark on the auxiliary settings:
        While the internal pipeline settings (config, reference, matrix)
        can be easily applied internally, the `auxiliary_settings`
        dict provided for convenience is a passive dict.
        The caller has to then read the values from that dict and update
        their settings accordingly. E.g. the camera settings in
        WavesensorUI are reapplied with `camworker.apply_settings(...)`.
        Crucially, after that, the link in `auxiliary_settings` should
        be updated to reference the current camera settings dict.
        This way, the next save() can also include the current values, there.
        """
        with open(fname, 'rb') as pkl_file:
            settings = pickle.load(pkl_file)
        cfg = settings['config'] # implicitly check for KeyError
        reference = settings['reference']
        aux_settings = settings['auxiliary_settings']
        averaging = settings['averaging']
        remove_tip_tilt = settings['remove_tip_tilt']
        matrix_settings = settings['matrix']
        wpl = cls()
        wpl.cfg.apply_dict(cfg)
        # applying the settings to phaseeval, no checks are 
        # done, instead simply hope the stored value will 
        # match our global config...
        wpl.phaseeval.apply_dict(matrix_settings)
        wpl.reference = reference
        wpl._auxiliary_settings = aux_settings
        wpl.averaging = averaging
        wpl.remove_tip_tilt = remove_tip_tilt
        return wpl

    #************* Public properties ***************

    @property
    def cfg(self):
        """Reference to the global config parameter set."""
        #as read-only property to avoid overwrite, just change child attr.
        return self._cfg

    @property
    def auxiliary_settings(self):
        """A publicly exposed dict which can be used to store references
        to other config dicts. Concretely, this is used as a workaround
        to store camera config settings and dark image objects which
        don't actually belong to analysis, but should be saved in its binary
        form anyway.
        """
        #as read-only property to avoid overwrite, just change child attr.
        return self._auxiliary_settings

    @property
    def reference(self):
        """Set a reference wavefront/phasemap. This is subtracted from the
        reconstructed wavefront each time.
        Set to None to reset (assume perfect regular grid as reference).
        The shape is not checked immediately, but if the shape does not match
        MxN an error will be raised the next time a phasemap is reconstructed.
        """
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value

    @property
    def averaging(self):
        return self.avgeval.averaging

    @averaging.setter
    def averaging(self, value):
        self.avgeval.averaging = value

    @property
    def is_matrix_built(self):
        return self.phaseeval.is_matrix_built

    @property
    def is_matrix_valid(self):
        return self.phaseeval.check_matrix_valid(self.cfg)

    @property
    def is_reference_valid(self):
        if self.reference is None:
            return True
        else:
            return self.reference.shape == (self.cfg.M, self.cfg.N)

    @property
    def is_reference_partially_nan(self):
        if not self.is_reference_valid:
            #TODO this is ugly, maybe clarify naming or so
            return True
        # only makes sense to check if everything same size
        mask = self.cfg.combined_mask_array
        # select only items in reference that are not masked
        # in data currently:
        reference_of_interest = self.reference[mask]
        return np.any(np.isnan(reference_of_interest))

    #********** Instance methods ********************************

    def __init__(self):
        """Instanciate a fresh evaluator with default settings. Do not yet
        build any matrices until settings have been changed. Therefore this
        does not take long."""
        
        self._cfg = GlobalConfig()
        self._auxiliary_settings = {}
        
        self._reference = None
        self.remove_tip_tilt = False

        self.phaseeval = ZonalWavefrontReconstructor(
            self.cfg, buildmatrix=False)
        self.avgeval = AveragingEvaluator()

    def save_instance(self, fname, overwrite=False):
        """New format saving method. Simply saving the pipeline
        object into a pickle is easy, but almost certainly breaks
        compatibility anytime a change is made to any of the 
        pipeline subclasses.
        On the other hand, saving just parameters as TXT (e.g. json)
        is not enough, since we also want to store dark images etc.
        (And if we are binary anyway, store the matrix, saving a couple
        of seconds during load by avoiding recalculation).
        Instead, the new format goes the extra step to translate all important
        parameters and settings to basic python types (and numpy arrays).
        This should be robust to import in future, and we can even add
        backwards-compatibility methods where necessary.

        Because the file contains the full matrix, it may be
        very large (20-50 MB)!

        Parameters
        ----------
        fname : str
            target file name
        overwrite : bool, optional
            If True, allow overwrite existing file, else raise Error,
            by default False
        """
        out = {}
        out['config'] = self.cfg.to_dict()
        out['reference'] = self.reference # None or ndarray
        out['auxiliary_settings'] = self.auxiliary_settings
            #TODO should loop the aux_settings and make sure
            # they are only basic Python and numpy types?
            # for now, trust callers (WavesensorUI)...
        out['averaging'] = self.averaging # int
        out['remove_tip_tilt'] = self.remove_tip_tilt # bool
        out['matrix'] = self.phaseeval.to_dict()
        fmode = 'wb' if overwrite else 'xb'
        with open(fname, fmode) as fout:
            pickle.dump(out, fout)

    def update_matrix(self):
        """If matrix is not built or not up to date with global settings,
        needs a re-build. Since this can take several seconds, let user decide
        when to trigger it."""
        if not self.is_matrix_valid:
            self.phaseeval.update_matrix(self.cfg)
            self.avgeval.reset() #reset last results to get sensible average
    
    def reset_matrix(self):
        self.phaseeval.reset_matrix()

    def evaluate_image(self,
                       img):
        """Reconstruct wavefront/phase map from input image.
        The image should be background-subtracted and thresholded
        first (if desired). The only further processing inside
        this function is the rotation of the image according
        to the configured parameters.

        The image will be passed "down the pipeline" and the
        wavefront reconstructed. If e.g. matrices partially built,
        will return result as far as possible (e.g. only img data and spots).

        During the analysis, a result structure is built
        containing the reconstructed phasemap and additional info like
        all params, all raw data, ...

        Parameters
        ----------
        img : array-like
            2D image to evaluate
        """
        
        res = PipelineResult()
        res.averaging = self.averaging
        res.remove_tiptilt = self.remove_tip_tilt
        
        # using inpaint_invalids=True and strict=False, the resulting spot
        # pattern will have valid numbers all inside the mask. Only exception:
        # completely dark image, in this case will have all-NaN
        res.image_result = image_to_centroids(self.cfg, img,
                                              inpaint_invalids=True, strict=False)
        
        # for wavefront reconstruction, if one single (or more) number inside mask
        # is NaN, the matrix multiplication will spread that and create an all-NaN
        # result. In strict=True mode, this would raise an error. In strict=False,
        # simply return NaN-wavefront and continue
        res.wavefront_result = self.phaseeval.evaluate_spot_deltas(self.cfg,
                                                                   res.image_result.centroid_deltas,
                                                                   strict=False)
        # new behaviour: continue with analysis even if NaN-result.
        # in this case, simply return NaNs.
        # this is better than having None fields for user side code than
        # partial result
        pmap = res.wavefront_result.phasemap
        """
        A word on calculation order:
        * getting the centroid from an image is a linear operation:
          averaging raw images and then taking centroid yields same result
          as averaging centroid coordinates (assuming thresholding etc.
          are applied before raw image averaging)
        * reconstructing the wavefront from the spots is a linear operation
          (matrix multiplications only)
        * averaging is a linear operation (a sum and prefactor)
        * removing tip-tilt is a "linear operation", i.e. taking average first
          or averaging the tilt-removed wavefronts yields same result
        * more generally, adding/subtracting any constant grid (e.g. a Zernike
          mode like Tip, but also higher orders, and of course
          the `reference`) is "linear" in the above sense
        -> the order of these operations does not matter much, unless e.g.
          reference is changed on the fly
        -> decide here to do averaging first, such that changes to `reference`
          or `remove tilt` or `Zernike mode filtering` will apply in 1 cycle
        """
        if self.averaging:
            pmap = self.avgeval.evaluate(pmap)
        if self.reference is not None:
            if self.reference.shape != pmap.shape:
                # even in non-strict mode, raise error, since this needs to
                # be corrected asap by user.
                raise ValueError(f'Mismatch between shape of phasemap {pmap.shape}'
                                    f' and reference {self.reference.shape}.'
                                    'Please reset/redefine reference.')
            pmap = pmap - self.reference
        if self.remove_tip_tilt:
            pmap = filter_tip_tilt(pmap)
        res.processed_phasemap = pmap
        fit_coefficients = 40
        if self.cfg.pupil_diameter > 0:
            # fit will error if no radius defined (and nonsense anyway)
            # not aware of any other error-sources for now
            j_fits, A_fits = ZernikeFit(pmap, fit_coefficients, self.cfg.pupil_center,
                                        self.cfg.pupil_diameter)
        else:
            #TODO should downstream code rely on these being present??
            j_fits, A_fits = np.asarray([1,]), np.asarray([0.0,])
        ptv = compute_ptv(pmap)
        rms = compute_rms(pmap)
        res.metrics = {'ptv': ptv,
                       'rms': rms,
                       'j_zern': j_fits,
                       'A_zern': A_fits}
        return res

    def get_image_extent(self, image_shape):
        """Given the image shape, return a tuple (x,y,width,height)
        in global [m] coordinates for plotting extent."""
        return get_extent_rectangle(image_shape, self.cfg.pixelsize,
                                    self.cfg.image_offset)

    def suggest_MN(self, image_shape, tight=True):
        """Return a suggestion (M, N) of maximum useful phasemap size given
        current params and image size. If tight, only include full subapertures
        on bottom right, if not tight, also include partial ones."""
        return suggest_MN(image_shape, self.cfg.lenspitch, self.cfg.pixelsize,
                          self.cfg.image_offset, tight=tight)
