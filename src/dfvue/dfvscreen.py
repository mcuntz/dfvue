#!/usr/bin/env python
"""
dfvscreen class for screen size and resolution

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2025- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   dfvScreen

History
   * Written Nov 2025 by Matthias Cuntz (mc (at) macu (dot) de)

"""
import platform
try:
    import customtkinter
    ihavectk = True
except ModuleNotFoundError:
    ihavectk = False


__all__ = ['dfvScreen']


class dfvScreen(object):
    """
    Set window sizes and resolution

    """

    def __init__(self, top, **kwargs):

        self.ihavectk = ihavectk
        self.os = platform.system()  # Windows, Darwin, Linux

        self.width = top.winfo_screenwidth()
        self.height = top.winfo_screenheight()
        self.dpi = top.winfo_fpixels('1i')

        # result of top.winfo_fpixels('1i') on development screen
        self.dpi_default = 72.

        xsize, ysize, xoffset, yoffset = self.standard_window_size()
        self.stdwin = f'{xsize}x{ysize}+{xoffset}+{yoffset}'

        xsize2, ysize2, xoffset2, yoffset2 = self.secondary_window_size()
        self.secondwin = f'{xsize2}x{ysize2}+{xoffset2}+{yoffset2}'

        xsizet, ysizet, xoffsett, yoffsett = self.transform_window_size()
        self.transformwin = f'{xsizet}x{ysizet}+{xoffsett}+{yoffsett}'

        xsizer, ysizer, xoffsetr, yoffsetr = self.readcsv_window_size()
        self.readcsvwin = f'{xsizer}x{ysizer}+{xoffsetr}+{yoffsetr}'

    #
    # DPI scaling
    #
    def scale(self, x):
        '''
        Scales *x* by current dpi over dpi of development screen

        '''
        return x * self.dpi / self.dpi_default

    #
    # Window sizes
    #
    def standard_window_size(self):
        '''
        Set xsize, ysize, xoffset, yoffset of standard window

        '''
        if self.width < 1000:
            xsize = self.width
            xoffset = 0
        else:
            xsize = max(2 * self.width // 5, 1000)
            xoffset = self.width // 5
            if ((xsize + xoffset) > self.width) or (xsize == 1000):
                xoffset = (self.width - xsize) // 2

        if self.height < 800:
            ysize = self.height
        else:
            ysize = max(4 * self.height // 5, 800)
        yoffset = 0

        return xsize, ysize, xoffset, yoffset

    def secondary_window_size(self):
        '''
        Set xsize, ysize, xoffset, yoffset of secondary window

        '''
        xsize, ysize, xoffset, yoffset = self.standard_window_size()
        
        xoffset += 50
        if (xsize + xoffset) > self.width:
            xoffset = self.width - xsize

        return xsize, ysize, xoffset, yoffset

    def transform_window_size(self):
        '''
        Set xsize, ysize, xoffset, yoffset of transform window

        '''
        xsize, ysize, xoffset, yoffset = self.standard_window_size()

        xsize = 700
        ysize = 340

        xoffset = max(xoffset - 50, 0)

        return xsize, ysize, xoffset, yoffset

    def readcsv_window_size(self):
        '''
        Set xsize, ysize, xoffset, yoffset of read csv file window

        '''
        xsize, ysize, xoffset, yoffset = self.standard_window_size()

        if self.ihavectk:
            ysize = 550
        else:
            if self.os == 'Linux':
                ysize = 620
            else:
                ysize = 550

        xoffset = max(xoffset - 100, 0)

        return xsize, ysize, xoffset, yoffset
