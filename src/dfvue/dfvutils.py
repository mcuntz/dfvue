#!/usr/bin/env python
"""
Utility functions for dfvue.

The utility functions do not depend on the dfvue class.
Functions depending on the class are in dfvmethods.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   clone_dfvmain
   list_intersection
   parse_entry
   size4font
   vardim2var
   standard_window_size
   secondary_window_size
   transform_window_size
   readcsv_window_size

History
   * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)
   * Use dfvMain directly for cloning window, Jun 2014, Matthias Cuntz
   * Use CustomTkinter, Jun 2024, Matthias Cuntz
   * Use mix of grid and pack layout manager, Jun 2024, Matthias Cuntz
   * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz
   * Allow list in window title in clone_dfvmain, Oct 2024, Matthias Cuntz
   * Remove [ms] from check for datetime in format_coord on axes2,
     Oct 2024, Matthias Cuntz
   * Back to pack layout manager for resizing, Nov 2024, Matthias Cuntz
   * Increased digits in format_coord_scatter, Jan 2025, Matthias Cuntz
   * Add parse_entry from dfvreadcsv, Jan 2025, Matthias Cuntz
   * Use dfvScreen for window sizes, Nov 2025, Matthias Cuntz
   * Deduce datetime in parse_entry, Nov 2025, Matthias Cuntz
   * Use set_window_geometry from dfvScreen, Nov 2025, Matthias Cuntz
   * Snap coordinates to nearest data points in format_coord_scatter,
     Feb 2026, Matthias Cuntz
   * Added size4font, Sep 2026, Matthias Cuntz
   * Moved and changed standard_window_size, secondary_window_size,
     transform_window_size, and readcsv_window_size for Qt framework
     with PySide6, Sep 2026, Matthias Cuntz
   * Changed clone_dfvmain for for Qt framework with PySide6,
     Sep 2026, Matthias Cuntz
   * Removed format_coord_scatter, Sep 2026, Matthias Cuntz

"""
from math import isfinite
import numpy as np
import matplotlib.dates as mpld


__all__ = ['clone_dfvmain',
           'list_intersection',
           'parse_entry',
           'size4font',
           'vardim2var',
           'standard_window_size',
           'secondary_window_size',
           'transform_window_size',
           'readcsv_window_size']


def clone_dfvmain(widget):
    """
    Duplicate the main dfvue window.

    Parameters
    ----------
    widget : dfvue.dfvMain
        widget of dfvMain class.

    Returns
    -------
    Another dfvue window will be created.

    Examples
    --------
    >>> 

    """
    cls = widget.__class__
    clone = cls(widget.top)
    clone.name = 'dfvClone'

    if len(clone.top.screen) == 0:
        screen = clone.screen().availableGeometry()
        clone.top.screen = (screen.width(), screen.height())
    xs, ys, xo, yo = secondary_window_size(clone.top.screen)
    clone.resize(xs, ys)
    clone.move(xo, yo)
    
    clone.show()

    return


def list_intersection(lst1, lst2):
    """
    Intersection of two lists.

    From:
    https://stackoverflow.com/questions/3697432/how-to-find-list-intersection
    Using list comprehension for small lists and set() method with builtin
    intersection for longer lists.

    Parameters
    ----------
    lst1, lst2 : list
        Python lists

    Returns
    -------
    list
        List with common elements in both input lists.

    Examples
    --------
    >>> lst1 = [ 4, 9, 1, 17, 11, 26, 28, 28, 26, 66, 91]
    >>> lst2 = [9, 9, 74, 21, 45, 11, 63]
    >>> print(Intersection(lst1, lst2))
    [9, 11]

    """
    if (len(lst1) > 10) or (len(lst2) > 10):
        return list(set(lst1).intersection(lst2))
    else:
        return [ ll for ll in lst1 if ll in lst2 ]


