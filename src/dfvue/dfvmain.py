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
   * Back to pack layout manager for resizing, Nov 2024, Matthias Cuntz
   * Use Qt framework with PySide6, Aug 2026, Matthias Cuntz

"""
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMainWindow, QTabWidget
from .dfvscatter import dfvScatter


__all__ = ['dfvMain']


#
# Window with plot panels
#

class dfvMain(QMainWindow):
    """
    Main dfvue tabbed window with the plotting panels.

    """

    def __init__(self, top, **kwargs):

        super().__init__(**kwargs)

        self.top = top
        self.name = 'dfvOne'
        
        if self.top.os == 'Darwin':
            self.setUnifiedTitleAndToolBarOnMac(True)

        if self.top.csvfile[0]:
            tit = f"dfvue {self.top.csvfile}"
        else:
            tit = QCoreApplication.applicationName()
        self.setWindowTitle(tit)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        # self.tabs.setMovable(True)

        self.tabs.addTab(dfvScatter(self), 'Scatter/Line')

        self.setCentralWidget(self.tabs)

        self.tabs.show()
