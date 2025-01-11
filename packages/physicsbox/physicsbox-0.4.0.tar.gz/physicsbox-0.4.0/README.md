# physicsbox

Collection of useful calculations for optics and more.
Intended to be a little toolbox/swiss army knife for everyday Python tasks for physists.

# Requirements

* numpy
* scipy
* (optional) numba to speed up OAP calculations

# Installation

Since the package is still under development, I recommend to clone this git
repository to your local machine and install the package in "develop" mode
via `pip`.

* `git clone https://gitlab.lrz.de/cala-public/packages/physicsbox.git`
* `cd physicsbox`
* `pip install -e .` where the `-e` installs in develop mode and `.` executes the `setup.py` in the current folder

If you make improvements to the package or want to download more recent
commits, you can now just use `git push/pull` as usual.

# Features

So far, the package contains the following submodules:
* `.units` which defines constants like `m=1, mm=1e-3` and so on to use in your code
* `.utils` contains some coordinate system handling that can be used to plot e.g. an image to scale easily
* `.optics` for
    * laser pulse calculations (power, energy, focus size etc. by typical formulas)
    * Gaussian pulse (in time and space) function definitions for 1d, 2d, 3d Gauss calculations
* `.relativity` is pretty basic so far, only contains a few formulas for relativistic energy/momentum etc.
* `.wavefronts` contains classes for reconstructing a wavefront from Shack-Hartmann images (see examples for use)
* `.oap` contains a class for vectorial calculation of the focus of an off-axis parabolic mirror
* Check out the examples for some things that this package is intended for.

# Contributing

* This started out as a private little helper project, if you have any suggestions just contact me.
* If you wish to make improvements or add new examples/ features, best create a new branch and a merge request.
    * This avoids headaches just in case I have uncommited/unpublished changes in my local copy somewhere.

# Project responsible

Leonard Doyle, leonard.doyle@physik.uni-muenchen.de
