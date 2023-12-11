#!/usr/bin/env python
"""
Main dfvue window.

This sets up the main notebook window with the plotting panels.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   dfvMain

History
    * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)

"""
import tkinter as tk
import tkinter.ttk as ttk
from .dfvscatter import dfvScatter


__all__ = ['dfvMain']


#
# Window with plot panels
#

class dfvMain(ttk.Frame):
    """
    Main dfvue notebook window with the plotting panels.

    Sets up the notebook layout with the panels.

    Contains the method to check if csv file has changed.

    """

    #
    # Window setup
    #

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=tk.BOTH, expand=1)

        self.name   = 'dfvMain'
        self.master = master      # master window, i.e. root
        self.top    = master.top  # top window

        # Notebook for tabs for future plot types
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tab_scatter = dfvScatter(self)

        self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)

        # self.tabs.bind("<<NotebookTabChanged>>", self.check_new_csv)
        # self.tabs.bind("<Enter>", self.check_new_csv)

    # #
    # # Methods
    # #

    # def check_new_csv(self, event):
    #     """
    #     Command called if notebook panel changed or mouse pointer enters a
    #     window. It checks if csv file was changed in any panel of any window
    #     and re-initialises all plot panels (of the current window).
    #     """
    #     ido = False
    #     if ( (self.tab_scatter.top.df is None) and
    #          (self.tab_scatter.df is None) ):
    #         ido = False
    #     elif ((self.tab_scatter.top.df is None) or
    #           (self.tab_scatter.df is None)):
    #         ido = True
    #     elif (not self.tab_scatter.df.equals(self.tab_scatter.top.df)):
    #         ido = True
    #     elif (not self.tab_scatter.top.df.equals(self.tab_scatter.df)):
    #         ido = True

    #     if ido:
    #         self.tab_scatter.reinit()
    #         self.tab_scatter.redraw()
