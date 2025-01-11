# -*- coding: utf-8 -*-
"""
Module to handle image data evaluation.
Given an input image and the geometry config, find the centroid
positions (and delta-deviation from each lenslet center) for each
lenslet. For those which are underexposed (0 intensity in entire subaperture),
this module can fill in interpolated/extrapolated values.

All functions only work with monochrome pictures, i.e. 2D shape, no color channel!

Created on Wed May 16 12:19:37 2018

@author: Leonard.Doyle
"""

import numpy as np
import scipy.ndimage.interpolation
from scipy.ndimage import center_of_mass

from .interpnan import inpaint_nan_inside_mask

def get_extent_rectangle(image_shape, pixelsize,
                         image_offset, padding = 0.0):
    """Return the extent rectangle (x, y, width, height)
    for plotting in [m] coordinates.
    If padding is not 0, rect is fraction 'padding' smaller
    (used for non-overlapping visualization of bounding rectangles.)"""
    x, y = image_offset
    height, width = image_shape
    height *= pixelsize
    width *= pixelsize
    if padding:
        x += width * padding/2
        y += height * padding/2
        width *= (1-padding)
        height *= (1-padding)
    return (x, y, width, height)

class ImageResult:
    #********** Class methods - Class factory ***********************
    
    @classmethod
    def from_config(cls, cfg):
        """Create fresh instance and fill all relevant values from config."""
        res = cls()
        res.M, res.N = cfg.M, cfg.N
        res.lens_f, res.lenspitch = cfg.lens_f, cfg.lenspitch
        res.image_offset = cfg.image_offset
        res.image_rotation = cfg.image_rotation
        res.pixelsize = cfg.pixelsize
        res.mask = cfg.combined_mask_array # in Result, no need to keep separate dotmask,
        # just use combined mask as if should/cannot be changed anymore
        return res

    #********** Instance methods ***********************
    
    def __init__(self):
        self.M, self.N = 0, 0
        self.lens_f = 0.0 # should Image know about this?
        # not really necessary but also not very consistent if it's the only missing one
        self.lenspitch = 0.0
        self.image_offset = (0, 0)
        self.image_rotation = 0.0
        self.pixelsize = 0.0
        self.mask = None
        
        #ImgEval
        self.raw_image = None #unrotated image as passed to Evaluator
        self.image = None #image as used for routine, rotated
        
        self.centroids = None
        self.center_spots = None
        self.centroid_deltas = None
        self.intensity_map = None
        self.sub_images = None
        self.invalids = None
        self.inpainted = None

    def get_extent_rectangle(self):
        """Return the extent rectangle (x, y, width, height) for plotting
        in [m] coordinates."""
        return get_extent_rectangle(self.image.shape, self.pixelsize,
                                    self.image_offset)

    def get_mean_displacement(self):
        # update: instead of using mask, we should use mask & valid
        # since by the time we are inside this result, a lot of
        # points may have been inpainted from NaN
        # -> respect only real data points and only inside mask
        # is probably what the user expects.
        valids = ~self.invalids
        to_use = valids & self.mask
        return get_mean_displacement(self.centroid_deltas, to_use)

    def estimate_rotation_angle(self):
        # respect only real data points (not interpolated) and only inside mask
        valids = ~self.invalids
        to_use = valids & self.mask
        return estimate_rotation_angle(self.centroid_deltas, self.lenspitch,
                                       to_use)

    @property
    def centroids_x(self):
        """Return a (flattened) list of all centroid X spots, e.g.
        to feed scatter plot"""
        return self.centroids[:,:,0].flatten()

    @property
    def centroids_y(self):
        """Return a (flattened) list of all centroid Y spots, e.g.
        to feed scatter plot"""
        return self.centroids[:,:,1].flatten()

    @property
    def center_spots_x(self):
        """Return a (flattened) list of all reference X spots, e.g.
        to feed scatter plot"""
        return self.center_spots[:,:,0].flatten()

    @property
    def center_spots_y(self):
        """Return a (flattened) list of all reference Y spots, e.g.
        to feed scatter plot"""
        return self.center_spots[:,:,1].flatten()

class Subimage:
    def __init__(self, image, origin = (0.0, 0.0), pixelsize = 1):
        """image is the subimage data, origin describes the top left edge (x, y) in
        (decimal) meter coordinates in the global coordinate system. Pixelsize
        in meters."""
        self.origin = origin
        self.pixelsize = pixelsize
        self.image = image
    
    def get_extent_rectangle(self, padding = 0.0):
        """Return a tuple of (x, y, width, height) where this subimage is placed
        in global coords. If padding is not 0, rect is fraction 'padding' smaller
        (used for non-overlapping visualization of bounding rectangles.)"""
        return get_extent_rectangle(self.image.shape, self.pixelsize,
                                    self.origin, padding=padding)

