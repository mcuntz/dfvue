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
    * Moved to customtkinter, Jun 2024, Matthias

"""
import tkinter as tk
import customtkinter as ctk
from .dfvscatter import dfvScatter


__all__ = ['dfvMain']


#
# Window with plot panels
#

class dfvMain(ctk.CTkTabview):
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

        stab = 'Scatter/Line'
        self.add(stab)
        itab = self.tab(stab)
        itab.name   = self.name
        itab.master = self.master
        itab.top    = self.top
        self.tab_scatter = dfvScatter(itab)
        self.tab_scatter.grid(sticky=tk.W + tk.E + tk.S + tk.N)
