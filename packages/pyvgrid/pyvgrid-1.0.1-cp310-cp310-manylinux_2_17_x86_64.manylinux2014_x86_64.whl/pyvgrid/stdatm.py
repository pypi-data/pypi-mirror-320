#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standard atmosphere functions.

Uses 'altsta' and 'presta' subroutines from associated 'stdatm' Fortran lib,
through the 'stdatm.so' shared object library, that can be compiled using `cmake` (or python -m build).
This library is to be installed in the 'lib' directory of this project.

The Python -> Fortran interface is implemented using 'ctypesForFortran'.
"""

import os
import numpy
import ctypesForFortran

from . import lpath

__all__ = ['presta', 'altsta', 'pressure_at', 'altitude_at']

so_basename = 'libstdatm.so'
shared_objects_library = os.path.join(lpath, so_basename)

IN = ctypesForFortran.IN
OUT = ctypesForFortran.OUT
INOUT = ctypesForFortran.INOUT
ctypesFF, handle = ctypesForFortran.ctypesForFortranFactory(shared_objects_library)


@ctypesFF()
def presta(KLEV, PSTZ):
    return ([KLEV, PSTZ],
            [(numpy.int64, None, IN),
             (numpy.float64, (KLEV,), IN),
             (numpy.float64, (KLEV,), OUT)],
            None)


@ctypesFF()
def altsta(KLEV, PREHYD):
    return ([KLEV, PREHYD],
            [(numpy.int64, None, IN),
             (numpy.float64, (KLEV,), IN),
             (numpy.float64, (KLEV,), OUT)],
            None)


def pressure_at(altitude):
    """
    Compute the pressure at a series of altitude, considering standard atmosphere.

    For more documentation, cf. arpifs' ppsta.F90
    """
    return presta(len(altitude), altitude)


def altitude_at(pressure):
    """
    Compute the altitude at a series of pressure, considering standard atmosphere.

    For more documentation, cf. arpifs' susta.F90
    """
    return altsta(len(pressure), pressure)
