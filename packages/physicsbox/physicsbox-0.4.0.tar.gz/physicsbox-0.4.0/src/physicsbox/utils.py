# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 18:51:52 2021

@author: Leonard.Doyle
"""

import numpy as np
import scipy.ndimage

def centroid(img):
    """Return centroid in pixel coordinates as (x,y).
    If centroid cannot be determined, returns (Nan, Nan)"""
    if img.ndim != 2:
        raise ValueError('Image shape must be 2D')
    if np.sum(img)==0.0:
        return (np.nan, np.nan)
    imgnorm = img/np.sum(img) #implicit float cast
    imgnorm = np.abs(imgnorm) #for centroid only weight not sign is important
    #TODO this is bullshit, what is mathematically correct?
    m_y,n_x = img.shape
    II,JJ = np.mgrid[0:m_y,0:n_x]
    #if top left corner of pixel is 0,0 and this is the only
    #full pixel, 0.5, 0.5 is the center of mass:
    c_x = np.dot(JJ.flat, imgnorm.flat) + 0.5
    c_y = np.dot(II.flat, imgnorm.flat) + 0.5
    return (c_x , c_y)

def imextent(img, dx=1, cx=None, cy=None, pixel_origin='center'):
    """
    Calculate the extent array as expected e.g. by matplotlib.imshow() given
    an image (or its shape) and a scaling dx. Optionally with shifted center.
    This assumes the default `origin`='upper'.
    If center X and Y (cx, cy in pixels) are None, the center
    will be in the middle of the image.
    If center X and Y are (0,0), the center will be in the top left corner
    of the image.
    `cx` and `cy` supplied in pixels, but can be fractional.
    For an even W or H,
    the center will be shifted to higher index as conventional.
    E.g. for 4x4 image X will be [-2, -1, 0, 1].
    
    :param img: Shape tuple or image to retrieve shape from
    :type img: array-like or PIL image, or floats tuple/array
    :param dx: Unit length per pixel, defaults to 1
    :type dx: float, optional
    :param cx: Pixel coordinate of image center in X, defaults to None. If
      None, `cx` is chosen to be in center of image.
    :type cx: int or float, optional
    :param cy: Pixel coordinate of image center in Y, defaults to None. If
      None, `cy` is chosen to be in center of image.
    :type cy: int or float, optional
    :param pixel_origin: If `center`, the grid coordinates lie
      on the pixel centers (matplotlib default). If `corner`, the
      grid coordinate values lie in the top left corner of each pixel.
    :type cy: int or float, optional
    :return: Array of extent coordinates [left, right, bottom, top]
    :rtype: ndarray

    """
    try:
        # if first arg is an image or similar, try to get it's shape
        shape = img.shape
    except AttributeError:
        # else hope that shape already is a tuple or similar
        shape = img
    
    h, w = shape[:2] #if dim>2, e.g. color channel, use only first 2
    
    if cx is None:
        cx = int(w/2)
    if cy is None:
        cy = int(h/2)
    
    H = (h-1)*dx
    W = (w-1)*dx
    xmin = 0 - dx*cx
    xmax = W - dx*cx
    ymin = 0 - dx*cy
    ymax = H - dx*cy
    
    if pixel_origin=='center':
        extent = np.array([(xmin-dx/2), (xmax+dx/2),
              (ymax+dx/2), (ymin-dx/2)]) #lrbt
    elif pixel_origin=='corner':
        extent = np.array([xmin, (xmax+dx),
              (ymax+dx), ymin]) #lrbt
    else:
        raise ValueError(f'Unknown argument pixel_origin=`{pixel_origin}`')
    return extent


def xy2polar(X, Y):
    """
    Convert array of cartesian coordinates into polar coordinates.
    Acts on any shape of array, element-wise. Therefore, X and Y must be same
    shape.
    
    :param X: X coordinates
    :type X: float or ndarray
    :param Y: Y coordinates
    :type Y: float or ndarray, same shape as X
    :return: (R, Phi) each with same shape as X, Y
    :rtype: tuple of floats or ndarrays

    """
    #inputs must have same shape
    RR =  X**2+Y**2
    R = np.sqrt(RR)
    Phi = np.arctan2(Y, X)
    return R, Phi


def polar2xy(R, Phi):
    """
    Convert array of polar coordinates into cartesian coordinates.
    Acts on any shape of array, element-wise. Therefore, R and Phi must be same
    shape.
    
    :param R: R coordinates
    :type R: float or ndarray
    :param Phi: Phi coordinates
    :type Phi: float or ndarray, same shape as R
    :return: (X, Y) each with same shape as R, Phi
    :rtype: tuple of floats or ndarrays

    """
    X = R*np.cos(Phi)
    Y = R*np.sin(Phi)
    return X, Y

def coord_array(N, dx=1, cx=None):
    """Build a coordinate array of length N
    with scaling `dx` and center coordinate `cx`
    (if given).
    `cx` supplied in counts/range index, but can be fractional.
    If None is given, it will be calculated automatically to
    place 0 in the middle of the array.
    For an even N,
    the center will be shifted to higher index as is conventional.
    E.g. for N=4 the returned array will be [-2, -1, 0, 1].
    """
    if cx is None:
        cx = int(N/2)
    return dx * (np.arange(N) - cx)

class ImageCoordSys:
    def __init__(self, img, dx=1, cx=None, cy=None, angle=0,
                 pixel_origin='center'):
        """
        Provide a coordinate system for a given image (or it's shape)
        and scaling. To be used e.g. for plot extent, coordinate axes
        arrays or full meshgrids in case of rotated coordinates.
        If angle is not 0, the extent is still supplied in horiz/vert view,
        only the meshgrid of coordinates is rotated.
        
        :param img: Shape tuple or image to retrieve shape from
        :type img: array-like or PIL image, or floats tuple/array
        :param dx: Unit length per pixel, defaults to 1
        :type dx: float, optional
        :param cx: Pixel coordinate of image center in X, defaults to None. If
          None, `cx` is chosen to be in center of image.
        :type cx: int or float, optional
        :param cy: Pixel coordinate of image center in Y, defaults to None. If
          None, `cy` is chosen to be in center of image.
        :type cy: int or float, optional
        :param angle: rotation angle (clockwise) in degree, defaults to 0
        :type angle: float, optional
        :return: coordinate system helper with convenient properties
        :rtype: ImageCoordSys

        """
        if dx == 0:
            raise ValueError('dx must be non-zero')
        
        try:
            # if first arg is an image or similar, try to get it's shape
            shape = img.shape
        except AttributeError:
            # else hope that shape already is a tuple or similar
            shape = img
        shape = shape[:2] #if dim>2, e.g. color channel, use only first 2
        
        h, w = shape
        if cx is None:
            cx = int(w/2)
        if cy is None:
            cy = int(h/2)
        
        self.shape = shape
        self.dx = dx
        self.cx = cx
        self.cy = cy
        self.angle = angle
        self.pixel_origin = pixel_origin

           
    @property
    def imextent(self):
        return imextent(self.shape, self.dx, self.cx, self.cy,
                        self.pixel_origin)

    
    @property
    def x_values(self):
        """Return 1d array of x-values on pixel center ignoring rotation."""
        return self.dx * (np.arange(self.shape[1])-self.cx)

    
    @property
    def y_values(self):
        """Return 1d array of y-values on pixel center ignoring rotation."""
        return self.dx * (np.arange(self.shape[0])-self.cy)


    @property
    def mgrid_xy(self):
        #behaves correclty for dx=1, cx=0,cy=0
        # correct for dx=1, cx=None,cy=None
        #correct for dx=.5, cx=1*dx, cy=2*dx
        
        dx = self.dx
        h, w = self.shape
        Y, X = np.mgrid[:h, :w]
        Y = Y * dx - dx * self.cy
        X = X * dx - dx * self.cx
        
        if self.angle:
            cc= np.cos(np.deg2rad(self.angle))
            ss=np.sin(np.deg2rad(self.angle))
            Xnew = (X*cc + Y*ss)
            Ynew = (X*(-ss) + Y*cc)
            X, Y = Xnew, Ynew

        return (X, Y)


    @property
    def X(self):
        """
        
        :return: grid of X coordinates, shaped like image.
        :rtype: ndarray

        """
        return self.mgrid_xy[0]


    @property
    def Y(self):
        """
        
        :return: grid of Y coordinates, shaped like image.
        :rtype: ndarray

        """
        return self.mgrid_xy[1]


    @property
    def mgrid_polar(self):
        X, Y = self.mgrid_xy
        # RR =  X**2+Y**2
        # R = np.sqrt(RR)
        # Phi = np.arctan2(Y, X)
        R, Phi = xy2polar(X, Y)
        return R, Phi


    @property
    def R(self):
        """
        
        :return: grid of R coordinates, shaped like image.
        :rtype: ndarray

        """
        return self.mgrid_polar[0]


    @property
    def Phi(self):
        """
        
        :return: grid of Phi coordinates, shaped like image.
        :rtype: ndarray

        """
        return self.mgrid_polar[1]
    
    def in_plot_coords(self, x, y):
        """
         Calculate the plot coordinates (always horiz/vert) given a pair
         or list of x and y coordinates in the images coord system.
         
        :param x: Value or list of values
        :type x: float, ndarray
        :param y: Value or list of values, same shape as x
        :type y: float, ndarray
        :return: Value pair or list pair, same shape as x
        :rtype: tuple

        """
        if type(x) in (list, tuple):
            x, y = np.asanyarray(x), np.asanyarray(y)
        
        if self.angle:
            cc = np.cos(np.deg2rad(-self.angle))
            ss = np.sin(np.deg2rad(-self.angle))
            Xnew = (x*cc + y*ss)
            Ynew = (x*(-ss) + y*cc)
            x, y = Xnew, Ynew

        return (x, y)


def img_rotate(img, angle, coords=None, around=None):
    """
    If just given (img, angle) works like scipy.ndimage.rotate().
    If coords is specified, the rotation will occur around the
    center of the ImageCoordSys.
    In the latter case, a new ImageCoordSys will be returned, matching
    the old coordinate system but related to the new image.
    The rotation of the old coord system is respected and added to `angle`.
    `around` is not implemented yet.

    Parameters
    ----------
    img : TYPE
        DESCRIPTION.
    angle : TYPE
        DESCRIPTION.
    coords : TYPE, optional
        DESCRIPTION. The default is None.
    around : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    img : TYPE
        DESCRIPTION.
    coords : TYPE
        DESCRIPTION.

    """
    if around is not None:
        raise NotImplementedError('`around` keyword not implemented yet.')
    if coords is None:
        return scipy.ndimage.rotate(img, angle)
    if img.shape[:2] != coords.shape:
        raise ValueError(
            'Image shape does not match coord system shape: {}!={}'.format(
                img.shape, coords.shape))
    
    #maybe not the most direct or efficient, but it works:
    cchelp = ImageCoordSys(img) #to get cx,cy=int(W/2,H/2)
    # since dx=1, coord system is in pixel units
    delX = coords.cx - cchelp.cx
    delY = coords.cy - cchelp.cy
    
    rimg = scipy.ndimage.rotate(img, angle)
    
    #TODO we have opposite convention to scipy, is there a "ground truth"?
    rcchelp = ImageCoordSys(rimg, angle=-angle) #rotated helper coord sys
    newX, newY = rcchelp.in_plot_coords(delX, delY)
    newX += int(rcchelp.shape[1]/2)
    newY += int(rcchelp.shape[0]/2)
    
    rout = ImageCoordSys(rimg, coords.dx, newX, newY, coords.angle-angle)
    
    return rimg, rout



