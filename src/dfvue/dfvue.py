#!/usr/bin/env python3
"""
Calling routine of dfvue

The calling routine sets up the toplevel root window and gets an
instance of the dfvMain class.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   dfvue

History
    * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)
      adapted ncvue.py

"""
import os
import platform
import sys
import tkinter as tk
try:
    import tkinter.ttk as ttk
except Exception:
    raise ImportError('Using the themed widget set introduced in Tk 8.5.')
import numpy as np
# import matplotlib as mpl
# mpl.use('TkAgg')
from matplotlib import pyplot as plt
from .dfvmain import dfvMain


__all__ = ['dfvue']


def dfvue(csvfile='', miss=None):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    csvfile : str, optional
        Name of csv file (default: '').
    miss : float, optional
        Set ``miss`` to NaN in pandas.DataFrame

    """
    # print(mpl.get_backend())
    ios = platform.system()  # Windows, Darwin, Linux
    if ios == 'Windows':
        # make Windows aware of high resolution displays
        # https://stackoverflow.com/questions/41315873/attempting-to-resolve-blurred-tkinter-text-scaling-on-windows-10-high-dpi-disp
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    # Pyinstaller sets _MEIPASS if macOS app
    bundle_dir = getattr(sys, '_MEIPASS',
                         os.path.abspath(os.path.dirname(__file__)))

    top = tk.Tk()
    top.withdraw()
    # top.option_add("*Font", "Helvetica 10")

    # Check light/dark mode
    # https://stackoverflow.com/questions/65294987/detect-os-dark-mode-in-python

    # style = ttk.Style()
    # print(style.theme_names(), style.theme_use())
    if ios == 'Darwin':
        theme = 'aqua'
        style = ttk.Style()
        try:
            style.theme_use(theme)
        except:
            pass
    elif ios == 'Windows':
        top.option_add("*Font", "Helvetica 10")
        plt.rc('font', size=13)
        # standard Windows themes
        # ('winnative', 'clam', 'alt', 'default', 'classic', 'vista',
        #  'xpnative')
        # theme = 'vista'
        # style = ttk.Style()
        # style.theme_use(theme)

        # 'azure' v2.x, 'sun-valley', 'forest' of rdbende
        top.tk.call('source', bundle_dir + '/themes/azure-2.0/azure.tcl')
        theme = 'light'  # light, dark
        top.tk.call("set_theme", theme)
    elif ios == 'Linux':
        # standard Linux schemes
        # theme = 'clam'  # 'clam', 'alt', 'default', 'classic'
        # style = ttk.Style()
        # style.theme_use(theme)

        # 'azure' v2.x, 'sun-valley', 'forest' of rdbende
        top.tk.call('source', bundle_dir + '/themes/azure-2.0/azure.tcl')
        theme = 'light'  # light, dark
        top.tk.call("set_theme", theme)

    # set titlebar and taskbar icon only if "standalone",
    # i.e. not ipython or jupyter
    try:
        whichpy = get_ipython().__class__.__name__
    except NameError:
        whichpy = ''
    if not whichpy:
        icon = tk.PhotoImage(file=bundle_dir + '/images/dfvue_icon.png')
        top.iconphoto(True, icon)  # True: apply to all future toplevels
    else:
        icon = None

    root = tk.Toplevel()
    root.name = 'dfvOne'
    root.title("dfvue " + csvfile)
    root.geometry('1000x800+110+0')

    # Connect csv file and add information to top
    top.os = ios           # operating system
    top.theme = theme      # current theme
    top.icon = icon        # app icon
    top.csvfile = csvfile  # file name or file handle
    top.df = None          # pandas.DataFrame of csvfile
    top.miss = miss        # extra missing value
    top.cols = []          # variable list
    root.top = top

    def on_closing():
        top.quit()
        top.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 1st plotting window
    main_frame = dfvMain(root)

    top.mainloop()
