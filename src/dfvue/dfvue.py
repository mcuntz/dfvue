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
    * Use CustomTkinter, Jun 2024, Matthias Cuntz
    * Use mix of grid and pack layout manager, Jun 2024, Matthias Cuntz
    * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz
    * Allow multiple input files, Oct 2024, Matthias Cuntz

"""
import os
import platform
import sys
import tkinter as tk
import tkinter.ttk as ttk
try:
    from customtkinter import CTk as Tk
    from customtkinter import CTkToplevel as Toplevel
    ihavectk = True
except ModuleNotFoundError:
    from tkinter import Tk
    from tkinter import Toplevel
    ihavectk = False
from .dfvmain import dfvMain


__all__ = ['dfvue']


def dfvue(csvfile='', sep='', index_col=None, skiprows=None,
          parse_dates=True, date_format=None, missing_value=None):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    csvfile : str or list of str, optional
        Name(s) of csv file (default: '').
    sep : str, optional
        Delimiter to use.
    index_col : str, optional
        Column(s) to use as index, either given as column index
        or string name.
    skiprows : str, optional
        Line numbers to skip (0-indexed, must include comma,
        e.g. "1," for skipping the second row) or
        number of lines to skip (int, without comma) at the start
        of the file.
    parse_dates : str, optional
        boolean. If True -> try parsing the index.

        list of int or names. e.g. If 1, 2, 3
        -> try parsing columns 1, 2, 3 each as a separate date column.

        list of lists. e.g. If [1, 3] -> combine columns 1 and 3 and
        parse as a single date column.

        dict, e.g. "foo" : [1, 3] -> parse columns 1, 3 as date and
        call result
    date_format : str, optional
        Will parse dates according to this format.
        For example: "%%Y-%%m-%%d %%H:%%M%%S". See
        https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    missing_value : str, optional
        Missing or undefined value set to NaN.

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

    top = Tk()
    top.withdraw()

    if not ihavectk:
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
    # ctk.set_appearance_mode("system")  # system, light, dark

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

    root = Toplevel()
    root.name = 'dfvOne'
    if isinstance(csvfile, str):
        csvfile = [csvfile]
    if csvfile:
        tit = f"dfvue {csvfile}"
    else:
        tit = "dfvue"
    root.title(tit)
    root.geometry('1000x800+110+0')

    # Connect csv file and add information to top
    top.os = ios           # operating system
    top.icon = icon        # app icon
    top.csvfile = csvfile  # file name or file handle
    top.newcsvfile = True  # new file after command line
    if csvfile:
        top.newcsvfile = False
    top.df = None          # pandas.DataFrame of csvfile
    top.sep = sep
    top.index_col = index_col
    top.skiprows = skiprows
    top.parse_dates = parse_dates
    top.date_format = date_format
    top.missing_value = missing_value
    top.cols = []          # variable list
    root.top = top

    def on_closing():
        top.quit()
        top.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 1st plotting window
    main_frame = dfvMain(root)
    main_frame.grid(sticky=tk.W + tk.E + tk.S + tk.N)

    top.mainloop()
