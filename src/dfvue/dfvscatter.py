#!/usr/bin/env python
"""
Scatter/Line panel of dfvue.

The panel allows plotting variables against time or two variables against
each other. A second variable can be plotted in the same graph using the
right-hand-side y-axis.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   dfvScatter

History
   * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)
   * Use CustomTkinter, Jun 2024, Matthias Cuntz
   * Use mix of grid and pack layout manager, Jun 2024, Matthias Cuntz
   * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz
   * Allow multiple input files, Oct 2024, Matthias Cuntz
   * Back to pack layout manager for resizing, Nov 2024, Matthias Cuntz
   * Bugfix for checking if csvfile was given, Jan 2025, Matthias Cuntz
   * Removed addition of index to column names in sortvars,
     Jan 2025, Matthias Cuntz
   * Add xlim, ylim, and y2lim options, Jan 2025, Matthias Cuntz
   * Use add_button, add_label, add_combobox from ncvwidgets,
     Jun 2025, Matthias Cuntz
   * Bugfix for setting axes limits, Jun 2025, Matthias Cuntz
   * Tooltip for xlim and ylim includes datetime, Nov 2025, Matthias Cuntz
   * Draw canvas as last element so that UI controls are displayed
     as long as possible, Dec 2025, Matthias Cuntz
   * Snap coordinates to nearest data points, Feb 2026, Matthias Cuntz
   * Respect command line options when reading first 40 lines,
     Aug 2026, Solim Rovera and Matthias Cuntz
   * Correct parsing of missing_value command line option,
     Aug 2026, Matthias Cuntz
   * Catch ParseError of pandas.read_csv, Aug 2026, Matthias Cuntz
   * Use Qt framework with PySide6, Aug 2026, Matthias Cuntz
   * Add reinit button, Sep 2026, Matthias Cuntz
   * Remove snap coord, Sep 2026, Matthias Cuntz

"""
# from functools import partial
from functools import partial
import sys
import warnings
import matplotlib as mpl
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from PySide6.QtCore import QCoreApplication, QSize, Qt
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget
from .dfvreadcsv import dfvReadcsv
from .dfvtransform import dfvTransform
from .dfvutils import clone_dfvmain, parse_entry, size4font, vardim2var
from .vuewidgets import mplCanvas, add_checkbox, add_combobox, add_lineedit
from .vuewidgets import add_label, add_pushbutton
try:
    plt.style.use('seaborn-v0_8-dark')
except OSError:
    plt.style.use('seaborn-dark')


__all__ = ['dfvScatter']


def _minmax_ylim(ylim, ylim2):
    """
    Get minimum of first elements of lists `ylim` and `ylim2` and
    maximum of second element of the two lists.

    Returns minimum, maximum.

    """
    if (ylim[0] is not None) and (ylim2[0] is not None):
        ymin = min(ylim[0], ylim2[0])
    else:
        if (ylim[0] is not None):
            ymin = ylim[0]
        else:
            ymin = ylim2[0]
    if (ylim[1] is not None) and (ylim2[1] is not None):
        ymax = max(ylim[1], ylim2[1])
    else:
        if (ylim[1] is not None):
            ymax = ylim[1]
        else:
            ymax = ylim2[1]
    return ymin, ymax


