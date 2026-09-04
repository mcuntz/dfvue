#!/usr/bin/env python
"""
Widget functions for Qt framework with PySide6

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2020- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   add_checkbox
   add_combobox
   add_label
   add_lineedit
   add_pushbutton
   add_table

History
   * Written Nov-Dec 2020 by Matthias Cuntz (mc (at) macu (dot) de)
   * Added tooltips to all widgets with class Tooltip,
     Jan 2021, Matthias Cuntz
   * Added add_tooltip widget, Jan 2021, Matthias Cuntz
   * add_spinbox returns also label widget, Jan 2021, Matthias Cuntz
   * padlabel for add_entry to add space to previous widget,
     Jul 2023, Matthias Cuntz
   * labelwidth for add_entry to align columns with pack,
     Jul 2023, Matthias Cuntz
   * Replace tk constants with strings such as tk.LEFT with 'left',
     Jul 2023, Matthias Cuntz
   * Use Hovertip from local copy of tooltip.py, Jul 2023, Matthias Cuntz
   * Added Treeview class with optional horizontal and vertical scroolbars,
     Jul 2023, Matthias Cuntz
   * Added callurl function, Dec 2023, Matthias Cuntz
   * Use CustomTkinter, Jun 2024, Matthias Cuntz
   * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz
   * Small bugfix in Combobox if no CustomTkinter, Nov 2024, Matthias Cuntz
   * Pass width to Checkbutton if CustomTkinter, Dec 2024, Matthias Cuntz
   * Pass padx for space between label and combobox, Dec 2024, Matthias Cuntz
   * Use CustomTkinter also in add_menu and add_scale,
     Dec 2024, Matthias Cuntz
   * Bugfix: did not make new frame in add_spinbox, Dec 2024, Matthias Cuntz
   * add_button, add_label, Feb 2025, Matthias Cuntz
   * Default delay for tooltips from 1 s to 0.5 s, Mar 2025, Matthias Cuntz
   * Use Qt framework with PySide6, Aug 2026, Matthias Cuntz
   * Remove add_checkbox, add_combobox, add_entry, add_imagemenu, add_label,
     add_menu, add_scale, add_spinbox, add_tooltip, Treeview
   * Add add_checkbox, add_combobox, add_label, add_lineedit, add_pushbutton,
     add_table for Qt framework with PySide6, Aug 2026, Matthias Cuntz
   * Add mplCanvas, Aug 2026, Matthias Cuntz
   * Rename file to vuewidgets.py, Aug 2026, Matthias Cuntz

"""
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel
from PySide6.QtWidgets import QLineEdit, QPushButton, QSizePolicy
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


__all__ = ['mplCanvas',
           'add_checkbox', 'add_combobox', 'add_label',
           'add_lineedit', 'add_pushbutton', 'add_table']


class mplCanvas(FigureCanvas):
    """
    Matplotlib Qt figure canvas with left (axes) and right axes (axes2)

    Parameters
    ----------
    width : float, optional
        Figure width (default: 1)
    height : float, optional
        Figure height (default: 1)
    **kwargs : dict, optional
        All other keyword arguments are passed to Figure

    Returns
    -------
    matplotlib.backends.backend_qtagg.FigureCanvas

    """

    def __init__(self, width=1, height=1, **kwargs):

        self.fig = Figure(facecolor='white', figsize=(width, height),
                          **kwargs)
        self.axes = self.fig.add_subplot(111)
        self.axes2 = self.axes.twinx()
        self.axes2.yaxis.set_label_position('right')
        self.axes2.yaxis.tick_right()

        super().__init__(self.fig)


def add_checkbox(layout, label='', value=False, command=None,
                 tooltip='', alignment=None, **kwargs):
    """
    Add a QCheckBox.

    Parameters
    ----------
    layout : QLayout
        Parent layout
    label : str, optional
        Text that appears on the checkbox (default: '')
    value : bool, optional
        Initial state of the checkbutton (default: False)
    command : function, optional
        Function to be called whenever the state of the
        checkbutton changes (default: None).
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the checkbutton (default: '' = no tooltip)
    alignment : Qt.Alignment, optional
        Alignment passed to layout.addWidget
        (default: None = Default(Qt.Alignment))
    **kwargs : option=value pairs, optional
        All other options will be passed to QCheckBox

    Returns
    -------
    QCheckBox

    Examples
    --------
    >>>

    """
    if label:
        icheck = QCheckBox(text=label, **kwargs)
    else:
        icheck = QCheckBox(**kwargs)

    if value:
        icheck.setChecked()

    if command is not None:
        icheck.checkStateChanged.connect(command)

    if tooltip:
        icheck.setToolTip(tooltip)

    icheck.setSizePolicy(QSizePolicy.Policy.Preferred,
                         QSizePolicy.Policy.Fixed)

    akwargs = {}
    if alignment is not None:
        akwargs.update({'alignment': alignment})
    layout.addWidget(icheck, **akwargs)

    return icheck


