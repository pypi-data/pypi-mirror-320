VGRID
=====

*Vertical Hybrid-pressure grid generation*

Components of the lib
---------------------

This is composed of:

* A Fortran program (`src/mkvgrid/main.F90`) for generating hybrid-pressure grid.
* A Fortran library (`src/stdatm/`) containing routines for standard atmosphere computations of
  altitude and pressure on grid levels.
* A Python interface package `pyvgrid` (`src/pyvgrid/`) to the Fortran program and library,
  including also utilities to plot grids using `bokeh`.
* Examples of namelists (`nam/`) used to generate grids, including canonical ones.

Install
-------

Using pip:

* `pip install pyvgrid`

To recompile:

* `git clone https://github.com/ACCORD-NWP/vgrid.git`
* `cd vgrid`
* for the python interface (incl. compilation):
  1. `python -m build`
  2. `pip install dist/pyvgrid*.whl`
* for the Fortran only:
  0. `BUILD_DIR=<where you want to build>; INSTALL_DIR=<where you want to install>`
  1. `cmake -B $BUILD_DIR -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR`
  2. `cmake --build $BUILD_DIR`
  3. `cmake --install $BUILD_DIR`

Examples of use
---------------

1. Generation of a new grid from namelist and command-line:
   * Prepare a namelist containing the parameters to tune, cf. examples in `nam/`
   * `mkvgrid <my_nam> [optionally_a_second_one_for_comparison]`
     this will compute the grid, generate namelist blocks for NAMVV1 and NAMFPG, and open a html figure in your default browser
   * Option `-h` to see other options of the command, especially to choose abscissa/ordinate among altitude, pressure, level number, level thickness (m or Pa).

2. Plot a grid from a FA file, and emulate its re-creation through `mkvgrid`:
   cf. `doc/test_vgrid_from_epygram.py`

Documentation
-------------

* Scientific documentation by P.Benard (2008) is available on: http://www.umr-cnrm.fr/gmapdoc/IMG/pdf/memoeta0.pdf
* Examples of namelists (in `nam/`) are auto-documented
* Python interface is auto-documented
* More to come...

