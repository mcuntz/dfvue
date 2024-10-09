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
   vardim2var

History
    * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)
    * Use dfvMain directly for cloning window, Jun 2014, Matthias Cuntz
    * Use CustomTkinter, Jun 2024, Matthias Cuntz
    * Use mix of grid and pack layout manager, Jun 2024, Matthias Cuntz
    * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz
    * Allow list in window title in clone_dfvmain, Oct 2024, Matthias Cuntz

"""
import tkinter as tk
try:
    from customtkinter import CTkToplevel as Toplevel
except ModuleNotFoundError:
    from tkinter import Toplevel
import numpy as np
import matplotlib.dates as mpld
import dfvue


__all__ = ['clone_dfvmain',
           'format_coord_scatter',
           'list_intersection',
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
    root.geometry('1000x800+150+100')

    cls = dfvue.dfvMain
    clone = cls(root)
    clone.grid(sticky=tk.W + tk.E + tk.S + tk.N)


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
    if xdtype == np.dtype('<M8[ms]'):
        xstr = mpld.num2date(x).strftime('%Y-%m-%d %H:%M:%S')
    else:
        xstr  = '{:.3g}'.format(x)
    if ydtype == np.dtype('<M8[ms]'):
        ystr = mpld.num2date(ax_coord[1]).strftime('%Y-%m-%d %H:%M:%S')
    else:
        ystr  = '{:.3g}'.format(ax_coord[1])
    if y2dtype == np.dtype('<M8[ms]'):
        y2str = mpld.num2date(y).strftime('%Y-%m-%d %H:%M:%S')
    else:
        y2str = '{:.3g}'.format(y)
    out  = 'Left: (' + xstr + ', ' + ystr + ')'
    out += ' Right: (' + xstr + ', ' + y2str + ')'
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