def add_combobox(layout, label='', values=[], command=None, tooltip='',
                 alignment=None, **kwargs):
    """
    Add a QComboBox

    Parameters
    ----------
    layout : QLayout
        Parent layout
    label : str, optional
        Label text that appears on the button (default: '')
    command : function, optional
        Function connected to QPushButton.clicked
        (default: None = no action on click)
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the checkbutton (default: '' = no tooltip)
    alignment : Qt.Alignment, optional
        Alignment passed to layout.addWidget
        (default: None = Default(Qt.Alignment))
    **kwargs : option=value pairs, optional
        All other options will be passed to QComboBox

    Returns
    -------
    QPushButton
        widget

    Examples
    --------
    >>>

    """
    if label:
        ilabel = QLabel(label)
        fm = ilabel.fontMetrics()
        iwidth = fm.size(0, label)
        ilabel.setMinimumWidth(iwidth.width())
        # ilabel.setMaximumWidth(iwidth.width())
    else:
        ilabel = None

    icombo = QComboBox(**kwargs)
    if len(values) > 0:
        icombo.addItems(values)

    if command is not None:
        icombo.currentIndexChanged.connect(command)

    if tooltip:
        icombo.setToolTip(tooltip)

    if label:
        ilabel.setSizePolicy(QSizePolicy.Policy.Preferred,
                             QSizePolicy.Policy.Fixed)

    icombo.setSizePolicy(QSizePolicy.Policy.Preferred,
                         QSizePolicy.Policy.Fixed)

    akwargs = {}
    if alignment is not None:
        akwargs.update({'alignment': alignment})
    if alignment == Qt.AlignmentFlag.AlignRight:
        layout.addWidget(icombo, **akwargs)
        if label:
            layout.addWidget(ilabel, **akwargs)
    else:
        if label:
            layout.addWidget(ilabel, **akwargs)
        layout.addWidget(icombo, **akwargs)

    return ilabel, icombo


def add_label(layout, text='', alignment=None, **kwargs):
    """
    Add a QLabel

    Parameters
    ----------
    layout : QLayout
        Parent layout
    text : str, optional
        Text that appears as textvariable in the label (default: '')
    alignment : Qt.Alignment, optional
        Alignment passed to layout.addWidget
        (default: None = Default(Qt.Alignment))
    **kwargs : option=value pairs, optional
        All other options will be passed to QLabel

    Returns
    -------
    QLabel

    Examples
    --------
    >>> 

    """
    ilabel = QLabel(text)
    # fm = ilabel.fontMetrics()
    # if text:
    #     iwidth = fm.size(0, text)
    # else:
    #     iwidth = fm.size(0, ' ')
    # ilabel.setMinimumWidth(iwidth.width())
    # ilabel.setMaximumWidth(iwidth.width())

    ilabel.setSizePolicy(QSizePolicy.Policy.Preferred,
                         QSizePolicy.Policy.Fixed)

    akwargs = {}
    if alignment is not None:
        akwargs.update({'alignment': alignment})
    layout.addWidget(ilabel, **akwargs)

    return ilabel


