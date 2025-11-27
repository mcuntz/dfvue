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
   format_coord_scatter
   list_intersection
   parse_entry
   vardim2var

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

"""
import tkinter as tk
try:
    from customtkinter import CTkToplevel as Toplevel
except ModuleNotFoundError:
    from tkinter import Toplevel
from math import isfinite
import numpy as np
import matplotlib.dates as mpld
from .dfvscreen import dfvScreen
import dfvue


__all__ = ['clone_dfvmain',
           'format_coord_scatter',
           'list_intersection',
           'parse_entry',
           'vardim2var']


#
# Clone the main window
#

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
    >>> self.newwin = ctk.CTkButton(
    ...     self.rowwin, text="New Window",
    ...     command=partial(clone_dfvmain, self.master))

    """
    if widget.name != 'dfvMain':
        print('clone_dfvmain failed. Widget should be dfvMain.')
        print('widget.name is: ', widget.name)
        import sys
        sys.exit()

    root = Toplevel()
    root.name = 'dfvClone'
    root.top = widget.top
    if root.top.csvfile:
        tit = f"Secondary dfvue {root.top.csvfile}"
    else:
        tit = "Secondary dfvue"
    root.title(tit)
    sc = dfvScreen(root.top)
    sc.set_window_geometry(root, sc.secondary_window_size())

    # https://stackoverflow.com/questions/46505982/is-there-a-way-to-clone-a-tkinter-widget
    cls = widget.__class__
    clone = cls(root)
    try:
        for key in widget.configure():
            if key != 'class':
                clone.configure({key: widget.cget(key)})
    except TypeError:
        cls = dfvue.dfvMain
        clone = cls(root)
        clone.pack(fill=tk.BOTH, expand=1)

    return clone


#
# How to write the value of the data point below the pointer
#

def format_coord_scatter(x, y, ax, ax2, xdtype, ydtype, y2dtype):
    """
    Formatter function for scatter plot with left and right axis
    having the same x-axis.

    Parameters
    ----------
    x, y : float
        Data coordinates of `ax2`.
    ax, ax2: matplotlib.axes._subplots.AxesSubplot
        Matplotlib axes object for left-hand and right-hand y-axis, resp.
    xdtype, ydtype, y2dtype: numpy.dtype
        Numpy dtype of data of x-values (xdtype), left-hand side y-values
        (ydtype), and right-hand side y-values (y2dtype)

    Returns
    -------
    String with left-hand side and right hand-side coordinates.

    Examples
    --------
    >>> ax = plt.subplot(111)
    >>> ax2 = ax.twinx()
    >>> ax.plot(xx, yy)
    >>> ax2.plot(xx, yy2)
    >>> ax2.format_coord = lambda x, y: format_coord_scatter(
    ...     x, y, ax, ax2, xx.dtype, yy.dtype, yy2.dtype)

    """
    # convert to display coords
    # https://stackoverflow.com/questions/21583965/matplotlib-cursor-value-with-two-axes
    display_coord = ax2.transData.transform((x, y))
    # convert back to data coords with respect to ax
    inv      = ax.transData.inverted()
    ax_coord = inv.transform(display_coord)

    # Special treatment for datetime
    # https://stackoverflow.com/questions/49267011/matplotlib-datetime-from-event-coordinates
    if xdtype.type == np.dtype('datetime64').type:
        xstr = mpld.num2date(x).strftime('%Y-%m-%d %H:%M:%S')
    else:
        xstr  = '{:.6g}'.format(x)
    if ydtype.type == np.dtype('datetime64').type:
        ystr = mpld.num2date(ax_coord[1]).strftime('%Y-%m-%d %H:%M:%S')
    else:
        ystr  = '{:.6g}'.format(ax_coord[1])
    if y2dtype.type == np.dtype('datetime64').type:
        y2str = mpld.num2date(y).strftime('%Y-%m-%d %H:%M:%S')
    else:
        y2str = '{:.6g}'.format(y)
    out = f'Left: ({xstr}, {ystr}) Right: ({xstr}, {y2str})'
    return out


#
# Intersection of two lists
#

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