def generate_reference_spots(cfg):
    """Generate a dummy reference spot pattern where the centroid lies
    in the middle of each lenslet's pitch. Careful: MxN (y,x),
    but coordinate tuples are (x,y). All coords in meters.
    """
    M, N, lenspitch = cfg.M, cfg.N, cfg.lenspitch
    refcentroids = np.zeros((M, N, 2))
    for yy in range(M):
        for xx in range(N):
            x1 = (xx + 0.5)*lenspitch
            y1 = (yy + 0.5)*lenspitch
            refcentroids[yy, xx, :] = (x1, y1)
    return refcentroids

def image_to_centroids(cfg, input_image, inpaint_invalids=True,
                       strict=True):
    """
    Split the given image according to current config and find
    centroids.
    
    This method will also do some rather advanced inpainting of
    missing data:
    * We would like to see the centroid spots for all lenslets
      inside and outside the mask if they exist/ are not NaN
    * We would like to interpolate/extrapolate the spots
      for NaNs inside the mask, but not outside
    * interpolated values (i.e. having enough neighbours)
      will always lie between two measured values
    * extrapolated values, esp. at beam edges, may overshoot
      their lenslet bounding boxes, so values are clipped
      to be inside each lenslet box
    * We still keep track of which were valid
      and which were inpainted with `result.invalids`
      (any which had 0 intensity in sub-aperture)

    Parameters
    ----------
    cfg : physicsbox.wavefronts.GlobalConfig
        config object with grid geometry and mask definition
    input_image : ndarray
        image to analyse. must be 2D. Dark image subtraction
        etc. has to be done first. Rotation according to
        config is done inside this function.
    inpaint_invalids : bool, optional
        if points inside mask are too dark to evaluate,
        they will contain NaN. if enabled, replace
        these by interpolated/extrapolated
        values, by default True
    strict : bool, optional
        raise an error if too many points too dark, else
        simply continue but return NaNs in result,
        by default True

    Returns
    -------
    ImageResult
        object containings copies of the input data, config
        and output data (centroids, deltas)

    Raises
    ------
    ValueError
        In strict mode if too many lenslets inside mask
        are under-illuminated (0 sum).
    """
    img = scipy.ndimage.interpolation.rotate(input_image,
                                                cfg.image_rotation,
                                                reshape=False)
    #rotation: 0.2-0.25s
    
    #Split into sub images and
    # calculate centroids (in global [m] coords) and intensity weight map.
    subimgs = _splitimg(img, cfg.M, cfg.N, cfg.lenspitch, cfg.pixelsize, 
                        cfg.image_offset) #<0,01s
    centroids = _get_centroids(subimgs) #0,06 s
    intmap = _get_intensitymap(subimgs) #0,02 s
    #total time split, centroid, intmap: <0.1s
    
    mask = cfg.combined_mask_array
    invalids = (intmap == 0.0) #True/False array where underexposed
    inpainted = np.zeros_like(invalids)
    ref_spots = generate_reference_spots(cfg)
    centroid_deltas = centroids - ref_spots
    
    if inpaint_invalids:
        # safeguards:
        valids_in_mask_count = ((~invalids) & mask).sum()
        mask_count = mask.sum()
        if strict:
            required_percent_valid = 10
            percent_valid = 100 * (valids_in_mask_count/mask_count)
            if percent_valid < required_percent_valid:
                raise ValueError(f'Interpolating more than {100-required_percent_valid}%'
                                ' of the data, something might be wrong')
        if valids_in_mask_count == 0:
            # in strict mode, this is an error, but alrady raised above
            # in non-strict mode, we must be careful since
            # `inpaint_nan_inside_mask` would raise error, so simply skip
            # and return all-nans
            pass
        else:
            """
            inside the mask, get rid of any NaNs.
            considerations on stability and limits see `inpaint_...()`
            Here, choose to operate on the deltas, not the centroids.
            Firstly, they should be zero-centered, so inpainting should be
            easy by similarity to neighbours.
            Secondly, this allows us to easy apply a sanity threshold:
            any extrapolated spot displacement should not be outside of its
            grid cell.
            """
            deltas_X = centroid_deltas[:,:,0]
            deltas_Y = centroid_deltas[:,:,1]
            deltas_X = inpaint_nan_inside_mask(deltas_X, mask,
                                                clip_min=-cfg.lenspitch/2, clip_max=cfg.lenspitch/2,
                                                strict=strict)
            deltas_Y = inpaint_nan_inside_mask(deltas_Y, mask,
                                                clip_min=-cfg.lenspitch/2, clip_max=cfg.lenspitch/2,
                                                strict=strict)
            # not sure if this is redundant/non-existent, but it seems we may have a situation where e.g. delta_x
            # in one location was clipped, while delta_y is not -> make sure we have the same NaN fields in both,
            # otherwise confusing
            deltas_Y[np.isnan(deltas_X)] = np.nan # order does not matter, effectively works like a nan-OR on each point
            deltas_X[np.isnan(deltas_Y)] = np.nan
            centroid_deltas[:,:,0] = deltas_X
            centroid_deltas[:,:,1] = deltas_Y
            
            # reapply inpainted spots to centroids:
            centroids = ref_spots + centroid_deltas
            # do not inpaint intensity_map, let user see and debug it.

            # update `inpainted` array: True where
            # intensity invalid but value now exists
            inpainted = ~np.isnan(deltas_X) & invalids

    res = ImageResult.from_config(cfg)
    res.raw_image = input_image.copy()
    res.image = img
    res.sub_images = subimgs
    res.centroids = centroids
    res.center_spots = ref_spots
    res.centroid_deltas = centroid_deltas
    res.intensity_map = intmap
    res.invalids = invalids
    res.inpainted = inpainted
    res.mask = mask
    return res