def add_lineedit(layout, label='', text='', command=None, tooltip='',
                 alignment=None, labelwidth=None, **kwargs):
    """
    Add a QLineEdit

    Parameters
    ----------
    layout : QLayout
        Parent layout
    label : str, optional
        Text that appears in front of the entry (default: "")
    text : str, optional
        Initial text in the entry area (default: "")
    command : function or list of functions, optional
        Handler function to be bound to the entry for the events
        'textChanged()', 'textEdited()', 'returnPressed()', and
        'editingFinished()'
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the entry (default: "" = no tooltip)
    alignment : Qt.Alignment, optional
        Alignment passed to layout.addWidget
        (default: None = Default(Qt.Alignment))
    labelwidth : int, optional
        If given, set width of Label
    **kwargs : option=value pairs, optional
        All other options will be passed to QLineEdit

    Returns
    -------
    QLineEdit

    Examples
    --------
    >>> self.rowxyopt = Frame(self)
    >>> self.rowxyopt.pack(side='top', fill='x')
    >>> self.lslbl, self.ls = add_entry(
    ...     self.rowxyopt, label="ls", text='-',
    ...     width=4, command=self.selected_y)

    """
    ilabel = QLabel(label)
    fm = ilabel.fontMetrics()
    if label:
        iwidth = fm.size(0, label)
    else:
        iwidth = fm.size(0, ' ')
    ilabel.setMinimumWidth(iwidth.width())
    # ilabel.setMaximumWidth(iwidth.width())

    iline = QLineEdit(**kwargs)
    if len(text) > 0:
        iline.setText(text)

    if command is not None:
        iline.editingFinished.connect(command)
        iline.returnPressed.connect(command)
        # iline.textChanged.connect(command)
        # iline.textEdited.connect(command)
        
    if tooltip:
        iline.setToolTip(tooltip)

    ilabel.setSizePolicy(QSizePolicy.Policy.Preferred,
                         QSizePolicy.Policy.Fixed)

    iline.setSizePolicy(QSizePolicy.Policy.Preferred,
                         QSizePolicy.Policy.Fixed)

    akwargs = {}
    if alignment is not None:
        akwargs.update({'alignment': alignment})
    if alignment == Qt.AlignmentFlag.AlignRight:
        layout.addWidget(iline, **akwargs)
        layout.addWidget(ilabel, **akwargs)
    else:
        layout.addWidget(ilabel, **akwargs)
        layout.addWidget(iline, **akwargs)

    return ilabel, iline


def add_pushbutton(layout, text='', command=None, tooltip='',
                   alignment=None, **kwargs):
    """
    Add a QPushButton

    Parameters
    ----------
    layout : QLayout
        Parent layout
    text : str, optional
        Text that appears on the button (default: '')
    command : function, optional
        Function connected to QPushButton.clicked
        (default: None = no action on click)
    tooltip : str, optional
        Tooltip appearing after one second when hovering over
        the checkbutton (default: '' = no tooltip)
    alignment : Qt.Alignment, optional
        Alignment passed to layout.addWidget
        (default: None = Default(Qt.Alignment))
    **kwargs : option=value pairs, optional
        All other options will be passed to QPushButton

    Returns
    -------
    QPushButton
        widget

    Examples
    --------
    >>> self.rowzxy = QHBoxLayout()
    >>> self.inv_x = add_pushbutton(
    ...     self.rowzxy, "invert x", command=self.checked,
    ...     tooltip='Press button to invert the x-axis.')

    """
    ibutton = QPushButton(text, **kwargs)

    if command is not None:
        ibutton.clicked.connect(command)

    if tooltip:
        ibutton.setToolTip(tooltip)

    # QPushButton is already fixed
    # ibutton.setSizePolicy(QSizePolicy.Policy.Preferred,
    #                       QSizePolicy.Policy.Fixed)

    akwargs = {}
    if alignment is not None:
        akwargs.update({'alignment': alignment})
    layout.addWidget(ibutton, **akwargs)

    return ibutton


def add_table(layout, df=None, **kwargs):
    """
    Add a QTableWidget from a pandas.DataFrame

    Parameters
    ----------
    layout : QLayout
        Parent layout
    df : pandas.DataFrame, optional
        pandas DataFrame to display. If None, create 4*5 empty cells (default: None)
    **kwargs : option=value pairs, optional
        All other options will be passed to QTableWidget

    Returns
    -------
    QTableWidget

    Examples
    --------
    >>> 

    """
    if df is None:
        nrows = 4
        ncols = 5
        columns = [ f'Column {i:03d}' for i in range(ncols) ]
        dat = [ [''] * ncols for i in range(nrows) ]
        df = pd.DataFrame(dat, columns=columns)
    nrows = df.shape[0]
    ncols = df.shape[1]

    columns = [ f'{ii}: {cc}' for ii, cc in enumerate(list(df.columns)) ]

    idx = 'index'
    if df.index.name is not None:
        idx = 'index ' + df.index.name

    itable = QTableWidget()
    itable.setRowCount(nrows)
    itable.setColumnCount(ncols + 1)
    itable.setHorizontalHeaderLabels([idx] + columns)

    for i in range(nrows):
        item = QTableWidgetItem(str(df.index[i]))
        itable.setItem(i, 0, item)
        for k, cc in enumerate(df.columns):
            item = QTableWidgetItem(str(df[cc].iloc[i]))
            itable.setItem(i, k + 1, item)

    # itable.setSizePolicy(QSizePolicy.Policy.Preferred,
    #                      QSizePolicy.Policy.Fixed)

    layout.addWidget(itable)

    return itable
