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
    * Use CustomTkinter, Jun 2024, Matthias Cuntz
    * Use mix of grid and pack layout manager, Jun 2024, Matthias Cuntz
    * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz

"""
import tkinter as tk
import tkinter.ttk as ttk
try:
    from customtkinter import CTkTabview as Frame
    ihavectk = True
except ModuleNotFoundError:
    from tkinter.ttk import Frame
    ihavectk = False
from .dfvscatter import dfvScatter


__all__ = ['dfvMain']


#
# Window with plot panels
#

class dfvMain(Frame):
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

        self.name   = 'dfvMain'
        self.master = master      # master window, i.e. root
        self.top    = master.top  # top window

        if ihavectk:
            stab = 'Scatter/Line'
            self.add(stab)
            itab = self.tab(stab)
            itab.name   = self.name
            itab.master = self.master
            itab.top    = self.top
            self.tab_scatter = dfvScatter(itab)
            self.tab_scatter.grid(sticky=tk.W + tk.E + tk.S + tk.N)
        else:
            # Notebook for tabs for future plot types
            self.tabs = ttk.Notebook(self)
            self.tabs.grid(sticky=tk.W + tk.E + tk.S + tk.N)
            self.tab_scatter = dfvScatter(self)
            self.tabs.add(self.tab_scatter, text=self.tab_scatter.name)
