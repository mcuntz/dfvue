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
   * Import pyplot for Windows, Oct 2024, Matthias Cuntz
   * Back to pack layout manager for resizing, Nov 2024, Matthias Cuntz
   * Pass Pandas DataFrame directly to dfvue, Jan 2025, Matthias Cuntz
   * Bugfix for checking if csvfile was given, Jan 2025, Matthias Cuntz
   * Use own ncvue-blue theme for customtkinter, Jan 2025, Matthias Cuntz
   * Use dfvScreen for window sizes, Nov 2025, Matthias Cuntz
   * Use set_window_geometry from dfvScreen, Nov 2025, Matthias Cuntz
   * Use Qt framework with PySide6, Aug 2026, Matthias Cuntz

"""
import os
import platform
import sys
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import QApplication
from .top import topState
from .dfvmain import dfvMain
from .dfvutils import standard_window_size


__all__ = ['dfvue']


def dfvue(df=None, csvfile='', sep='', index_col=None, skiprows=None,
          parse_dates=True, date_format=None, missing_value=None):
    """
    The main function to start the data frame GUI.

    Parameters
    ----------
    df : pandas.DataFrame, optional
        Pandas DataFrame will be used if no csvfile given
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
    # Pyinstaller sets _MEIPASS if macOS app
    bundle_dir = getattr(sys, '_MEIPASS',
                         os.path.abspath(os.path.dirname(__file__)))

    # Initialise shared state
    top = topState()

    top.os = platform.system()  # Windows, Darwin, Linux

    # parse (command line) parameters
    top.csvfile = [csvfile] if isinstance(csvfile, str) else list(csvfile)
    top.newcsvfile = True  # new file after command line
    if top.csvfile[0]:
        top.newcsvfile = False

    top.df = df
    top.sep = sep
    top.index_col = index_col
    top.skiprows = skiprows
    top.parse_dates = parse_dates
    top.date_format = date_format
    top.missing_value = missing_value

    # variable list
    if df is not None:
        top.newcsvfile = False
        rows = top.df.shape[0]
        top.cols = [ f'{cc} ({rows} {top.df[cc].dtype.name})'
                     for cc in top.df.columns ]
    else:
        top.cols = []

    # Run dfvue
    app = QApplication()
    QCoreApplication.setApplicationName("dfvue")

    # taskbar icon only if "standalone",
    # i.e. not ipython or jupyter
    try:
        whichpy = get_ipython().__class__.__name__
    except NameError:
        whichpy = ''
    if not whichpy:
        top.icon = f'{bundle_dir}/images/dfvue_icon.png'
        app.setWindowIcon(QIcon(top.icon))
    else:
        top.icon = ''

    # design using system colours
    # palette = main_frame.palette()
    palette = app.palette()
    # iblue = palette.color(QPalette.ColorRole.Highlight).name()
    iblue = palette.color(QPalette.ColorRole.Accent).name()
    # iblue = palette.color(QPalette.ColorRole.Link).name()
    if top.os == 'Darwin':
        iblue = '#3974E4'
    # iblue_hoover = palette.color(QPalette.ColorRole.Accent).name()
    iblue_hoover = palette.color(QPalette.ColorRole.Highlight).name()
    # iblue_hoover = palette.color(QPalette.ColorRole.Link).name()
    # if iblue < iblue_hoover:
    #     iblue, iblue_hoover = iblue_hoover, iblue
    # igray = palette.color(QPalette.ColorRole.AlternateBase).name()
    igray = palette.color(QPalette.ColorRole.Dark).name()
    iwin = palette.color(QPalette.ColorRole.Window).name()
    iwintext = palette.color(QPalette.ColorRole.WindowText).name()
    isize = 14
    iradius = 5
    ipadx = 5
    app.setStyleSheet(
        f"""
        QCheckBox{{
            font-size: {isize}pt;
            border-radius: {iradius}px;
        }}
        QComboBox{{
            font-size: {isize-1}pt;
        }}
        QLabel{{
            font-size: {isize}pt;
        }}
        QLineEdit{{
            font-size: {isize}pt;
            background-color: {iwin};
            color: {iwintext};
            border: 1px solid {igray};
            border-radius: {iradius}px;
        }}
        QPushButton{{
            background: {iblue};
            border-color: {igray};
            color: white;
            font-size: {isize}pt;
            border-radius: {iradius}px;
            padding: {ipadx}px;
            height: 18px;
            width: 130px;
        }}
        QPushButton:hover{{
            background-color: {iblue_hoover};
        }}
        QTabWidget, QTabBar::tab{{
            background-color: {iblue};
            color: white;
            font-size: {isize}pt;
            border-radius: {iradius}px;
            padding: {ipadx}px;
            height: 18px;
            width: 130px;
        }}
        QTabBar::tab:selected{{
            background-color: {iblue};
            color: white;
        }}
        # QTabBar::tab:hover{{
        #     background-color: {iblue_hoover};
        #     color: white;
        # }}
        QToolTip{{
            font-size: {isize-1}pt;
            border-radius: {iradius}px;
        }}
        """)

    # 1st plotting window
    mf = dfvMain(top)
    
    # # design using css
    # with open(f'{bundle_dir}/css/dfvue.css', 'r') as fi:
    #     mf.setStyleSheet(fi.read())

    # window size
    screen = mf.screen().availableGeometry()
    top.screen = (screen.width(), screen.height())
    xs, ys, xo, yo = standard_window_size(top.screen)
    mf.resize(xs, ys)
    mf.move(xo, yo)

    mf.show()

    sys.exit(app.exec())