class dfvScatter(QWidget):
    """
    Panel for scatter and line plots.

    Sets up the layout with the figure canvas, variable selectors, dimension
    spinboxes, and options.

    Contains various commands that manage what will be drawn or redrawn if
    something is selected, changed, checked, etc.

    Contains three drawing routines. `redraw_y` and `redraw_y2` redraw the
    y-axes without changing zoom level, etc. `redraw` is called if a new
    x-variable was selected or the `Redraw`-button was pressed. It resets
    all axes, resetting zoom, etc.

    """

    #
    # Setup panel
    #

    def __init__(self, master, **kwargs):

        super().__init__(**kwargs)

        self.master = master
        self.top = master.top
        
        # selections and options
        columns = [''] + self.top.cols
        # colors
        pcycle = [ cc for cc in plt.rcParams['axes.prop_cycle'] ]
        c = [ mpl.colors.to_hex(cc['color']) for cc in pcycle ]
        self.col1 = c[0]  # blue
        self.col2 = c[3]  # red
        # color tooltip
        ctstr = ("- color names: red, green, blue, yellow, ...\n"
                 "- single characters: b (blue), g (green), r (red), c (cyan),"
                 " m (magenta), y (yellow), k (black), w (white)\n"
                 "- hex RGB: #rrggbb such such as #ff9300 (orange)\n"
                 "- gray level: float between 0 and 1\n"
                 "- RGA (red, green, blue) or RGBA (red, green, blue, alpha)"
                 " tuples between 0 and 1, e.g. (1, 0.57, 0) for orange\n"
                 "- name from xkcd color survey, e.g. xkcd:sky blue")
        # marker tooltip
        mtstr = (". (point), ',' (pixel), o (circle),\n"
                 "v (triangle_down), ^ (triangle_up),\n"
                 "< (triangle_left), > (triangle_right),\n"
                 "1 (tri_down), 2 (tri_up), 3 (tri_left), 4 (tri_right),"
                 " 8 (octagon),\n"
                 "s (square), p (pentagon), P (plus (filled)),\n"
                 "* (star), h (hexagon1), H (hexagon2),\n"
                 "+ (plus), x (x), X (x (filled)),\n"
                 "D (diamond), d (thin_diamond),\n"
                 "| (vline), _ (hline), or None")
        # xlim, ylim tooltip
        ltstr = ("min, max\n"
                 "Set to None for free scaling.\n"
                 "Datetime must be in iso8601 format, e.g. 2025-11-23")

        shortline = 'X'
        medline = 'XXXX'
        longline = 'XXXXXXX'
        xlongline = 'XXXX-XX-XX,XXXX-XX-XX'
        if self.top.os == 'Linux':
            shortline += 'X'
            medline += 'X'
            longline += 'XX'
            xlongline += 'XXXXX'
        self.minboxwidth = 'XXXXXXXXXXXXXXX'
        self.maxboxwidth = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # open file and new window
        self.rowwin = QHBoxLayout()
        self.rowwin.setContentsMargins(5, 0, 5, 0)
        self.rowwin.setSpacing(3)

        self.newfile = add_pushbutton(
            self.rowwin, text='Open File', command=self.new_csv,
            tooltip='Open a new csv file',
            alignment=Qt.AlignmentFlag.AlignLeft)

        self.newwin = add_pushbutton(
            self.rowwin, text='New Window',
            command=partial(clone_dfvmain, self.master),
            tooltip='Open secondary dfvue window',
            alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(self.rowwin)

        # plotting canvas
        self.rowcanvas = QVBoxLayout()
        self.rowcanvas.setContentsMargins(5, 0, 5, 10)
        self.rowcanvas.setSpacing(3)

        height = 7
        self.canvas = mplCanvas(width=1.618 * height, height=height)

        self.rowcanvas.addWidget(self.canvas)

        # matplotlib toolbar
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setIconSize(QSize(20, 20))  # default: 24

        self.rowcanvas.addWidget(self.toolbar)

        layout.addLayout(self.rowcanvas)

        # 1. row: x-axis and left y-axis
        self.rowxy = QHBoxLayout()
        self.rowxy.setContentsMargins(5, 0, 5, 0)
        self.rowxy.setSpacing(3)

        self.xlab = add_label(self.rowxy, text='x')
        self.bprev_x = add_pushbutton(
            self.rowxy, text='<', command=self.prev_x,
            tooltip='Previous variable')
        self.bprev_x.setFixedWidth(size4font(self.bprev_x))
        self.bnext_x = add_pushbutton(
            self.rowxy, text='>', command=self.next_x,
            tooltip='Next variable')
        self.bnext_x.setFixedWidth(size4font(self.bnext_x))
        self.xlbl, self.x = add_combobox(
            self.rowxy, label='', values=columns,
            command=self.selected_x,
            tooltip=('Choose variable of x-axis.\n'
                     'Take index if "None" (fast).'))
        self.x.setMinimumWidth(size4font(self.x, self.minboxwidth))
        self.x.setMaximumWidth(size4font(self.x, self.maxboxwidth))

        self.inv_x = add_checkbox(self.rowxy, label='invert x',
                                  value=False, command=self.checked_x,
                                  tooltip='Invert x-axis')

        space = add_label(self.rowxy, text=' ' * 3)
        self.ylab = add_label(self.rowxy, text='y')
        self.bprev_y = add_pushbutton(
            self.rowxy, text='<', command=self.prev_y,
            tooltip='Previous variable')
        self.bprev_y.setFixedWidth(size4font(self.bprev_y))
        self.bnext_y = add_pushbutton(
            self.rowxy, text='>', command=self.next_y,
            tooltip='Next variable')
        self.bnext_y.setFixedWidth(size4font(self.bnext_y))

        self.ylbl, self.y = add_combobox(
            self.rowxy, label='', values=columns,
            command=self.selected_y,
            tooltip='Choose variable of y-axis.')
        self.y.setMinimumWidth(size4font(self.y, self.minboxwidth))
        self.y.setMaximumWidth(size4font(self.y, self.maxboxwidth))

        self.inv_y = add_checkbox(self.rowxy, label='invert y',
                                  value=False, command=self.checked_y,
                                  tooltip='Invert y-axis')

        space = add_label(self.rowxy, text=' ' * 1)
        self.rowxy.addStretch()

        self.bredraw = add_pushbutton(
            self.rowxy, text='Reinit', command=self.reinit,
            alignment=Qt.AlignmentFlag.AlignRight,
            tooltip='Reinit dfvue from start')
        
        layout.addLayout(self.rowxy)

        # 2. row: options for lhs y-axis
        self.rowxyopt = QHBoxLayout()
        self.rowxyopt.setContentsMargins(5, 0, 5, 0)
        self.rowxyopt.setSpacing(3)

        self.lslbl, self.ls = add_lineedit(
            self.rowxyopt, label='ls', text='-',
            command=self.entered_y,
            tooltip='Line style: -, --, -., :, or None')
        self.ls.setFixedWidth(size4font(self.ls, medline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.lwlbl, self.lw = add_lineedit(
            self.rowxyopt, label='lw', text='1',
            command=self.entered_y, tooltip='Line width')
        self.lw.setFixedWidth(size4font(self.lw, shortline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.lclbl, self.lc = add_lineedit(
            self.rowxyopt, label='c', text=self.col1,
            command=self.entered_y,
            tooltip='Line color:\n' + ctstr)
        self.lc.setFixedWidth(size4font(self.lc, longline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.markerlbl, self.marker = add_lineedit(
            self.rowxyopt, label='marker', text='None',
            command=self.entered_y,
            tooltip='Marker symbol:\n' + mtstr)
        self.marker.setFixedWidth(size4font(self.marker, medline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.mslbl, self.ms = add_lineedit(
            self.rowxyopt, label='ms', text='1',
            command=self.entered_y, tooltip='Marker size')
        self.ms.setFixedWidth(size4font(self.ms, shortline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.mfclbl, self.mfc = add_lineedit(
            self.rowxyopt, label='mfc', text=self.col1,
            command=self.entered_y,
            tooltip='Marker fill color:\n' + ctstr)
        self.mfc.setFixedWidth(size4font(self.mfc, longline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.meclbl, self.mec = add_lineedit(
            self.rowxyopt, label='mec', text=self.col1,
            command=self.entered_y,
            tooltip='Marker edge color:\n' + ctstr)
        self.mec.setFixedWidth(size4font(self.mec, longline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.mewlbl, self.mew = add_lineedit(
            self.rowxyopt, label='mew', text='1',
            command=self.entered_y, tooltip='Marker edge width')
        self.mew.setFixedWidth(size4font(self.mew, shortline))

        space = add_label(self.rowxyopt, text=' ' * 1)
        self.rowxyopt.addStretch()

        self.bredraw = add_pushbutton(
            self.rowxyopt, text='Redraw', command=self.redraw,
            alignment=Qt.AlignmentFlag.AlignRight,
            tooltip='Redraw, resetting zoom')

        layout.addLayout(self.rowxyopt)

        # 3. row: xlim, ylim
        self.rowtransform = QHBoxLayout()
        self.rowtransform.setContentsMargins(5, 0, 5, 0)
        self.rowtransform.setSpacing(3)

        self.xlimlbl, self.xlim = add_lineedit(
            self.rowtransform, label='xlim', text='None',
            command=self.entered_y, tooltip=ltstr)
        self.xlim.setFixedWidth(size4font(self.xlim, xlongline))

        space = add_label(self.rowtransform, text=' ' * 1)
        self.ylimlbl, self.ylim = add_lineedit(
            self.rowtransform, label='ylim', text='None',
            command=self.entered_y, tooltip=ltstr)
        self.ylim.setFixedWidth(size4font(self.ylim, xlongline))

        space = add_label(self.rowtransform, text=' ' * 1)
        self.rowtransform.addStretch()

        self.bsort = add_pushbutton(
            self.rowtransform, text='Sort vars', command=self.sortvars,
            alignment=Qt.AlignmentFlag.AlignRight,
            tooltip='Sort variable names')

        layout.addLayout(self.rowtransform)
        
        # 4. row: empty row
        self.rowspace = QHBoxLayout()
        self.rowspace.setContentsMargins(5, 0, 5, 0)
        self.rowspace.setSpacing(3)

        space = add_label(self.rowspace, text=' ' * 1)
        self.rowspace.addStretch()

        self.transform = add_pushbutton(
            self.rowspace, text='Transform', command=self.transform_df,
            alignment=Qt.AlignmentFlag.AlignRight,
            tooltip='Manipulate DataFrame')

        layout.addLayout(self.rowspace)
        
        # 5. row: right y2-axis
        self.rowyy2 = QHBoxLayout()
        self.rowyy2.setContentsMargins(5, 0, 5, 0)
        self.rowyy2.setSpacing(3)

        self.y2lab = add_label(self.rowyy2, text='y2')
        self.bprev_y2 = add_pushbutton(
            self.rowyy2, text='<', command=self.prev_y2,
            tooltip='Previous variable')
        self.bprev_y2.setFixedWidth(size4font(self.bprev_y2))
        self.bnext_y2 = add_pushbutton(
            self.rowyy2, text='>', command=self.next_y2,
            tooltip='Next variable')
        self.bnext_y2.setFixedWidth(size4font(self.bnext_y2))

        self.y2lbl, self.y2 = add_combobox(
            self.rowyy2, label='', values=columns,
            command=self.selected_y2,
            tooltip='Choose variable of right y-axis.')
        self.y2.setMinimumWidth(size4font(self.y2, self.minboxwidth))
        self.y2.setMaximumWidth(size4font(self.y2, self.maxboxwidth))

        self.inv_y2 = add_checkbox(self.rowyy2, label='invert y2',
                                  value=False, command=self.checked_y2,
                                  tooltip='Invert right y-axis')

        space = add_label(self.rowyy2, text=' ' * 1)
        tstr = 'Same limits for left-hand-side and right-hand-side y-axes'
        self.same_y = add_checkbox(self.rowyy2, label='same y-axes',
                                  value=False, command=self.checked_yy2,
                                  tooltip=tstr)

        space = add_label(self.rowyy2, text=' ' * 1)
        self.rowyy2.addStretch()

        layout.addLayout(self.rowyy2)

        # 6. row: options for rhs y-axis
        self.rowy2opt = QHBoxLayout()
        self.rowy2opt.setContentsMargins(5, 0, 5, 0)
        self.rowy2opt.setSpacing(3)

        self.ls2lbl, self.ls2 = add_lineedit(
            self.rowy2opt, label='ls', text='-',
            command=self.entered_y2,
            tooltip='Line style: -, --, -., :, or None')
        self.ls2.setFixedWidth(size4font(self.ls2, medline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.lw2lbl, self.lw2 = add_lineedit(
            self.rowy2opt, label='lw', text='1',
            command=self.entered_y2, tooltip='Line width')
        self.lw2.setFixedWidth(size4font(self.lw2, shortline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.lc2lbl, self.lc2 = add_lineedit(
            self.rowy2opt, label='c', text=self.col2,
            command=self.entered_y2,
            tooltip='Line color:\n' + ctstr)
        self.lc2.setFixedWidth(size4font(self.lc2, longline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.marker2lbl, self.marker2 = add_lineedit(
            self.rowy2opt, label='marker', text='None',
            command=self.entered_y2,
            tooltip='Marker symbol:\n' + mtstr)
        self.marker2.setFixedWidth(size4font(self.marker2, medline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.ms2lbl, self.ms2 = add_lineedit(
            self.rowy2opt, label='ms', text='1',
            command=self.entered_y2, tooltip='Marker size')
        self.ms2.setFixedWidth(size4font(self.ms2, shortline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.mfc2lbl, self.mfc2 = add_lineedit(
            self.rowy2opt, label='mfc', text=self.col2,
            command=self.entered_y2,
            tooltip='Marker fill color:\n' + ctstr)
        self.mfc2.setFixedWidth(size4font(self.mfc2, longline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.mec2lbl, self.mec2 = add_lineedit(
            self.rowy2opt, label='mec', text=self.col2,
            command=self.entered_y2,
            tooltip='Marker edge color:\n' + ctstr)
        self.mec2.setFixedWidth(size4font(self.mec2, longline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.mew2lbl, self.mew2 = add_lineedit(
            self.rowy2opt, label='mew', text='1',
            command=self.entered_y2, tooltip='Marker edge width')
        self.mew2.setFixedWidth(size4font(self.mew2, shortline))

        space = add_label(self.rowy2opt, text=' ' * 1)
        self.rowy2opt.addStretch()

        layout.addLayout(self.rowy2opt)

        # 7. row: y2lim
        self.rowquit = QHBoxLayout()
        self.rowquit.setContentsMargins(5, 0, 5, 10)
        self.rowquit.setSpacing(3)

        self.y2limlbl, self.y2lim = add_lineedit(
            self.rowquit, label='y2lim', text='None',
            command=self.entered_y2, tooltip=ltstr)
        self.y2lim.setFixedWidth(size4font(self.y2lim, xlongline))

        space = add_label(self.rowquit, text=' ' * 1)
        self.rowquit.addStretch()

        self.iquit = add_pushbutton(
            self.rowquit, text='Quit', command=self.quit_app,
            alignment=Qt.AlignmentFlag.AlignRight,
            tooltip='Quit dfvue')

        layout.addLayout(self.rowquit)

        self.setLayout(layout)

        self.show()

        if (self.top.df is None) and self.top.csvfile[0]:
            self.new_df()

    #
    # Event bindings
    #

    def checked_x(self):
        """
        Command called if any checkbutton for x-axis was checked or unchecked.

        Redraws left-hand-side and right-hand-side y-axes.

        """
        self.redraw_y()
        self.redraw_y2()

    def checked_y(self):
        """
        Command called if any checkbutton for left-hand-side y-axis was checked
        or unchecked.

        Redraws left-hand-side y-axis.

        """
        self.redraw_y()

    def checked_y2(self):
        """
        Command called if any checkbutton for right-hand-side y-axis was
        checked or unchecked.

        Redraws right-hand-side y-axis.

        """
        self.redraw_y2()

    def checked_yy2(self):
        """
        Command called if any checkbutton was checked or unchecked that
        concerns both, the left-hand-side and right-hand-side y-axes.

        Redraws left-hand-side and right-hand-side y-axes.

        """
        self.ylim.setText('None')
        self.y2lim.setText('None')
        self.redraw_y()
        self.redraw_y2()

    def entered_y(self):
        """
        Command called if option was entered for left-hand-side y-axis.

        Redraws left-hand-side y-axis.

        """
        self.redraw_y()

    def entered_y2(self):
        """
        Command called if option was entered for right-hand-side y-axis.

        Redraws right-hand-side y-axis.

        """
        self.redraw_y2()

    def new_csv(self):
        """
        Open a new csv file and connect it to top.

        """
        self.top.csvfile, _ = QFileDialog.getOpenFileNames(
            self, "Choose csv file(s)")

        if self.top.csvfile[0]:
            self.top.newcsvfile = True
            self.new_df()
            self.top.newcsvfile = False

    def new_df(self):
        """
        Read new DataFrame.

        """
        opts = {'nrows': 40}
        if not self.top.newcsvfile:
            for kk in ['sep', 'index_col', 'skiprows', 'parse_dates',
                       'date_format', 'missing_value']:
                text = getattr(self.top, kk, None)
                if (text != '') and (text is not None):
                    tt = parse_entry(text)
                    if (tt != '') and (tt is not None):
                        if kk == 'missing_value':
                            opts.update({'na_values': [tt]})
                        else:
                            opts.update({kk: tt})

        try:
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=FutureWarning)
                self.top.df = pd.read_csv(self.top.csvfile[0], **opts)
        except pd.errors.ParserError:
            with open(self.top.csvfile[0], 'r') as fi:
                fin = fi.readlines()
            self.top.df = pd.DataFrame(fin)

        # # add index as column
        # idx = 'df.index'
        # if self.top.df.index.name is not None:
        #     idx = self.top.df.index.name
        # if isinstance(self.top.df.index, pd.MultiIndex):
        #     series = [ [ str(kk) for kk in ii ]
        #                for ii in self.top.df.index ]
        #     series = [ ' '.join(ii) for ii in series ]
        # else:
        #     series = self.top.df.index
        # # self.top.df.insert(0, idx, pd.Series(series, index=self.top.df.index))
        # self.top.df = pd.concat([pd.Series(series, index=self.top.df.index),
        #                          self.top.df], axis=1)
        # if isinstance(self.top.df.index, pd.MultiIndex):
        #     # replace MultiIndex with combined column
        #     self.top.df.set_index(idx, drop=False, inplace=True)
            
        self.readcsvwin = dfvReadcsv(self)

        self.resetvars(nosort=True)
        self.x.setMinimumWidth(size4font(self.x, self.minboxwidth))
        self.x.setMaximumWidth(size4font(self.x, self.maxboxwidth))
        self.y.setMinimumWidth(size4font(self.y, self.minboxwidth))
        self.y.setMaximumWidth(size4font(self.y, self.maxboxwidth))
        self.y2.setMinimumWidth(size4font(self.y2, self.minboxwidth))
        self.y2.setMaximumWidth(size4font(self.y2, self.maxboxwidth))

        

    def next_x(self):
        """
        Command called if next button for the x-variable was
        pressed.

        Resets dimensions of x-variable.
        Redraws plot.

        """
        idx = self.x.currentIndex()
        idx += 1
        if idx < self.x.count():
            self.x.setCurrentIndex(idx)
            self.xlim.setText('None')
            self.redraw()

    def next_y(self):
        """
        Command called if next button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        idx = self.y.currentIndex()
        idx += 1
        if idx < self.y.count():
            self.y.setCurrentIndex(idx)
            self.ylim.setText('None')
            self.redraw()

    def next_y2(self):
        """
        Command called if next button for the right-hand-side y-variable was
        pressed.

        Resets dimensions of right-hand-side y-variable.
        Redraws plot.

        """
        idx = self.y2.currentIndex()
        idx += 1
        if idx < self.y2.count():
            self.y2.setCurrentIndex(idx)
            self.y2lim.setText('None')
            self.redraw()

    def prev_x(self):
        """
        Command called if previous button for the x-variable was
        pressed.

        Resets dimensions of x-variable.
        Redraws plot.

        """
        idx = self.x.currentIndex()
        idx -= 1
        if idx > 0:
            self.x.setCurrentIndex(idx)
            self.xlim.setText('None')
            self.redraw()

    def prev_y(self):
        """
        Command called if previous button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        idx = self.y.currentIndex()
        idx -= 1
        if idx > 0:
            self.y.setCurrentIndex(idx)
            self.ylim.setText('None')
            self.redraw()

    def prev_y2(self):
        """
        Command called if previous button for the right-hand-side
        y-variable was pressed.

        Resets dimensions of right-hand-side y-variable.
        Redraws plot.

        """
        idx = self.y2.currentIndex()
        idx -= 1
        if idx > 0:
            self.y2.setCurrentIndex(idx)
            self.y2lim.setText('None')
            self.redraw()

    def quit_app(self):
        """
        Quit application.

        """
        sys.exit()

    def resetvars(self, nosort=True):
        """
        Reassign df.columns to comboboxes.

        """
        if self.top.df is not None:
            # check if something to do
            # new variable names
            columns = list(self.top.df.columns)
            if not nosort:
                columns.sort()
            rows = self.top.df.shape[0]
            columns = [ f'{cc} ({rows} {self.top.df[cc].dtype.name})'
                        for cc in columns ]
            self.top.cols = columns
            columns = [''] + self.top.cols

            # check old vs. new variables
            iredo = False
            if len(columns) != self.y.count():
                iredo = True
            else:
                for ii in range(len(columns)):
                    if self.y.itemText(ii) != columns[ii]:
                        iredo = True

            if iredo:
                # save current selections
                x = self.x.currentText()
                y = self.y.currentText()
                y2 = self.y2.currentText()
                nvars = self.y.count()

                for ii, cc in enumerate(columns):
                    if ii < nvars:
                        self.x.setItemText(ii, cc)
                        self.y.setItemText(ii, cc)
                        self.y2.setItemText(ii, cc)
                    else:
                        self.x.addItem(cc)
                        self.y.addItem(cc)
                        self.y2.addItem(cc)

                # delete old entries
                if nvars > len(columns):
                    # removeItem updates index, i.e. start at last item
                    for ii in range(nvars - 1, len(columns) - 1, -1):
                        self.x.removeItem(ii)
                        self.y.removeItem(ii)
                        self.y2.removeItem(ii)

                # re-set current selections
                self.x.setCurrentText(x)
                self.y.setCurrentText(y)
                self.y2.setCurrentText(y2)

    def selected_x(self, event):
        """
        Command called if x-variable was selected with combobox.

        Redraws plot.

        """
        self.xlim.setText('None')
        self.redraw()

    def selected_y(self, event):
        """
        Command called if left-hand-side y-variable was selected with
        combobox.

        Redraws plot.

        """
        self.ylim.setText('None')
        self.redraw()

    def selected_y2(self, event):
        """
        Command called if right-hand-side y-variable was selected with
        combobox.

        Redraws plot.

        """
        self.y2lim.setText('None')
        self.redraw()

    def sortvars(self):
        """
        Sort variable names in comboboxes.

        """
        if self.top.df is not None:
            self.resetvars(nosort=False)

    def transform_df(self):
        """
        Manipulate DataFrame.

        """
        # a second window must be assigned to self (or stored in a
        # persistent variable) so that Python's garbage collector does
        # not delete it immediately.
        self.trans = dfvTransform(self)

    #
    # Methods
    #

    def reinit(self):
        """
        Reinitialise the panel from top.

        """
        # reinit from top
        if self.top.csvfile[0]:
            tit = f"dfvue {self.top.csvfile}"
        else:
            tit = QCoreApplication.applicationName()
        self.setWindowTitle(tit)

        # set variables
        if self.top.df is not None:
            self.resetvars(nosort=True)
        else:
            # remove all entries
            for ii in range(self.y.count() - 1, -1, -1):
                self.x.removeItem(ii)
                self.y.removeItem(ii)
                self.y2.removeItem(ii)

        # set variables and options
        self.x.setCurrentIndex(0)
        self.inv_x.setChecked(False)
        self.y.setCurrentIndex(0)
        self.inv_y.setChecked(False)

        self.ls.setText('-')
        self.lw.setText('1')
        self.lc.setText(self.col1)
        self.marker.setText('None')
        self.ms.setText('1')
        self.mfc.setText(self.col1)
        self.mec.setText(self.col1)
        self.mew.setText('1')
        self.xlim.setText('None')
        self.ylim.setText('None')

        self.y2.setCurrentIndex(0)
        self.inv_y2.setChecked(False)
        self.same_y.setChecked(False)
        self.ls2.setText('-')
        self.lw2.setText('1')
        self.lc2.setText(self.col2)
        self.marker2.setText('None')
        self.ms2.setText('1')
        self.mfc2.setText(self.col2)
        self.mec2.setText(self.col2)
        self.mew2.setText('1')
        self.y2lim.setText('None')

    def reset(self):
        """
        Reinit and redraw.

        """
        self.reinit()
        self.redraw()

    #
    # Plot
    #

    def redraw_y(self):
        """
        Redraw the left-hand-side y-axis.

        Reads left-hand-side `y` variable name, the current settings of
        its dimension spinboxes, as well as all other plotting options.
        Then redraws the left-hand-side y-axis.

        """
        # get all states
        # rowxy
        y = self.y.currentText()
        if y != '':
            inv_y = self.inv_y.isChecked()
            ylim = parse_entry(self.ylim.text())
            ylim2 = parse_entry(self.y2lim.text())
            # rowxyopt
            ls = self.ls.text()
            lw = float(self.lw.text())
            c = str(self.lc.text())
            try:
                if isinstance(eval(c), tuple):
                    c = eval(c)
            except:  # several different exceptions possible
                pass
            m = self.marker.text()
            ms = float(self.ms.text())
            mfc = self.mfc.text()
            try:
                if isinstance(eval(mfc), tuple):
                    mfc = eval(mfc)
            except:
                pass
            mec = self.mec.text()
            try:
                if isinstance(eval(mec), tuple):
                    mec = eval(mec)
            except:
                pass
            mew = float(self.mew.text())
            # rowy2
            y2 = self.y2.currentText()
            same_y = self.same_y.isChecked()
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mfc,
                     'markeredgecolor': mec,
                     'markeredgewidth': mew}
            vy = vardim2var(y)
            ylab = self.top.df[vy].name
            if len(self.line_y) == 1:
                # set color only if single line,
                # None and 'None' do not work for multiple lines
                pargs['color'] = c
            # set style
            for ll in self.line_y:
                plt.setp(ll, **pargs)
            if 'color' in pargs:
                ic = pargs['color']
                if (ic != 'None'):
                    self.canvas.axes.spines['left'].set_color(ic)
                    self.canvas.axes.tick_params(axis='y', colors=ic)
                    self.canvas.axes.yaxis.label.set_color(ic)
            self.canvas.axes.yaxis.set_label_text(ylab)
            # same y-axes
            if not isinstance(ylim, list):
                ylim = self.canvas.axes.get_ylim()
            if not isinstance(ylim2, list):
                ylim2 = self.canvas.axes2.get_ylim()
            if same_y and (y2 != ''):
                ymin, ymax = _minmax_ylim(ylim, ylim2)
                if (ymin is not None) and (ymax is not None):
                    ylim  = [ymin, ymax]
                    ylim2 = [ymin, ymax]
                self.canvas.axes.set_ylim(ylim)
                self.canvas.axes2.set_ylim(ylim2)
            # invert y-axis
            if inv_y and (ylim[0] is not None):
                if ylim[0] < ylim[1]:
                    ylim = ylim[::-1]
                self.canvas.axes.set_ylim(ylim)
            else:
                if ylim[1] < ylim[0]:
                    ylim = ylim[::-1]
                self.canvas.axes.set_ylim(ylim)
            # invert x-axis
            inv_x = self.inv_x.isChecked()
            xlim = parse_entry(self.xlim.text())
            if not isinstance(xlim, list):
                xlim = self.canvas.axes.get_xlim()
            if inv_x and (xlim[0] is not None):
                if xlim[0] < xlim[1]:
                    xlim = xlim[::-1]
                self.canvas.axes.set_xlim(xlim)
            else:
                if xlim[1] < xlim[0]:
                    xlim = xlim[::-1]
                self.canvas.axes.set_xlim(xlim)
            # redraw
            self.canvas.draw()
            self.toolbar.update()

    def redraw_y2(self):
        """
        Redraw the right-hand-side y-axis.

        Reads right-hand-side `y` variable name, the current settings of
        its dimension spinboxes, as well as all other plotting options.
        Then redraws the right-hand-side y-axis.

        """
        # get all states
        # rowy2
        y2 = self.y2.currentText()
        if y2 != '':
            # # rowxy
            # y = self.y.currentText()
            # rowy2
            inv_y2 = self.inv_y2.isChecked()
            same_y = self.same_y.isChecked()
            ylim = parse_entry(self.ylim.text())
            ylim2 = parse_entry(self.y2lim.text())
            # rowy2opt
            ls = self.ls2.text()
            lw = float(self.lw2.text())
            c = self.lc2.text()
            try:
                if isinstance(eval(c), tuple):
                    c = eval(c)
            except:
                pass
            m = self.marker2.text()
            ms = float(self.ms2.text())
            mfc = self.mfc2.text()
            try:
                if isinstance(eval(mfc), tuple):
                    mfc = eval(mfc)
            except:
                pass
            mec = self.mec2.text()
            try:
                if isinstance(eval(mec), tuple):
                    mec = eval(mec)
            except:
                pass
            mew = float(self.mew2.text())
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mfc,
                     'markeredgecolor': mec,
                     'markeredgewidth': mew}
            vy2 = vardim2var(y2)
            ylab = self.top.df[vy2].name
            if len(self.line_y2) == 1:
                # set color only if single line,
                # None and 'None' do not work for multiple lines
                pargs['color'] = c
            # set style
            for ll in self.line_y2:
                plt.setp(ll, **pargs)
            if 'color' in pargs:
                ic = pargs['color']
                if (ic != 'None'):
                    self.canvas.axes2.spines['left'].set_color(ic)
                    self.canvas.axes2.tick_params(axis='y', colors=ic)
                    self.canvas.axes2.yaxis.label.set_color(ic)
            self.canvas.axes2.yaxis.set_label_text(ylab)
            # same y-axes
            if not isinstance(ylim, list):
                ylim = self.canvas.axes.get_ylim()
            if not isinstance(ylim2, list):
                ylim2 = self.canvas.axes2.get_ylim()
            if same_y and (y2 != ''):
                ymin, ymax = _minmax_ylim(ylim, ylim2)
                if (ymin is not None) and (ymax is not None):
                    ylim  = [ymin, ymax]
                    ylim2 = [ymin, ymax]
                self.canvas.axes.set_ylim(ylim)
                self.canvas.axes2.set_ylim(ylim2)
            # invert y-axis
            ylim = ylim2
            if inv_y2 and (ylim[0] is not None):
                if ylim[0] < ylim[1]:
                    ylim = ylim[::-1]
                self.canvas.axes2.set_ylim(ylim)
            else:
                if ylim[1] < ylim[0]:
                    ylim = ylim[::-1]
                self.canvas.axes2.set_ylim(ylim)
            # invert x-axis
            inv_x = self.inv_x.isChecked()
            xlim = parse_entry(self.xlim.text())
            if not isinstance(xlim, list):
                xlim = self.canvas.axes.get_xlim()
            if inv_x and (xlim[0] is not None):
                if xlim[0] < xlim[1]:
                    xlim = xlim[::-1]
                self.canvas.axes.set_xlim(xlim)
            else:
                if xlim[1] < xlim[0]:
                    xlim = xlim[::-1]
                self.canvas.axes.set_xlim(xlim)
            # redraw
            self.canvas.draw()
            self.toolbar.update()

    def redraw(self, event=None):
        """
        Redraw the left-hand-side and right-hand-side y-axis.

        Reads the two `y` variable names, the current settings of
        their dimension spinboxes, as well as all other plotting options.
        Then redraws both y-axes.

        """
        # get all states
        # rowxy
        x = self.x.currentText()
        y = self.y.currentText()
        # rowy2
        y2 = self.y2.currentText()
        # # snap coordinates
        # snap_coord = self.snap_coord.isChecked()

        # Clear both axes first, otherwise x-axis shows only if
        # line2 is chosen.
        self.canvas.axes.clear()
        self.canvas.axes2.clear()
        self.canvas.axes2.yaxis.set_label_position('right')
        self.canvas.axes2.yaxis.tick_right()
        # set x, y, axes labels
        if (y != '') or (y2 != ''):
            # y axis
            if y != '':
                vy = vardim2var(y)
                yy = self.top.df[vy]
                ylab = yy.name
            # y2 axis
            if y2 != '':
                vy2 = vardim2var(y2)
                yy2 = self.top.df[vy2]
                ylab2 = yy2.name
            if (x != ''):
                # x axis
                vx = vardim2var(x)
                xx = self.top.df[vx]
                xlab = xx.name
            else:
                # set x to index if not selected
                xx = self.top.df.index
                xlab = ''
            # set y-axes to nan if not selected
            if (y == ''):
                yy = np.ones_like(xx, dtype='float') * np.nan
                ylab = ''
            if (y2 == ''):
                yy2 = np.ones_like(xx, dtype='float') * np.nan
                ylab2 = ''
            # plot
            # y-axis
            try:
                self.line_y = self.canvas.axes.plot(xx, yy)
            except Exception:
                estr = ('Scatter: x (' + vx + ') and y (' + vy + ')'
                        ' shapes do not match for plot:')
                print(estr, xx.shape, yy.shape)
                return
            self.canvas.axes.xaxis.set_label_text(xlab)
            self.canvas.axes.yaxis.set_label_text(ylab)
            # y2-axis
            try:
                self.line_y2 = self.canvas.axes2.plot(xx, yy2)
            except Exception:
                estr  = 'Scatter: x (' + vx + ') and y2 (' + vy2 + ')'
                estr += ' shapes do not match for plot:'
                print(estr, xx.shape, yy2.shape)
                return
            # self.canvas.axes2.format_coord = lambda x, y2: format_coord_scatter(
            #     x, y2, self.canvas.axes, self.canvas.axes2, xx, yy, yy2, snap_coord)
            self.canvas.axes2.xaxis.set_label_text(xlab)
            self.canvas.axes2.yaxis.set_label_text(ylab2)
            # styles, invert, same axes, etc.
            self.redraw_y()
            self.redraw_y2()
            # redraw
            self.canvas.draw()
            self.toolbar.update()
        else:
            self.line_y = self.canvas.axes.plot([0.], [0.])
            self.canvas.draw()
            self.toolbar.update()


    # def resnap(self, event=None):
    #     """
    #     Change axes.format_coord depending snap_coord checkbox.

    #     Changes the behaviour of format_coord depending on snap_coord checkbox
    #     without redrawing whole figure.

    #     """
    #     # rowxy
    #     x = self.x.currentText()
    #     y = self.y.currentText()
    #     # rowy2
    #     y2 = self.y2.currentText()
    #     # snap coordinates
    #     snap_coord = self.snap_coord.isChecked()

    #     # set x, y, axes labels
    #     if (y != '') or (y2 != ''):
    #         # y axis
    #         if y != '':
    #             vy = vardim2var(y)
    #             yy = self.top.df[vy]
    #         # y2 axis
    #         if y2 != '':
    #             vy2 = vardim2var(y2)
    #             yy2 = self.top.df[vy2]
    #         if (x != ''):
    #             # x axis
    #             vx = vardim2var(x)
    #             xx = self.top.df[vx]
    #         else:
    #             # set x to index if not selected
    #             xx = self.top.df.index
    #         # set y-axes to nan if not selected
    #         if (y == ''):
    #             yy = np.ones_like(xx, dtype='float') * np.nan
    #         if (y2 == ''):
    #             yy2 = np.ones_like(xx, dtype='float') * np.nan
    #         self.canvas.axes2.format_coord = lambda x, y2: format_coord_scatter(
    #             x, y2, self.canvas.axes, self.canvas.axes2, xx, yy, yy2, snap_coord)
    #         # styles, invert, same axes, etc.
    #         self.redraw_y()
    #         self.redraw_y2()
    #         # redraw
    #         self.canvas.draw()
    #         self.toolbar.update()
