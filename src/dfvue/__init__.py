#!/usr/bin/env python
"""
Purpose
-------

dfvue is a minimal GUI for a quick view of csv files.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

Subpackages
-----------
.. autosummary::
   dfvmain
   dfvreadcsv
   dfvscatter
   dfvue
   dfvutils
   ncvwidgets

History
    * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)

"""
# version, author
try:
    from ._version import __version__
except ImportError:  # pragma: nocover
    # package is not installed
    __version__ = "0.0.0.dev0"
__author__  = "Matthias Cuntz"

# helper
# copy from idle
from .tooltip import TooltipBase, OnHoverTooltipBase, Hovertip

# general helper functions
from .dfvutils import clone_dfvmain, format_coord_scatter, list_intersection
from .dfvutils import vardim2var

# adding widgets with labels, etc.
from .ncvwidgets import callurl, Tooltip
from .ncvwidgets import add_checkbutton, add_combobox, add_entry, add_imagemenu
from .ncvwidgets import add_menu, add_scale, add_spinbox, add_tooltip
from .ncvwidgets import Treeview

# panels
# read csv window
from .dfvreadcsv import read_csvopts, read_csvdefaults, read_csvhelp
from .dfvreadcsv import dfvReadcsv

# scatter/line panel
from .dfvscatter import dfvScatter

# main window with panels
from .dfvmain import dfvMain

# main
from .dfvue import dfvue


__all__ = ['TooltipBase', 'OnHoverTooltipBase', 'Hovertip',
           'clone_dfvmain',
           'format_coord_scatter',
           'list_intersection', 'vardim2var',
           'Tooltip',
           'add_checkbutton', 'add_combobox', 'add_entry', 'add_imagemenu',
           'add_menu', 'add_scale', 'add_spinbox', 'add_tooltip',
           'Treeview',
           'read_csvopts', 'read_csvdefaults', 'read_csvhelp',
           'dfvReadcsv',
           'dfvScatter',
           'dfvMain',
           'dfvue',
           ]
