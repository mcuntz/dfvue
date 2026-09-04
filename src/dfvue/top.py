#!/usr/bin/env python3
"""
Pass around current state

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2026- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following functions are provided:

.. autosummary::
   TopState

History
   * Written Jul 2026 by Matthias Cuntz (mc (at) macu (dot) de)

"""
from dataclasses import dataclass, field
import pandas as pd


__all__ = ['topState']


@dataclass
class topState:
    #
    # operating system
    os: str = ""
    screen: tuple = ()
    # app icon
    icon: str = ""
    # file name(s) or file handle(s)
    csvfile: list[str] = field(default_factory=list)
    # new file after command line
    newcsvfile: bool = False
    # pandas DataFrame or csvfile
    df: pd.DataFrame = field(default_factory=pd.DataFrame)
    # column description strings
    cols: list[str] = field(default_factory=list)
    #
    # command line options
    sep: str = ""
    index_col: int = -1
    skiprows: int = -1
    parse_dates: bool = True
    date_format: str = ""
    missing_value: float = None
