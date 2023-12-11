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

"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import numpy as np
import pandas as pd
from .dfvutils import clone_dfvmain, format_coord_scatter, vardim2var
from .ncvwidgets import add_checkbutton, add_combobox, add_entry
from .ncvwidgets import add_tooltip
from .dfvreadcsv import dfvReadcsv
# import matplotlib
# matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
# plt.style.use('seaborn-darkgrid')
plt.style.use('seaborn-dark')
# plt.style.use('fast')


__all__ = ['dfvScatter']


class dfvScatter(ttk.Frame):
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
        from functools import partial
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        from matplotlib.figure import Figure

        super().__init__(master, **kwargs)

        self.name   = 'Scatter/Line'
        self.master = master
        self.top    = master.top

        # copy for ease of use
        self.csvfile = self.top.csvfile
        self.newcsvfile = self.top.newcsvfile
        self.df = self.top.df
        self.sep = self.top.sep
        self.index_col = self.top.index_col
        self.skiprows = self.top.skiprows
        self.parse_dates = self.top.parse_dates
        self.date_format = self.top.date_format
        self.missing_value = self.top.missing_value
        self.cols = self.top.cols

        # row new window
        self.rowwin = ttk.Frame(self)
        self.rowwin.pack(side=tk.TOP, fill=tk.X)
        self.newfile = ttk.Button(self.rowwin, text="Open File",
                                  command=self.new_csv)
        self.newfile.pack(side=tk.LEFT)
        self.newfiletip = add_tooltip(self.newfile, 'Open a new csv file')
        self.newwin = ttk.Button(
            self.rowwin, text="New Window",
            command=partial(clone_dfvmain, self.master))
        self.newwin.pack(side=tk.RIGHT)
        self.newwintip = add_tooltip(
            self.newwin, 'Open secondary dfvue window')

        # plotting canvas
        self.figure = Figure(facecolor="white", figsize=(1, 1))
        self.axes   = self.figure.add_subplot(111)
        self.axes2  = self.axes.twinx()
        self.axes2.yaxis.set_label_position("right")
        self.axes2.yaxis.tick_right()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        # pack
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # selections and options
        columns = [''] + self.cols
        # colors
        c = list(plt.rcParams['axes.prop_cycle'])
        col1 = c[0]['color']  # blue
        col2 = c[3]['color']  # red
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

        # 1. row
        # x- and lhs y-axis selection
        self.rowxy = ttk.Frame(self)
        self.rowxy.pack(side=tk.TOP, fill=tk.X)
        # block x with dimensions
        self.blockx = ttk.Frame(self.rowxy)
        self.blockx.pack(side=tk.LEFT)
        self.rowx = ttk.Frame(self.blockx)
        self.rowx.pack(side=tk.TOP, fill=tk.X)
        self.xlbl, self.x, self.xtip = add_combobox(
            self.rowx, label="x", values=columns, command=self.selected_x,
            tooltip="Choose variable of x-axis.\nTake index if 'None' (fast).")
        # self.x0 = ''
        self.line_x = []
        self.inv_xlbl, self.inv_x, self.inv_xtip = add_checkbutton(
            self.rowx, label="invert x", value=False,
            command=self.checked_x,
            tooltip="Invert x-axis")
        # block y with dimensions
        spacex = ttk.Label(self.rowxy, text=" " * 3)
        spacex.pack(side=tk.LEFT)
        self.blocky = ttk.Frame(self.rowxy)
        self.blocky.pack(side=tk.LEFT)
        self.rowy = ttk.Frame(self.blocky)
        self.rowy.pack(side=tk.TOP, fill=tk.X)
        self.ylbl = tk.StringVar()
        self.ylbl.set("y")
        ylab = ttk.Label(self.rowy, textvariable=self.ylbl)
        ylab.pack(side=tk.LEFT)
        self.bprev_y = ttk.Button(self.rowy, text="<", width=1,
                                  command=self.prev_y)
        self.bprev_y.pack(side=tk.LEFT)
        self.bprev_ytip = add_tooltip(self.bprev_y, 'Previous variable')
        self.bnext_y = ttk.Button(self.rowy, text=">", width=1,
                                  command=self.next_y)
        self.bnext_y.pack(side=tk.LEFT)
        self.bnext_ytip = add_tooltip(self.bnext_y, 'Next variable')
        self.y = ttk.Combobox(self.rowy, values=columns, width=25)
        # long = len(max(columns, key=len))
        # self.y.configure(width=(max(20, long//2)))
        self.y.bind("<<ComboboxSelected>>", self.selected_y)
        self.y.pack(side=tk.LEFT)
        self.ytip = add_tooltip(self.y, 'Choose variable of y-axis')
        # self.y0 = ''
        self.line_y = []
        self.inv_ylbl, self.inv_y, self.inv_ytip = add_checkbutton(
            self.rowy, label="invert y", value=False,
            command=self.checked_y,
            tooltip="Inert y-axis")
        # redraw button
        self.bredraw = ttk.Button(self.rowxy, text="Redraw",
                                  command=self.redraw)
        self.bredraw.pack(side=tk.RIGHT)
        self.bredrawtip = add_tooltip(self.bredraw, 'Redraw, resetting zoom')

        # 2. row
        # options for lhs y-axis
        self.rowxyopt = ttk.Frame(self)
        self.rowxyopt.pack(side=tk.TOP, fill=tk.X)
        self.lslbl, self.ls, self.lstip = add_entry(
            self.rowxyopt, label="ls", text='-', width=4,
            command=self.entered_y,
            tooltip="Line style: -, --, -., :, or None")
        self.lwlbl, self.lw, self.lwtip = add_entry(
            self.rowxyopt, label="lw", text='1', width=3,
            command=self.entered_y, tooltip="Line width")
        self.lclbl, self.lc, self.lctip = add_entry(
            self.rowxyopt, label="c", text=col1, width=7,
            command=self.entered_y,
            tooltip="Line color:\n" + ctstr)
        self.markerlbl, self.marker, self.markertip = add_entry(
            self.rowxyopt, label="marker", text='None', width=4,
            command=self.entered_y,
            tooltip="Marker symbol:\n" + mtstr)
        self.mslbl, self.ms, self.mstip = add_entry(
            self.rowxyopt, label="ms", text='1', width=3,
            command=self.entered_y, tooltip="Marker size")
        self.mfclbl, self.mfc, self.mfctip = add_entry(
            self.rowxyopt, label="mfc", text=col1, width=7,
            command=self.entered_y,
            tooltip="Marker fill color:\n" + ctstr)
        self.meclbl, self.mec, self.mectip = add_entry(
            self.rowxyopt, label="mec", text=col1, width=7,
            command=self.entered_y,
            tooltip="Marker edge color:\n" + ctstr)
        self.mewlbl, self.mew, self.mewtip = add_entry(
            self.rowxyopt, label="mew", text='1', width=3,
            command=self.entered_y, tooltip="Marker edge width")
        # redraw button
        self.bsort = ttk.Button(self.rowxyopt, text="Sort vars",
                                command=self.sortvars)
        self.bsort.pack(side=tk.RIGHT)
        self.bsorttip = add_tooltip(self.bsort, 'Sort variable names')

        # space
        self.rowspace = ttk.Frame(self)
        self.rowspace.pack(side=tk.TOP, fill=tk.X)
        rowspace = ttk.Label(self.rowspace, text=" ")
        rowspace.pack(side=tk.LEFT)

        # 3. row
        # rhs y-axis 2 selection
        self.rowyy2 = ttk.Frame(self)
        self.rowyy2.pack(side=tk.TOP, fill=tk.X)
        self.blocky2 = ttk.Frame(self.rowyy2)
        self.blocky2.pack(side=tk.LEFT)
        self.rowy2 = ttk.Frame(self.blocky2)
        self.rowy2.pack(side=tk.TOP, fill=tk.X)
        self.y2lbl, self.y2, self.y2tip = add_combobox(
            self.rowy2, label="y2", values=columns,
            command=self.selected_y2,
            tooltip="Choose variable for right-hand-side y-axis")
        # self.y20 = ''
        self.line_y2 = []
        self.inv_y2lbl, self.inv_y2, self.inv_y2tip = add_checkbutton(
            self.rowy2, label="invert y2", value=False,
            command=self.checked_y2,
            tooltip="Invert right-hand-side y-axis")
        spacey2 = ttk.Label(self.rowy2, text=" " * 1)
        spacey2.pack(side=tk.LEFT)
        tstr = "Same limits for left-hand-side and right-hand-side y-axes"
        self.same_ylbl, self.same_y, self.same_ytip = add_checkbutton(
            self.rowy2, label="same y-axes", value=False,
            command=self.checked_yy2, tooltip=tstr)

        # 4. row
        # options for rhs y-axis 2
        self.rowy2opt = ttk.Frame(self)
        self.rowy2opt.pack(side=tk.TOP, fill=tk.X)
        self.ls2lbl, self.ls2, self.ls2tip = add_entry(
            self.rowy2opt, label="ls", text='-', width=4,
            command=self.entered_y2,
            tooltip="Line style: -, --, -., :, or None")
        self.lw2lbl, self.lw2, self.lw2tip = add_entry(
            self.rowy2opt, label="lw", text='1', width=3,
            command=self.entered_y2, tooltip="Line width")
        self.lc2lbl, self.lc2, self.lc2tip = add_entry(
            self.rowy2opt, label="c", text=col2, width=7,
            command=self.entered_y2,
            tooltip="Line color:\n" + ctstr)
        self.marker2lbl, self.marker2, self.marker2tip = add_entry(
            self.rowy2opt, label="marker", text='None', width=4,
            command=self.entered_y2,
            tooltip="Marker symbol:\n" + mtstr)
        self.ms2lbl, self.ms2, self.ms2tip = add_entry(
            self.rowy2opt, label="ms", text='1', width=3,
            command=self.entered_y2, tooltip="Marker size")
        self.mfc2lbl, self.mfc2, self.mfc2tip = add_entry(
            self.rowy2opt, label="mfc", text=col2, width=7,
            command=self.entered_y2, tooltip="Marker fill color:\n" + ctstr)
        self.mec2lbl, self.mec2, self.mec2tip = add_entry(
            self.rowy2opt, label="mec", text=col2, width=7,
            command=self.entered_y2, tooltip="Marker edge color:\n" + ctstr)
        self.mew2lbl, self.mew2, self.mew2tip = add_entry(
            self.rowy2opt, label="mew", text='1', width=3,
            command=self.entered_y2, tooltip="Marker edge width")
        # Quit button
        self.bquit = ttk.Button(self.rowy2opt, text="Quit",
                                command=self.master.top.destroy)
        self.bquit.pack(side=tk.RIGHT)
        self.bquittip = add_tooltip(self.bquit, 'Quit dfvue')

        if self.csvfile and (self.master.master.name == 'dfvOne'):
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
        self.redraw_y()
        self.redraw_y2()

    def entered_y(self, event):
        """
        Command called if option was entered for left-hand-side y-axis.

        Redraws left-hand-side y-axis.

        """
        self.redraw_y()

    def entered_y2(self, event):
        """
        Command called if option was entered for right-hand-side y-axis.

        Redraws right-hand-side y-axis.

        """
        self.redraw_y2()

    def new_csv(self):
        """
        Open a new csv file and connect it to top.

        """
        # get new csv file name
        self.top.csvfile = filedialog.askopenfilename(
            parent=self, title='Choose csv file', multiple=False)

        if self.top.csvfile:
            self.top.newcsvfile = True
            self.new_df()

    def new_df(self):
        """
        Read new DataFrame.

        """
        self.top.df = pd.read_csv(self.top.csvfile, nrows=40)
        dfvReadcsv(self.top, callback=self.reset)

    def next_y(self):
        """
        Command called if next button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        y = self.y.get()
        cols = self.y["values"]
        idx  = cols.index(y)
        idx += 1
        if idx < len(cols):
            self.y.set(cols[idx])
            self.redraw()

    # def onpick(self, event):
    #     print('in pick')
    #     print('you pressed', event.button, event.xdata, event.ydata)
    #     thisline = event.artist
    #     xdata = thisline.get_xdata()
    #     ydata = thisline.get_ydata()
    #     ind = event.ind
    #     points = tuple(zip(xdata[ind], ydata[ind]))
    #     print('onpick points:', points)

    def prev_y(self):
        """
        Command called if previous button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        y = self.y.get()
        cols = self.y["values"]
        idx  = cols.index(y)
        idx -= 1
        if idx > 0:
            self.y.set(cols[idx])
            self.redraw()

    def selected_x(self, event):
        """
        Command called if x-variable was selected with combobox.

        Triggering `event` was bound to the combobox.

        Redraws plot.

        """
        self.redraw()

    def selected_y(self, event):
        """
        Command called if left-hand-side y-variable was selected with
        combobox.

        Triggering `event` was bound to the combobox.

        Redraws plot.

        """
        self.redraw()

    def selected_y2(self, event):
        """
        Command called if right-hand-side y-variable was selected with
        combobox.

        Triggering `event` was bound to the combobox.

        Redraws plot.

        """
        self.redraw()

    def sortvars(self):
        """
        Sort variable names in comboboxes.

        Triggering `event` was bound to button bsort.

        """
        if self.df is not None:
            columns = list(self.df.columns)
            columns.sort()
            rows = self.df.shape[0]
            columns = [ f'{cc} ({rows} {self.df[cc].dtype.name})'
                        for cc in columns ]
            if self.df.index.name is not None:
                idx = (f'{self.df.index.name}'
                       f' (index {rows} {self.df.index.dtype.name})')
            else:
                idx = f'index ({rows} {self.df.index.dtype.name})'
            self.cols = [idx]
            self.cols.extend(columns)
            # set variables
            columns = [''] + self.cols
            x = self.x.get()
            self.x['values'] = columns
            self.x.set(x)
            y = self.y.get()
            self.y['values'] = columns
            self.y.set(y)
            y2 = self.y2.get()
            self.y2['values'] = columns
            self.y2.set(y2)

    def spinned_x(self, event=None):
        """
        Command called if spinbox of x-dimensions was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.

        """
        self.redraw()

    def spinned_y(self, event=None):
        """
        Command called if spinbox of any dimension of left-hand-side
        y-variable was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.

        """
        self.redraw()

    def spinned_y2(self, event=None):
        """
        Command called if spinbox of any dimension of right-hand-side
        y-variable was changed.

        Triggering `event` was bound to the spinbox.

        Redraws plot.

        """
        self.redraw()

    #
    # Methods
    #

    def minmax_ylim(self, ylim, ylim2):
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

    def reinit(self):
        """
        Reinitialise the panel from top.

        """
        # reinit from top
        self.csvfile = self.top.csvfile
        self.newcsvfile = self.top.newcsvfile
        self.df = self.top.df
        self.sep = self.top.sep
        self.index_col = self.top.index_col
        self.skiprows = self.top.skiprows
        self.parse_dates = self.top.parse_dates
        self.date_format = self.top.date_format
        self.missing_value = self.top.missing_value
        self.cols = self.top.cols
        if self.top.csvfile:
            tit = "dfvue " + self.top.csvfile
        else:
            tit = "dfvue"
        self.master.master.title(tit)
        # set variables
        columns = [''] + self.cols
        self.x['values'] = columns
        self.x.set(columns[0])
        self.y['values'] = columns
        self.y.set(columns[0])
        self.y2['values'] = columns
        self.y2.set(columns[0])

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
        y = self.y.get()
        if y != '':
            inv_y = self.inv_y.get()
            # rowxyopt
            ls = self.ls.get()
            lw = float(self.lw.get())
            c = str(self.lc.get())
            try:
                if isinstance(eval(c), tuple):
                    c = eval(c)
            except:  # several different exceptions possible
                pass
            m = self.marker.get()
            ms = float(self.ms.get())
            mfc = self.mfc.get()
            try:
                if isinstance(eval(mfc), tuple):
                    mfc = eval(mfc)
            except:
                pass
            mec = self.mec.get()
            try:
                if isinstance(eval(mec), tuple):
                    mec = eval(mec)
            except:
                pass
            mew = float(self.mew.get())
            # rowy2
            y2 = self.y2.get()
            same_y = self.same_y.get()
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mfc,
                     'markeredgecolor': mec,
                     'markeredgewidth': mew}
            vy = vardim2var(y)
            ylab = self.df[vy].name
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
                    self.axes.spines['left'].set_color(ic)
                    self.axes.tick_params(axis='y', colors=ic)
                    self.axes.yaxis.label.set_color(ic)
            self.axes.yaxis.set_label_text(ylab)
            # same y-axes
            ylim  = self.axes.get_ylim()
            ylim2 = self.axes2.get_ylim()
            if same_y and (y2 != ''):
                ymin, ymax = self.minmax_ylim(ylim, ylim2)
                if (ymin is not None) and (ymax is not None):
                    ylim  = [ymin, ymax]
                    ylim2 = [ymin, ymax]
                    self.axes.set_ylim(ylim)
                    self.axes2.set_ylim(ylim2)
            # invert y-axis
            if inv_y and (ylim[0] is not None):
                if ylim[0] < ylim[1]:
                    ylim = ylim[::-1]
                    self.axes.set_ylim(ylim)
            else:
                if ylim[1] < ylim[0]:
                    ylim = ylim[::-1]
                    self.axes.set_ylim(ylim)
            # invert x-axis
            inv_x = self.inv_x.get()
            xlim  = self.axes.get_xlim()
            if inv_x and (xlim[0] is not None):
                if xlim[0] < xlim[1]:
                    xlim = xlim[::-1]
                    self.axes.set_xlim(xlim)
            else:
                if xlim[1] < xlim[0]:
                    xlim = xlim[::-1]
                    self.axes.set_xlim(xlim)
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
        y2 = self.y2.get()
        if y2 != '':
            # # rowxy
            # y = self.y.get()
            # rowy2
            inv_y2 = self.inv_y2.get()
            same_y = self.same_y.get()
            # rowy2opt
            ls = self.ls2.get()
            lw = float(self.lw2.get())
            c = self.lc2.get()
            try:
                if isinstance(eval(c), tuple):
                    c = eval(c)
            except:
                pass
            m = self.marker2.get()
            ms = float(self.ms2.get())
            mfc = self.mfc2.get()
            try:
                if isinstance(eval(mfc), tuple):
                    mfc = eval(mfc)
            except:
                pass
            mec = self.mec2.get()
            try:
                if isinstance(eval(mec), tuple):
                    mec = eval(mec)
            except:
                pass
            mew = float(self.mew2.get())
            # y plotting styles
            pargs = {'linestyle': ls,
                     'linewidth': lw,
                     'marker': m,
                     'markersize': ms,
                     'markerfacecolor': mfc,
                     'markeredgecolor': mec,
                     'markeredgewidth': mew}
            vy2 = vardim2var(y2)
            ylab = self.df[vy2].name
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
                    self.axes2.spines['left'].set_color(ic)
                    self.axes2.tick_params(axis='y', colors=ic)
                    self.axes2.yaxis.label.set_color(ic)
            self.axes2.yaxis.set_label_text(ylab)
            # same y-axes
            ylim  = self.axes.get_ylim()
            ylim2 = self.axes2.get_ylim()
            if same_y and (y2 != ''):
                ymin, ymax = self.minmax_ylim(ylim, ylim2)
                if (ymin is not None) and (ymax is not None):
                    ylim  = [ymin, ymax]
                    ylim2 = [ymin, ymax]
                    self.axes.set_ylim(ylim)
                    self.axes2.set_ylim(ylim2)
            # invert y-axis
            ylim = ylim2
            if inv_y2 and (ylim[0] is not None):
                if ylim[0] < ylim[1]:
                    ylim = ylim[::-1]
                    self.axes2.set_ylim(ylim)
            else:
                if ylim[1] < ylim[0]:
                    ylim = ylim[::-1]
                    self.axes2.set_ylim(ylim)
            # invert x-axis
            inv_x = self.inv_x.get()
            xlim  = self.axes.get_xlim()
            if inv_x and (xlim[0] is not None):
                if xlim[0] < xlim[1]:
                    xlim = xlim[::-1]
                    self.axes.set_xlim(xlim)
            else:
                if xlim[1] < xlim[0]:
                    xlim = xlim[::-1]
                    self.axes.set_xlim(xlim)
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
        x = self.x.get()
        y = self.y.get()
        # rowy2
        y2 = self.y2.get()

        # Clear both axes first, otherwise x-axis shows only if
        # line2 is chosen.
        # if (x != self.x0) or (y != self.y0):
        self.axes.clear()
        # if (x != self.x0) or (y2 != self.y20):
        self.axes2.clear()
        self.axes2.yaxis.set_label_position("right")
        self.axes2.yaxis.tick_right()
        # set x, y, axes labels
        if (y != '') or (y2 != ''):
            # y axis
            if y != '':
                vy = vardim2var(y)
                yy = self.df[vy]
                ylab = yy.name
            # y2 axis
            if y2 != '':
                vy2 = vardim2var(y2)
                yy2 = self.df[vy2]
                ylab2 = yy2.name
            if (x != ''):
                # x axis
                vx = vardim2var(x)
                xx = self.df[vx]
                xlab = xx.name
            else:
                # set x to index if not selected
                xx = self.df.index
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
                # , picker=True, pickradius=5)
                self.line_y = self.axes.plot(xx, yy)
            except Exception:
                estr = ('Scatter: x (' + vx + ') and y (' + vy + ')'
                        ' shapes do not match for plot:')
                print(estr, xx.shape, yy.shape)
                return
            self.axes.xaxis.set_label_text(xlab)
            self.axes.yaxis.set_label_text(ylab)
            # y2-axis
            try:
                # , picker=True, pickradius=5)
                self.line_y2 = self.axes2.plot(xx, yy2)
            except Exception:
                estr  = 'Scatter: x (' + vx + ') and y2 (' + vy2 + ')'
                estr += ' shapes do not match for plot:'
                print(estr, xx.shape, yy2.shape)
                return
            self.axes2.format_coord = lambda x, y: format_coord_scatter(
                x, y, self.axes, self.axes2, xx.dtype, yy.dtype, yy2.dtype)
            self.axes2.xaxis.set_label_text(xlab)
            self.axes2.yaxis.set_label_text(ylab2)
            # styles, invert, same axes, etc.
            self.redraw_y()
            self.redraw_y2()
            # redraw
            # self.x0  = x
            # self.y0  = y
            # self.y20 = y2
            self.canvas.draw()
            self.toolbar.update()
        else:
            self.line_y = self.axes.plot([0.], [0.])
            self.canvas.draw()
            self.toolbar.update()