def get_mean_displacement(deltas, mask=None):
    # assuming deltas as input where some are NaN,
    # but may be non-nan inside and outside of mask
    # -> first make outside mask NaN, then get mean of
    # all remaining
    assert deltas.ndim==3 # operate on combined deltasXY directly
    deltas_x = deltas[:,:,0]
    deltas_y = deltas[:,:,1]
    if mask is not None:
        deltas_x = deltas_x.copy()
        deltas_x[mask==False] = np.nan
        deltas_y = deltas_y.copy()
        deltas_y[mask==False] = np.nan
    # prevent all-nan warning by checking ourselves:
    xmean = np.nanmean(deltas_x) if not np.all(np.isnan(deltas_x)) else np.nan
    ymean = np.nanmean(deltas_y) if not np.all(np.isnan(deltas_y)) else np.nan
    return xmean, ymean

def estimate_rotation_angle(deltas, lenspitch, mask=None):
    """Given the relative spot displacements `deltas` (MxNx2),
    calculate the curl of the 2D vector field and estimate
    the rotation angle of the microlens array (MLA) with respect to the
    camera.
    In absence of e.g. spiral phase plates, the wavefront is
    curl-free, since the slopes are measurements of a scalar,
    differentiable field. Any curl is therefore purely related
    to the misalignment between the MLA and the camera.
    The `deltas` and `lenspitch` have to share the same real-world
    units.
    Math background:
    * My simplistic derivation is probably far from elegant, but somehow
      got me the right answer
    * Consider only the slopes in the center of the rotation:
      here, going left on the horizontal x-axis results in a displacement
      Fy of points over a distance `lenspitch:=l`, so
      DFy/dx = (Fy_j+1 - Fy_j)/l
      At the same time, the triangle `DFy` and `l` is formed by rotation
      with angle `alpha` according to `tan(alpha)~=DFy/l`
      going down on the vertical y-axis results in a displacement
      Fx of points over the same distance DFx/dy = (Fx_i+1 - Fx_i)
      Again this is equal to `tan(alpha)`
    * In 2D, the curl is defined as curlF=DFy/dx-DFx/dy
      Substituting above relations, we get curlF = 2*tan(alpha)
    * While this was only shown for the origin point, the curl
      has no global reference and the formula applies globally
    * We can therefore estimate the rotation angle
      `alpha=arctan(1/2*curlF_average)` over all curl values on the grid
    * To make the predition more robust, respect the `mask` if specified
      and only consider non-NaN points inside the mask for the estimation.

    Parameters
    ----------
    deltas : ndarray
        MxNx2 array of displacements in X and Y (as last array dim)
    lenspitch : float
        distance between two delta points in same units (typically [m])
    mask : ndarray, optional
        If specified, must be MxN, by default None
        Any point where `mask` is 0 will not be considered for the estimation

    Returns
    -------
    float
        estimated angle in degrees
    """
    # assuming deltas as input where some are NaN,
    # but may be finite inside and outside of mask
    # -> first make outside mask NaN
    assert deltas.ndim==3 # operate on combined deltasXY directly
    deltas_x = deltas[:,:,0]
    deltas_y = deltas[:,:,1]
    if mask is not None:
        deltas_x = deltas_x.copy()
        deltas_x[mask==False] = np.nan
        deltas_y = deltas_y.copy()
        deltas_y[mask==False] = np.nan
    #DFx_dx = 1/lenspitch * np.diff(deltas_x, 1, 1)[:-1,:] # shrink other dim to make all 1 shorter
    DFx_dy = 1/lenspitch * np.diff(deltas_x, 1, 0)[:,:-1]
    DFy_dx = 1/lenspitch * np.diff(deltas_y, 1, 1)[:-1,:]
    #DFy_dy = 1/lenspitch * np.diff(deltas_y, 1, 0)[:,:-1]
    curlF = DFy_dx - DFx_dy
    # prevent all-nan warning by checking ourselves:
    curl_mean = np.nanmean(curlF) if not np.isnan(curlF).all() else np.nan
    alpha_deg = np.rad2deg(np.arctan(curl_mean/2))
    return alpha_deg

