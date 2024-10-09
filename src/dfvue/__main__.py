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
   * Allow multiple input files, Oct 2024, Matthias Cuntz

"""
from dfvue import dfvue


def main():
    import argparse

    sep = ''
    index_col = None
    skiprows = None
    parse_dates = 'True'
    date_format = None
    missing_value = None
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description='A minimal GUI for a quick view of csv files.')
    hstr = 'Delimiter to use.'
    parser.add_argument('-s', '--sep', action='store', type=str,
                        default=sep, dest='sep',
                        metavar='separator', help=hstr)
    hstr = ('Column(s) to use as index, either given as column index'
            ' or string name.')
    parser.add_argument('-i', '--index_col', action='store', type=str,
                        default=index_col, dest='index_col',
                        metavar='columns', help=hstr)
    hstr = ('Line number(s) to skip (0-indexed, must include comma,'
            ' e.g. "1," for skipping the second row) or\n'
            'number of lines to skip (int, without comma) at the start'
            ' of the file.')
    parser.add_argument('-k', '--skiprows', action='store', type=str,
                        default=skiprows, dest='skiprows',
                        metavar='rows', help=hstr)
    hstr = ('boolean, if True -> try parsing the index.\n'
            'list of int or names, e.g. 1,2,3\n'
            '    -> try parsing columns 1, 2, and 3 each as a separate date'
            ' column.\n'
            'list of lists, e.g. [1,3]\n'
            '    -> combine columns 1 and 3 and parse as a single date'
            ' column.\n'
            'dict, e.g. "foo":[1,3]\n'
            '    -> parse columns 1 and 3 as date and call result "foo"')
    parser.add_argument('-p', '--parse_dates', action='store', type=str,
                        default=parse_dates, dest='parse_dates',
                        metavar='bool/list/dict', help=hstr)
    hstr = ('Will parse dates according to this format.\n'
            'For example: "%%Y-%%m-%%d %%H:%%M%%S". See\n'
            'https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior')
    parser.add_argument('-d', '--date_format', action='store', type=str,
                        default=date_format, dest='date_format',
                        metavar='format_string', help=hstr)
    hstr = ('Missing or undefined value set to NaN.\n'
            'For negative values, use long format, e.g. --missing_value=-9999.')
    parser.add_argument('-m', '--missing_value', action='store', type=str,
                        default=missing_value, dest='missing_value',
                        metavar='missing_value', help=hstr)
    parser.add_argument('csvfile', nargs='*', default=None,
                        metavar='csv_file(s)',
                        help='Delimited text file(s)')

    args = parser.parse_args()
    sep = args.sep
    index_col = args.index_col
    skiprows = args.skiprows
    parse_dates = args.parse_dates
    date_format = args.date_format
    missing_value = args.missing_value
    csvfile = args.csvfile

    del parser, args

    # This must be before any other call to matplotlib
    # because it uses the TkAgg backend.
    # This means, do not use --pylab with ipython.
    dfvue(csvfile=csvfile, sep=sep, index_col=index_col, skiprows=skiprows,
          parse_dates=parse_dates, date_format=date_format,
          missing_value=missing_value)


if __name__ == "__main__":
    main()
