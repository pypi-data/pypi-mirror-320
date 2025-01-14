#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package **pyvgrid**:

Contains Python handling of Hybrid-Pressure vertical grid generation and plotting.
"""

import os
import subprocess

__version__ = "1.0.1"

lpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
bpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin')
default_to_clean = ['{}.latex', '{}.mapping', '{}.namvv1']
default_yaxis = 'z'
default_xaxis = 'pthickness'


def generate_vertical_grid(namelist_file, to_clean=default_to_clean):
    """
    Run the (Fortran) ``mkvgrid.x`` binary used to generate a vertical grid
    according to a **namelist_file**,
    and get back the name of the so-called *infosup* file
    to read data to plot from.
    """
    mkvgrid_binary_basename = 'mkvgrid.x'
    mkvgrid_binary = os.path.join(bpath, mkvgrid_binary_basename)
    subprocess.check_call([mkvgrid_binary, namelist_file])
    infosup_file = '{}.infosup'.format(namelist_file)
    for f in to_clean:
        if os.path.exists(f.format(namelist_file)):
            os.remove(f.format(namelist_file))
    return infosup_file


def make_HybridPressureVGrid(
    source, 
    vertical_mean=None,
    reference_pressure=101325.,
    ptop=0.,
    vgrid_name=None
    ):
    """
    Build the grid object from a **source**, which may be

        - a namelist file, used to generate an "infosup" file with ``mkvgrid.x``, from which to build the grid
        - an "infosup" file from ``mkvgrid.x``
        - an epygram Hybrid-Pressure VGeometry; in which case the below
          additional arguments must/may be provided:

    Case of an epygram Hybrid-Pressure VGeometry **source**:

    :param vertical_mean: mandatory, among ('geometric', 'arithmetic', 'LAPRXPK=False')
    :param reference_pressure: at the surface, for building a standard atmosphere
    :param ptop: pressure at the top of the model (upper boundary of the upper layer)
    :param vgrid_name: name of the grid, for plot/saving purpose
    """
    from .hybridpressurevgrid import HybridPressureVGrid
    vgrid = HybridPressureVGrid()
    if isinstance(source, str):
        if source.endswith('.nam'):
            infosup = generate_vertical_grid(source)
            vgrid.init_from_infosup(infosup)
        if source.endswith('.infosup'):
            vgrid.init_from_infosup(source)
        vgrid.name = os.path.basename(source).replace('.infosup', '').replace('.nam', '')
    else:
        from epygram.geometries.VGeometry import VGeometry
        if isinstance(source, VGeometry):
            assert vertical_mean is not None, \
                "must provide a **vertical_mean** among ('geometric', 'arithmetic', 'LAPRXPK=False')"
            vgrid.init_from_epygram(source,
                                    vertical_mean=vertical_mean,
                                    reference_pressure=reference_pressure,
                                    ptop=ptop,
                                    vgrid_name=vgrid_name)
        else:
            raise NotImplementedError('construction from else that source:' + str(type(source)))
    return vgrid

