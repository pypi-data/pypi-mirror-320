#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse

from pyvgrid import make_HybridPressureVGrid, generate_vertical_grid
from pyvgrid import default_to_clean, default_yaxis, default_xaxis


def main():
    args = get_args()
    mkvgrid(
        args.namelist,
        plot_grid=not args.noplot,
        xaxis=args.xaxis,
        yaxis=args.yaxis,
        outputfilename=args.output,
        to_clean=args.to_clean,
        fig_kwargs=args.fig_kwargs)


def mkvgrid(
    namelist_files,
    plot_grid=True,
    show_figure=True,
    yaxis=default_yaxis,
    xaxis=default_xaxis,
    outputfilename=None,
    to_clean=default_to_clean,
    fig_kwargs={}):
    """
    Run the generation of grid, read grid, plot.

    :param namelist_files: namelist(s) to use to generate grid(s) (1 or 2)
    :param plot_grid: to plot the grid or not
    :param show_figure: whether to open the plot in a WebBrowser tab or not
    :param yaxis: 'level', 'p' (pressure), 'z' (height) or 'pthickness'//'zthickness'
    :param xaxis: 'level', 'p' (pressure), 'z' (height) or 'pthickness'//'zthickness'
    :param yaxis: 'p' (pressure) or 'z' (height)
    :param outputfilename: a specific html filename for output:
                           if None, name of file auto-generated
    :param to_clean: additional files to clean
    :param fig_kwargs: to be passed to bokeh's figure()
    """
    if not isinstance(namelist_files, list):
        namelist_files = [namelist_files]
    assert len(namelist_files) <= 2
    vgrids = []
    for n in namelist_files:
        infosup_file = generate_vertical_grid(n, to_clean=to_clean)
        vg = make_HybridPressureVGrid(infosup_file)
        vg.write_AB_to_namelist()
        vgrids.append(vg)
    if plot_grid:
        if outputfilename is None:
            if len(vgrids) == 1:
                outputfilename = infosup_file.replace('infosup',
                                                      '.'.join([yaxis, xaxis, 'html']))
            elif len(vgrids) == 2:
                outputfilename = os.path.join(os.path.dirname(infosup_file),
                                              vgrids[0].name + '+' + vgrids[1].name +
                                              '.'.join([yaxis, xaxis, 'html']))
        fig = vgrids[0].bokeh_plot_y_vs_x(yaxis, xaxis,
                                          plot_domains=True,
                                          fig_kwargs=fig_kwargs)
        if len(vgrids) == 2:
            fig = vgrids[1].bokeh_plot_y_vs_x(yaxis, xaxis,
                                              over=fig,
                                              hover_attachment='left',
                                              plot_domains=True,
                                              fig_kwargs=fig_kwargs)
        vgrids[0].bokeh_fig_to_html(fig, htmlname=outputfilename,
                                    show_figure=show_figure)
        return fig


def get_args():
    parser = argparse.ArgumentParser("Wrapper for generating hybrid-pressure vertical grids.")
    parser.add_argument('namelist',
                        help="Namelist(s) to be read for generating the grid(s). 1 or 2 namelists.",
                        nargs='+')
    parser.add_argument('-y',
                        dest='yaxis',
                        default=default_yaxis,
                        help="Y-axis for the plot, 'level' (=='l'), 'p' (pressure), 'z' (height) or 'pthickness'//'zthickness'.")
    parser.add_argument('-x',
                        dest='xaxis',
                        default=default_xaxis,
                        help="X-axis for the plot, 'level' (=='l'), 'p' (pressure), 'z' (height) or 'pthickness'//'zthickness'.")
    parser.add_argument('-o',
                        dest='output',
                        default=None,
                        help='specify output html filename of the plot.')
    parser.add_argument('-n',
                        dest='noplot',
                        action='store_true',
                        default=False,
                        help="NOT to show the plot.")
    parser.add_argument('--xlog',
                        dest='xlog',
                        default=False,
                        action='store_true',
                        help="set logscale to x-axis")
    parser.add_argument('--ylog',
                        dest='ylog',
                        default=False,
                        action='store_true',
                        help="set logscale to y-axis")
    parser.add_argument('--nc', '--no_clean',
                        dest='to_clean',
                        action='store_const',
                        const=[],
                        default=default_to_clean,
                        help="NOT to clean '{namelist}.latex', '{namelist}.mapping' and '{namelist}.namvv1' files.")
    args = parser.parse_args()
    if args.xaxis == 'l':
        args.xaxis = 'level'
    if args.yaxis == 'l':
        args.yaxis = 'level'
    args.fig_kwargs = {}
    if args.xlog:
        args.fig_kwargs['x_axis_type'] = "log"
    if args.ylog:
        args.fig_kwargs['y_axis_type'] = "log"
    return args
