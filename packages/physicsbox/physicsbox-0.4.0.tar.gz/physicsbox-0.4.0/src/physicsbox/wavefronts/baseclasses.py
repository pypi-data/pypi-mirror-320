# -*- coding: utf-8 -*-
"""
Common classes and definitions

Created on Wed May 16 13:06:38 2018

@author: Leonard.Doyle
"""

import numpy as np

from .helpers import circular_mask


class GlobalConfig:
    """Global parameters relevant to more than 1 evaluation stage.
    Inside each stage, avoid to keep own copies of these variables
    if possible to ensure always using the most current value.
    The only exceptions might be when changing a certain parameter
    will lead to a large recalculation of e.g. some matrix."""
    def __init__(self):
        self.M = 5 # avoid bugs that appear only with 0,0 maps
        self.N = 5 # 5 is arbitrary
        self.lenspitch = 150e-6 #[m] MLA150-5C defaults
        self.lens_f = 4.1e-3 #[m]
        self.pixelsize = 5.3e-6 #[m] uEye UIx241-defaults
        self.image_offset = (0.0, 0.0) #[m]
        self.image_rotation = 0.0 #[deg]
        self.pupil_diameter = 0 #if 0, no circular mask
        self.pupil_center = (0, 0) #[x, y]
        self._dotmask = None

    def to_dict(self):
        """Build a dictionary containing all parameters
        fully describing this config object. However, the returned output
        dict only contains basic Python and numpy types.
        Therefore, storing it with e.g. `pickle` will be much easier
        than storing the config object itself.
        (For one, `GlobalConfig` must be importable when unpickling,
        and secondly, if it ever changes the chances are high this will
        break backward compatibility.)

        Returns
        -------
        dict
            dictionary of all relevant parameters in simplistic format
        """
        #NB: yes this probably can be done with fancy introspection,
        # but I am a friend of explicit over clever...
        out = {
            'M': self.M,
            'N': self.N,
            'lenspitch': self.lenspitch,
            'lens_f': self.lens_f,
            'pixelsize': self.pixelsize,
            'image_offset': self.image_offset,
            'image_rotation': self.image_rotation,
            'pupil_diameter': self.pupil_diameter,
            'pupil_center': self.pupil_center,
            'dotmask': self.dotmask,
        }
        return out

    def apply_dict(self, values, strict=False):
        """Apply the settings given to this config object.
        If a setting is not inside the input dictionary, no action
        is taken.
        If a setting specified is not valid for this class, the action
        depends on the `strict` setting:
        If strict, will raise error about unknown setting specified.
        If not strict, will simply ignore (useful in the future when
        removing or renaming attributes.)

        Parameters
        ----------
        values : dict
            dictionary of settings where key is the parameter name in
            this class
        strict : bool, optional
            raise error if unknown setting key supplied, by default False

        Raises
        ------
        KeyError
            if `strict=True` and unknown setting key is supplied
        """
        for k,v in values.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                if strict:
                    raise KeyError(f'Unknown setting key supplied: {k}')

    @property
    def dotmask(self):
        """A pixelwise map defining if lenslet is used (True) or masked out (False)
        Is either None or array of size (M,N)."""
        return self._dotmask
    
    @dotmask.setter
    def dotmask(self, value):
        """Set an array mask of True and False the same size as the phase map.
        This mask will be ANDed with circular pupil.
        Set None to disable. An array of all 1s will also be set to None"""
        if value is None:
            self._dotmask = None
        else:
            assert value.dtype == bool
            if np.array_equiv(value, True):
                # a mask of all 1s is no mask
                dotmask = None
            else:            
                dotmask = value.copy()
            self._dotmask = dotmask

    @property
    def dotmask_array(self):
        """Return an array of the current dotmask.
        True means include, False means exclude.
        This property always returns an array of
        size MxN, even if no dotmask is set (i.e. 
        set to None). To check if it is set, better
        use `.dotmask` property.

        Returns
        -------
        ndarray
            MxN bool array, True=included, False=masked
        """
        dmask = self.dotmask
        if dmask is None:
            return np.ones((self.M, self.N), dtype=bool)
        else:
            return dmask

    @property
    def is_dotmask_valid(self):
        """Check whether the dotmask has correct dimensions matching MxN.
        Always True if dotmask is not set."""
        if self.dotmask is None:
            return True
        return self.dotmask.shape == (self.M, self.N)

    @property
    def pupil_mask_array(self):
        """Return an array of the current pupil mask.
        This property always returns an array of
        size MxN, even if no pupil is set (i.e. 
        diameter = 0). To check if it is set, better
        use `.pupil_diameter`.

        Returns
        -------
        ndarray
            MxN bool array, True=included, False=masked
        """
        x, y = self.pupil_center
        diam = self.pupil_diameter
        mask = np.ones((self.M, self.N), dtype=bool)
        if self.pupil_diameter > 0:
            mask = circular_mask(mask, diam/2, (x,y))
        return mask

    @property
    def combined_mask_array(self):
        """Boolean AND of the dotmask and the pupil definition. This is the
        mask that will be used to evaluate the wavefront.
        If the dotmask is None and the pupil diameter is set to 0 (off),
        this will not return None, but an array of size MxN with True."""
        #Tictoc 10000 iterations results in 0.45s -> 45us per iter
        # on the fly calc is fine, this avoids having a combinedmask with
        # wrong shape due to outdated calc.
        if not self.is_dotmask_valid:
            raise ValueError('Dot mask does not have correct size (MxN)')
        dmask = self.dotmask_array # always an array, even if dotmask=None
        pmask = self.pupil_mask_array
        mask = dmask & pmask

        if np.all(mask==False):
            raise ValueError('Combined mask is all 0, check pupil and dotmask')

        return mask
