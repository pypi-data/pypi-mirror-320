# -*- coding: utf-8 -*-
"""
Common methods

Created on Wed May 16 13:06:38 2018

@author: Leonard.Doyle
"""

import numpy as np

def circular_mask(pmap, radius=None, center=None):
    """Define a circular mask (of True and False) with same size as pmap and
    given radius and center."""
    #from
    #https://stackoverflow.com/questions/44865023/
    # circular-masking-an-image-in-python-using-numpy-arrays
    h, w = pmap.shape
    if center is None: # use the middle of the image
        center = [int(w/2), int(h/2)]
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    
    pmasked = np.ones_like(pmap, dtype=bool)
    pmasked[dist_from_center > radius] = False
    return pmasked

def suggest_MN(imgshape, lenspitch, pixelsize, imoffset = (0,0), tight=True):
    """Return a suggestion (M, N) of maximum useful phasemap size given
    current params and image size. If tight, only include full subapertures
    on bottom right, if not tight, also include partial ones (possibly 
    almost empty, giving nan results)."""
    """Choose largest sensible M, N matching image size, respecting offset.
    If tight, exlude partial fields on bottom right since they may produce Nan."""
    height, width = imgshape
    width *= pixelsize
    height *= pixelsize
    newwidth = width + imoffset[0]
    newheight = height + imoffset[1]
    if tight:
        noofpointsx = int(np.floor(newwidth/lenspitch))
        noofpointsy = int(np.floor(newheight/lenspitch))
    else:
        noofpointsx = int(np.ceil(newwidth/lenspitch))
        noofpointsy = int(np.ceil(newheight/lenspitch))
    return (noofpointsy,noofpointsx)