#!/usr/bin/env python
"""
Text widget for manipulation of DataFrame

This text widget allows putting in code to manipulate the current data frame.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   dfvTransform

History
   * Written Oct 2024 by Matthias Cuntz (mc (at) macu (dot) de)
   * Use dfvScreen for window sizes, Nov 2025, Matthias Cuntz
   * Use set_window_geometry from dfvScreen, Nov 2025, Matthias Cuntz
   * Use Qt framework with PySide6, Aug 2026, Matthias Cuntz

"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QTextEdit, QVBoxLayout, QWidget
from .dfvutils import transform_window_size
from .vuewidgets import add_pushbutton


__all__ = ['dfvTransform']


class dfvTransform(QWidget):
    """
    Window for reading Python code to change DataFrame.

    """

    #
    # Setup panel
    #

    def __init__(self, master, **kwargs):

        super().__init__(**kwargs)

        self.name = 'dfvTransform'

        self.master = master
        self.top = master.top
        self.df = self.top.df
        
        self.setWindowTitle("Manipulate DataFrame")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # text window
        self.text_edit = QTextEdit()
        # self.setCentralWidget(self.text_edit)

        self.text_edit.setPlainText(
            '# Example daily mean if datetime index\n'
            'import numpy as np\n'
            'self.df = self.df.resample("1D").mean().squeeze()'
        )
        
        layout.addWidget(self.text_edit)

        # cancel and transform buttons
        self.rowdone = QHBoxLayout()
        self.rowdone.setContentsMargins(3, 0, 3, 10)  # left, top, tight, bottom
        self.rowdone.setSpacing(3)

        self.rowdone.addStretch()

        self.icancel = add_pushbutton(
            self.rowdone, text='Cancel', command=self.cancel,
            tooltip='Cancel DataFrame manipulation',
            alignment=Qt.AlignmentFlag.AlignRight)

        self.done = add_pushbutton(
            self.rowdone, text='Transform', command=self.exec_text,
            tooltip='Execute DataFrame manipulations',
            alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(self.rowdone)

        if len(self.top.screen) == 0:
            screen = self.screen().availableGeometry()
            self.top.screen = (screen.width(), screen.height())
        xs, ys, xo, yo = transform_window_size(self.top.screen)
        self.resize(xs, ys)
        self.move(xo, yo)

        self.setLayout(layout)
        self.show()

    #
    # Event bindings
    #

    def cancel(self):
        self.close()

    def exec_text(self):
        tt = self.text_edit.toPlainText()
        _ = exec(tt)

        self.master.top.df = self.df
        self.master.resetvars(nosort=True)
        self.master.redraw()

        self.close()
