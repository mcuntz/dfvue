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

"""
import tkinter as tk
try:
    from customtkinter import CTkFrame as Frame
    from customtkinter import CTkButton as Button
    from customtkinter import CTkLabel as Label
    from customtkinter import CTkComboBox as Combobox
    ihavectk = True
except ModuleNotFoundError:
    from tkinter.ttk import Frame
    from tkinter.ttk import Button
    from tkinter.ttk import Label
    from tkinter.ttk import Combobox
    ihavectk = False
from tkinter import filedialog
import numpy as np
import pandas as pd
from .dfvutils import clone_dfvmain, format_coord_scatter, vardim2var
from .ncvwidgets import add_checkbutton, add_combobox, add_entry
from .ncvwidgets import add_tooltip
from .dfvreadcsv import dfvReadcsv
from matplotlib import pyplot as plt
try:
    plt.style.use('seaborn-v0_8-dark')
except OSError:
    plt.style.use('seaborn-dark')


__all__ = ['dfvScatter']


class dfvScatter(Frame):
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
        if ihavectk:
            # height of plotting canvas in px
            canvasheight = 550
            # width of combo boxes in px
            combowidth = 288
            # widths of entry widgets in px
            ewsmall = 20
            ewmed = 45
            ewbig = 70
        else:
            # height of plotting canvas
            canvasheight = 550
            # width of combo boxes in characters
            combowidth = 25
            # widths of entry widgets in characters
            ewsmall = 3
            ewmed = 4
            ewbig = 7
            
        # open file and new window
        self.newfile = Button(self, text="Open File",
                                     command=self.new_csv)
        self.newfiletip = add_tooltip(self.newfile, 'Open a new csv file')
        self.newfile.grid(row=0, column=0, sticky=tk.W)
        self.newwin = Button(
            self, text="New Window",
            command=partial(clone_dfvmain, self.master))
        self.newwintip = add_tooltip(
            self.newwin, 'Open secondary dfvue window')
        self.newwin.grid(row=0, column=8, sticky=tk.E)

        # plotting canvas
        self.figure = Figure(facecolor="white", figsize=(1, 1))
        self.axes   = self.figure.add_subplot(111)
        self.axes2  = self.axes.twinx()
        self.axes2.yaxis.set_label_position("right")
        self.axes2.yaxis.tick_right()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.tkcanvas = self.canvas.get_tk_widget()
        self.tkcanvas.grid(row=1, column=0, rowspan=12, columnspan=9,
                           sticky=tk.NSEW)
        # if ihavectk:
        self.rowconfigure(1, minsize=canvasheight)

        # matplotlib toolbar
        # toolbar uses pack internally -> put into frame
        self.toolwin = Frame(self)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolwin,
                                            pack_toolbar=True)
        self.toolbar.update()
        self.toolwin.grid(row=13, column=0, columnspan=9, sticky=tk.W)

        # x-axis and left y-axis
        # block with x
        self.blockx = Frame(self)
        self.blockx.grid(row=14, column=0, columnspan=3, sticky=tk.W)
        # x
        self.xframe, self.xlbl, self.x, self.xtip = add_combobox(
            self.blockx, label="x", values=columns, command=self.selected_x,
            width=combowidth,
            tooltip="Choose variable of x-axis.\nTake index if 'None' (fast).")
        self.xframe.pack(side=tk.LEFT)
        # invert x
        self.line_x = []
        (self.inv_xframe, self.inv_xlbl, self.inv_x,
         self.inv_xtip) = add_checkbutton(
             self.blockx, label="invert x", value=False,
             command=self.checked_x,
             tooltip="Invert x-axis")
        self.inv_xframe.pack(side=tk.LEFT)
        # block with y
        self.blocky = Frame(self)
        self.blocky.grid(row=14, column=3, columnspan=4, sticky=tk.W)
        # y label
        self.ylbl = tk.StringVar()
        self.ylbl.set("y")
        ylab = Label(self.blocky, textvariable=self.ylbl)
        ylab.pack(side='left')
        # previous and next buttons
        self.bprev_y = Button(self.blocky, text="<", width=1,
                                     command=self.prev_y)
        self.bprev_ytip = add_tooltip(self.bprev_y, 'Previous variable')
        self.bprev_y.pack(side='left')
        self.bnext_y = Button(self.blocky, text=">", width=1,
                              command=self.next_y)
        self.bnext_ytip = add_tooltip(self.bnext_y, 'Next variable')
        self.bnext_y.pack(side='left')
        # y
        if ihavectk:
            self.y = Combobox(self.blocky, values=columns, width=combowidth,
                              command=self.selected_y)
        else:
            self.y = Combobox(self.blocky, values=columns, width=combowidth)
            self.y.bind("<<ComboboxSelected>>", self.selected_y)
        self.ytip = add_tooltip(self.y, 'Choose variable of y-axis')
        self.y.pack(side='left')
        # invert y
        self.line_y = []
        (self.inv_yframe, self.inv_ylbl, self.inv_y,
         self.inv_ytip) = add_checkbutton(
             self.blocky, label="invert y", value=False,
             command=self.checked_y,
             tooltip="Invert y-axis")
        self.inv_yframe.pack(side=tk.LEFT)
        # redraw button
        self.bredraw = Button(self, text="Redraw",
                              command=self.redraw)
        self.bredrawtip = add_tooltip(self.bredraw, 'Redraw, resetting zoom')
        self.bredraw.grid(row=14, column=8, sticky=tk.E)

        # options for lhs y-axis
        self.blockyopt = Frame(self)
        self.blockyopt.grid(row=15, column=0, columnspan=6, sticky=tk.W)
        self.lsframe, self.lslbl, self.ls, self.lstip = add_entry(
            self.blockyopt, label="ls", text='-', width=ewmed,
            command=self.entered_y,
            tooltip="Line style: -, --, -., :, or None")
        self.lsframe.pack(side=tk.LEFT)
        self.lwframe, self.lwlbl, self.lw, self.lwtip = add_entry(
            self.blockyopt, label="lw", text='1', width=ewsmall,
            command=self.entered_y, tooltip="Line width")
        self.lwframe.pack(side=tk.LEFT)
        self.lcframe, self.lclbl, self.lc, self.lctip = add_entry(
            self.blockyopt, label="c", text=col1, width=ewbig,
            command=self.entered_y,
            tooltip="Line color:\n" + ctstr)
        self.lcframe.pack(side=tk.LEFT)
        (self.markerframe, self.markerlbl, self.marker,
         self.markertip) = add_entry(
            self.blockyopt, label="marker", text='None', width=ewmed,
            command=self.entered_y,
            tooltip="Marker symbol:\n" + mtstr)
        self.markerframe.pack(side=tk.LEFT)
        self.msframe, self.mslbl, self.ms, self.mstip = add_entry(
            self.blockyopt, label="ms", text='1', width=ewsmall,
            command=self.entered_y, tooltip="Marker size")
        self.msframe.pack(side=tk.LEFT)
        self.mfcframe, self.mfclbl, self.mfc, self.mfctip = add_entry(
            self.blockyopt, label="mfc", text=col1, width=ewbig,
            command=self.entered_y,
            tooltip="Marker fill color:\n" + ctstr)
        self.mfcframe.pack(side=tk.LEFT)
        self.mecframe, self.meclbl, self.mec, self.mectip = add_entry(
            self.blockyopt, label="mec", text=col1, width=ewbig,
            command=self.entered_y,
            tooltip="Marker edge color:\n" + ctstr)
        self.mecframe.pack(side=tk.LEFT)
        self.mewframe, self.mewlbl, self.mew, self.mewtip = add_entry(
            self.blockyopt, label="mew", text='1', width=ewsmall,
            command=self.entered_y, tooltip="Marker edge width")
        self.mewframe.pack(side=tk.LEFT)
        # redraw button
        self.bsort = Button(self, text="Sort vars",
                            command=self.sortvars)
        self.bsorttip = add_tooltip(self.bsort, 'Sort variable names')
        self.bsort.grid(row=15, column=8, sticky=tk.E)

        # empty row
        self.rowconfigure(16, minsize=20)

        # right y2-axis
        self.blocky2 = Frame(self)
        self.blocky2.grid(row=17, column=0, columnspan=4, sticky=tk.W)
        # y label
        self.ylbl2 = tk.StringVar()
        self.ylbl2.set("y2")
        ylab2 = Label(self.blocky2, textvariable=self.ylbl2)
        ylab2.pack(side='left')
        # previous and next buttons
        self.bprev_y2 = Button(self.blocky2, text="<", width=1,
                               command=self.prev_y2)
        self.bprev_y2tip = add_tooltip(self.bprev_y2, 'Previous variable')
        self.bprev_y2.pack(side='left')
        self.bnext_y2 = Button(self.blocky2, text=">", width=1,
                               command=self.next_y2)
        self.bnext_y2tip = add_tooltip(self.bnext_y2, 'Next variable')
        self.bnext_y2.pack(side='left')
        # y
        if ihavectk:
            self.y2 = Combobox(self.blocky2, values=columns, width=combowidth,
                               command=self.selected_y2)
        else:
            self.y2 = Combobox(self.blocky2, values=columns, width=combowidth)
            self.y2.bind("<<ComboboxSelected>>", self.selected_y2)
        self.y2tip = add_tooltip(self.y2,
                                 'Choose variable of right-hand-side y-axis')
        self.y2.pack(side='left')
        # invert y2
        self.line_y2 = []
        (self.inv_y2frame, self.inv_y2lbl, self.inv_y2,
         self.inv_y2tip) = add_checkbutton(
             self.blocky2, label="invert y2", value=False,
             command=self.checked_y2,
             tooltip="Invert right-hand-side y-axis")
        self.inv_y2frame.pack(side=tk.LEFT)
        tstr = "Same limits for left-hand-side and right-hand-side y-axes"
        (self.same_yframe, self.same_ylbl, self.same_y,
         self.same_ytip) = add_checkbutton(
             self.blocky2, label="same y-axes", value=False,
             command=self.checked_yy2, tooltip=tstr)
        self.same_yframe.pack(side=tk.LEFT)

        # options for rhs y-axis 2
        self.blocky2opt = Frame(self)
        self.blocky2opt.grid(row=18, column=0, columnspan=6, sticky=tk.W)
        self.ls2frame, self.ls2lbl, self.ls2, self.ls2tip = add_entry(
            self.blocky2opt, label="ls", text='-', width=ewmed,
            command=self.entered_y2,
            tooltip="Line style: -, --, -., :, or None")
        self.ls2frame.pack(side=tk.LEFT)
        self.lw2frame, self.lw2lbl, self.lw2, self.lw2tip = add_entry(
            self.blocky2opt, label="lw", text='1', width=ewsmall,
            command=self.entered_y2, tooltip="Line width")
        self.lw2frame.pack(side=tk.LEFT)
        self.lc2frame, self.lc2lbl, self.lc2, self.lc2tip = add_entry(
            self.blocky2opt, label="c", text=col2, width=ewbig,
            command=self.entered_y2,
            tooltip="Line color:\n" + ctstr)
        self.lc2frame.pack(side=tk.LEFT)
        (self.marker2frame, self.marker2lbl, self.marker2,
         self.marker2tip) = add_entry(
            self.blocky2opt, label="marker", text='None', width=ewmed,
            command=self.entered_y2,
            tooltip="Marker symbol:\n" + mtstr)
        self.marker2frame.pack(side=tk.LEFT)
        self.ms2frame, self.ms2lbl, self.ms2, self.ms2tip = add_entry(
            self.blocky2opt, label="ms", text='1', width=ewsmall,
            command=self.entered_y2, tooltip="Marker size")
        self.ms2frame.pack(side=tk.LEFT)
        self.mfc2frame, self.mfc2lbl, self.mfc2, self.mfc2tip = add_entry(
            self.blocky2opt, label="mfc", text=col2, width=ewbig,
            command=self.entered_y2, tooltip="Marker fill color:\n" + ctstr)
        self.mfc2frame.pack(side=tk.LEFT)
        self.mec2frame, self.mec2lbl, self.mec2, self.mec2tip = add_entry(
            self.blocky2opt, label="mec", text=col2, width=ewbig,
            command=self.entered_y2, tooltip="Marker edge color:\n" + ctstr)
        self.mec2frame.pack(side=tk.LEFT)
        self.mew2frame, self.mew2lbl, self.mew2, self.mew2tip = add_entry(
            self.blocky2opt, label="mew", text='1', width=ewsmall,
            command=self.entered_y2, tooltip="Marker edge width")
        self.mew2frame.pack(side=tk.LEFT)
        # Quit button
        self.bquit = Button(self, text="Quit",
                            command=self.master.top.destroy)
        self.bquittip = add_tooltip(self.bquit, 'Quit dfvue')
        self.bquit.grid(row=18, column=8, sticky=tk.E)

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
            parent=self, title='Choose csv file(s)', multiple=True)

        if self.top.csvfile:
            self.top.newcsvfile = True
            self.new_df()

    def new_df(self):
        """
        Read new DataFrame.

        """
        self.top.df = pd.read_csv(self.top.csvfile[0], nrows=40)
        self.readcsvwin = dfvReadcsv(self.top, callback=self.reset)

    def next_y(self):
        """
        Command called if next button for the left-hand-side y-variable was
        pressed.

        Resets dimensions of left-hand-side y-variable.
        Redraws plot.

        """
        y = self.y.get()
        if ihavectk:
            cols = self.y.cget("values")
        else:
            cols = self.y["values"]
        idx = cols.index(y)
        idx += 1
        if idx < len(cols):
            self.y.set(cols[idx])
            self.redraw()

    def next_y2(self):
        """
        Command called if next button for the right-hand-side y-variable was
        pressed.

        Resets dimensions of right-hand-side y-variable.
        Redraws plot.

        """
        y2 = self.y2.get()
        if ihavectk:
            cols = self.y2.cget("values")
        else:
            cols = self.y2["values"]
        idx = cols.index(y2)
        idx += 1
        if idx < len(cols):
            self.y2.set(cols[idx])
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
        if ihavectk:
            cols = self.y.cget("values")
        else:
            cols = self.y["values"]
        idx = cols.index(y)
        idx -= 1
        if idx > 0:
            self.y.set(cols[idx])
            self.redraw()

    def prev_y2(self):
        """
        Command called if previous button for the right-hand-side
        y-variable was pressed.

        Resets dimensions of right-hand-side y-variable.
        Redraws plot.

        """
        y2 = self.y2.get()
        if ihavectk:
            cols = self.y2.cget("values")
        else:
            cols = self.y2["values"]
        idx = cols.index(y2)
        idx -= 1
        if idx > 0:
            self.y2.set(cols[idx])
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
            if ihavectk:
                self.x.configure(values=columns)
            else:
                self.x['values'] = columns
            self.x.set(x)
            y = self.y.get()
            if ihavectk:
                self.y.configure(values=columns)
            else:
                self.y['values'] = columns
            self.y.set(y)
            y2 = self.y2.get()
            if ihavectk:
                self.y2.configure(values=columns)
            else:
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
            tit = f"dfvue {self.top.csvfile}"
        else:
            tit = "dfvue"
        self.master.master.title(tit)
        # set variables
        columns = [''] + self.cols
        if ihavectk:
            self.x.configure(values=columns)
        else:
            self.x['values'] = columns
        self.x.set(columns[0])
        if ihavectk:
            self.y.configure(values=columns)
        else:
            self.y['values'] = columns
        self.y.set(columns[0])
        if ihavectk:
            self.y2.configure(values=columns)
        else:
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
