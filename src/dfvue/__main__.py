#!/usr/bin/env python
"""
usage: dfvue [-h] [-m missing_value] [csv_file]

A minimal GUI for a quick view of csv files.

positional arguments:
  csv_file              Delimited text file

optional arguments:
  -h, --help            show this help message and exit
  -m missing_value, --miss missing_value
                        Missing or undefined value set to NaN.
                        For negative values, use for example --miss=-9999.


Example command line:
    dfvue meteo_DB1_2020.csv

:copyright: Copyright 2023- Matthias Cuntz, see AUTHORS.rst for details.
:license: MIT License, see LICENSE for details.

History
    * Written Jul 2023 2023 by Matthias Cuntz (mc (at) macu (dot) de)

"""
import numpy as np
from dfvue import dfvue


def main():
    import argparse

    miss = None
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='A minimal GUI for a quick view of csv files.')
    hstr = ('Missing or undefined value set to NaN.'
            ' For negative values, use for example --miss=-9999.')
    parser.add_argument('-m', '--miss', action='store', type=float,
                        default=miss, dest='miss',
                        metavar='missing_value', help=hstr)
    parser.add_argument('csvfile', nargs='*', default=None,
                        metavar='csv_file',
                        help='Delimited text file')

    args = parser.parse_args()
    miss = args.miss
    csvfile = args.csvfile

    del parser, args

    if len(csvfile) > 0:
        csvfile = csvfile[0]
    else:
        csvfile = ''

    # This must be before any other call to matplotlib
    # because it uses the TkAgg backend.
    # This means, do not use --pylab with ipython.
    dfvue(csvfile=csvfile, miss=miss)


if __name__ == "__main__":
    main()