def _splitimg(img, M, N, lenspitch, pixelsize, offset=(0, 0)):
    """Split image into MxN subimages, starting at imoffset and going lens-
    pitch forward for each subimage. Resulting top-left corner is saved
    together with subimage to be able to track fraction-of-pixel coordinates"""
    #v2 for performance, keep in 1 function to avoid recalculation of same values
    #massive performance increase from 0.17s for 45x36 subimgs to 0.01s
    off_x, off_y = offset #unpack
    dimy, dimx = img.shape
    
    xarr = np.arange(N)
    x1arr = xarr*lenspitch
    x2arr = (xarr+1)*lenspitch
    x1a_px = np.floor((x1arr-off_x)/pixelsize).astype(int)
    x2a_px = np.ceil((x2arr-off_x)/pixelsize).astype(int)
    x1a_px = np.clip(x1a_px, 0, dimx)
    x2a_px = np.clip(x2a_px, 0, dimx)
    
    yarr = np.arange(M)
    y1arr = yarr*lenspitch
    y2arr = (yarr+1)*lenspitch
    y1a_px = np.floor((y1arr-off_y)/pixelsize).astype(int)
    y2a_px = np.ceil((y2arr-off_y)/pixelsize).astype(int)
    y1a_px = np.clip(y1a_px, 0, dimy)
    y2a_px = np.clip(y2a_px, 0, dimy)
    
    #origin = global coords of top left of this subimage
    neworig_x = x1a_px * pixelsize + off_x
    neworig_y = y1a_px * pixelsize + off_y
    
    subimages = np.empty((M, N), dtype=object)
    for yy in range(M):
        y1_px = y1a_px[yy]
        y2_px = y2a_px[yy]
        for xx in range(N):
            x1_px = x1a_px[xx]
            x2_px = x2a_px[xx]
            subimg = img[y1_px:y2_px, x1_px:x2_px].copy()
            neworigin = (neworig_x[xx], neworig_y[yy])
            subimages[yy, xx] = Subimage(subimg, neworigin, pixelsize)
    return subimages

def _get_centroids(sub_images):
    """Calculate centroids for all subimages and return MxN numpy array of 
    tuples (x,y) of each centroid."""
    centroids = np.zeros((sub_images.shape[0],sub_images.shape[1],2))
    for yy in range(sub_images.shape[0]):
        for xx in range(sub_images.shape[1]):
            centroids[yy, xx, :] = _get_centroid(sub_images[yy, xx])
    return centroids

def _get_centroid(sub_image):
    """Return centroid in global coordinates (including subimg offset) as
    decimal meters (x, y). If centroid cannot be determined, returns (Nan, Nan)"""
    if np.sum(sub_image.image)==0.0:
        return (np.nan, np.nan)
    c_y, c_x = center_of_mass(sub_image.image)
    #if top left corner of pixel is 0,0 and this is the only full
    # pixel, 0.5, 0.5 is the center of mass:
    c_x += 0.5
    c_y += 0.5
    c_x = c_x * sub_image.pixelsize + sub_image.origin[0]
    c_y = c_y * sub_image.pixelsize + sub_image.origin[1]
    return (c_x, c_y)
    
def _get_intensitymap(sub_images):
    """Calculate the averaged intensity in each subimage to reconstruct a low
    resolution intensity profile of the beam. Normalized over subimage size
    since this is not same for each subimage.
    If a subimage slice lies outside the source image, i.e. contains no pixels,
    the value will be NaN in the output."""
    intmap = np.zeros(sub_images.shape)
    for yy in range(sub_images.shape[0]):
        for xx in range(sub_images.shape[1]):
            subimg = sub_images[yy,xx].image
            if subimg.size > 0:
                intmap[yy, xx] = subimg.mean()
            else:
                # prevent warning "mean of empty slice"
                # also, change from `nan` to 0.0 to guarantee
                # finite float value in entire intensitymap
                intmap[yy, xx] = 0.0
    return intmap