def parse_entry(text):
    """
    Convert text string to correct data type

    Parse an entry field to None, bool, int, float, datetime, list, dict

    Parameters
    ----------
    text : str
        String from entry field

    Returns
    -------
    None, bool, int, float, datetime, list, dict

    Examples
    --------
    >>> parse_entry('7')
    7
    >>> parse_entry('7,3')
    [7, 3]

    """
    if ',' in text:
        # # list or str
        # try:
        #     tt = eval(f'[{text}]')
        # except SyntaxError:
        #     tt = text
        # parse each element
        stext = text.split(',')
        tt = [ parse_entry(ss) for ss in stext ]
    elif text == 'None':
        # None
        tt = None
    elif text == 'True':
        # bool True
        tt = True
    elif text == 'False':
        # bool False
        tt = False
    elif ':' in text:
        # dict, datetime, or str
        try:
            tt = eval(f'{{{text}}}')
        except SyntaxError:
            try:
                tt = np.datetime64(text)
            except ValueError:
                tt = text
    elif text.count('-') == 2:
        # datetime or str
        try:
            tt = np.datetime64(text)
        except ValueError:
            tt = text
    else:
        tt = text

    # if above gave str, check for scalars
    if tt == text:
        try:
            # int
            tt = int(text)
        except ValueError:
            try:
                # float
                tt = float(text)
            except ValueError:
                # str
                tt = text
            try:
                if not isfinite(tt):
                    # keep NaN and Inf string
                    tt = text
            except TypeError:
                pass
    return tt


def size4font(widget, text=None):
    """
    Extract variable name from 'variable (dim1=ndim1,)' string.

    Parameters
    ----------
    widget : QWidget
        Any PSyde6 widget
    text : string, optional
        Return size needed for text in widget

    Returns
    -------
    int
        Size to bi used in widget.setFixedWidth(size)

    Examples
    --------
    >>> 

    """
    fm = widget.fontMetrics()
    if text is None:
        text = widget.text()
    if text:
        iwidth = fm.size(0, text)
    else:
        iwidth = fm.size(0, '')
    return iwidth.width() + 2 * 5  # +padding


def vardim2var(vardim):
    """
    Extract variable name from 'variable (dim1=ndim1,)' string.

    Parameters
    ----------
    vardim : string
        Variable name with dimensions, such as 'latitude (lat=32,lon=64)'.

    Returns
    -------
    string
        Variable name.

    Examples
    --------
    >>> vardim2var('latitude (lat=32,lon=64)')
    latitude

    """
    return vardim[0:vardim.rfind('(')].rstrip()

#
# Window sizes
#

def standard_window_size(screen):
    '''
    Set xsize, ysize, xoffset, yoffset of standard window

    Parameters
    ----------
    screen : tuple
        (width, height) of useable space on screen

    Returns
    -------
    tuple
        xsize, ysize, xoffset, yoffset

    '''
    if screen[1] < 800:
        ysize = screen[1]
    else:
        ysize = max(4 * screen[1] // 5, 800)
    yoffset = 0

    if screen[0] < 1000:
        xsize = screen[0]
        xoffset = 0
    else:
        xsize = max(2 * screen[0] // 5, 1000)
        xoffset = screen[0] // 5
        if ((xsize + xoffset) > screen[0]) or (xsize == 1000):
            xoffset = (screen[0] - xsize) // 2

    # ysize = 1200
    # xsize = int(1.5 * ysize)
    return xsize, ysize, xoffset, yoffset


def secondary_window_size(screen):
    '''
    Set xsize, ysize, xoffset, yoffset of secondary window

    Parameters
    ----------
    screen : tuple
        (width, height) of useable space on screen

    Returns
    -------
    tuple
        xsize, ysize, xoffset, yoffset

    '''
    xsize, ysize, xoffset, yoffset = standard_window_size(screen)
    
    xoffset += 50
    if (xsize + xoffset) > screen[0]:
        xoffset = screen[0] - xsize

    return xsize, ysize, xoffset, yoffset


def transform_window_size(screen):
    '''
    Set xsize, ysize, xoffset, yoffset of transform window

    Parameters
    ----------
    screen : tuple
        (width, height) of useable space on screen

    Returns
    -------
    tuple
        xsize, ysize, xoffset, yoffset

    '''
    xsize, ysize, xoffset, yoffset = standard_window_size(screen)

    xsize = 700
    ysize = 340

    xoffset = max(xoffset - 50, 0)

    return xsize, ysize, xoffset, yoffset


def readcsv_window_size(screen):
    '''
    Set xsize, ysize, xoffset, yoffset of read csv file window

    Parameters
    ----------
    screen : tuple
        (width, height) of useable space on screen

    Returns
    -------
    tuple
        xsize, ysize, xoffset, yoffset

    '''
    xsize, ysize, xoffset, yoffset = standard_window_size(screen)

    ysize = 550

    xoffset = max(xoffset - 100, 0)

    return xsize, ysize, xoffset, yoffset
