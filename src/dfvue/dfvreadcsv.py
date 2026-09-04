#!/usr/bin/env python
"""
Scatter/Line panel of dfvue.

The panel allows plotting variables against time or two variables against
each other. A second variable can be plotted in the same graph using the
right-hand-side y-axis.

This module was written by Matthias Cuntz while at Institut National de
Recherche pour l'Agriculture, l'Alimentation et l'Environnement (INRAE), Nancy,
France.

:copyright: Copyright 2023- Matthias Cuntz - mc (at) macu (dot) de
:license: MIT License, see LICENSE for details.

.. moduleauthor:: Matthias Cuntz

The following classes are provided:

.. autosummary::
   read_csvopts
   read_csvdefaults
   read_csvhelp
   dfvReadcsv

History
   * Written Jul 2023 by Matthias Cuntz (mc (at) macu (dot) de)
   * Use CustomTkinter, Jun 2024, Matthias Cuntz
   * Use mix of grid and pack layout manager, Jun 2024, Matthias Cuntz
   * Use CustomTkinter only if installed, Jun 2024, Matthias Cuntz
   * Concat multiple input files, Oct 2024, Matthias Cuntz
   * Add low_memory to read_csvopts, Jan 2025, Matthias Cuntz
   * Keep na_values as str, Jan 2025, Matthias Cuntz
   * Moved parse_entry to dfvutils, Jan 2025, Matthias Cuntz
   * Move new window to the left, Jul 2025, Matthias Cuntz
   * Focus on first option upon calling, Jul 2025, Matthias Cuntz
   * Use dfvScreen for window sizes, Nov 2025, Matthias Cuntz
   * Use set_window_geometry from dfvScreen, Nov 2025, Matthias Cuntz
   * Catch ParseError of pandas.read_csv, Aug 2026, Matthias Cuntz
   * Use Qt framework with PySide6, Aug 2026, Matthias Cuntz

"""
from collections.abc import Iterable
import warnings
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtWidgets import QLabel, QLineEdit
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from .dfvutils import parse_entry, readcsv_window_size
from .vuewidgets import add_label, add_table
from .vuewidgets import add_pushbutton


__all__ = ['read_csvopts', 'read_csvdefaults', 'read_csvhelp',
           'dfvReadcsv']

read_csvopts = ['sep', 'index_col', 'usecols', 'skiprows', 'nrows',
                'parse_dates', 'date_format',
                'header', 'names',
                'na_filter', 'na_values', 'keep_default_na',
                'true_values', 'false_values',
                'skip_blank_lines', 'skipinitialspace',
                'comment', 'skipfooter',
                'thousands', 'decimal', 'lineterminator',
                'quotechar', 'doublequote',
                'dayfirst', 'encoding', 'low_memory'
                ]
read_csvopts.append('missing_value')
"""
pandas.read_csv options provided in form in the given order

"""

read_csvdefaults = {'sep': '', 'header': 'infer',
                    'names': '', 'index_col': None, 'usecols': None,
                    'dtype': None, 'engine': None, 'converters': None,
                    'true_values': None, 'false_values': None,
                    'skipinitialspace': False, 'skiprows': None,
                    'skipfooter': 0, 'nrows': None, 'na_values': None,
                    'keep_default_na': True, 'na_filter': True,
                    'verbose': False, 'skip_blank_lines': True,
                    'parse_dates': True,
                    'date_format': None, 'dayfirst': False,
                    'cache_dates': True, 'iterator': False,
                    'chunksize': None, 'compression': 'infer',
                    'thousands': None, 'decimal': '.', 'lineterminator': None,
                    'quotechar': '"', 'quoting': 0, 'doublequote': True,
                    'escapechar': None, 'comment': None, 'encoding': None,
                    'encoding_errors': 'strict', 'dialect': None,
                    'on_bad_lines': 'error', 'delim_whitespace': False,
                    'low_memory': True, 'memory_map': False,
                    'float_precision': None, 'storage_options': None}
read_csvdefaults.update({'missing_value': None})
"""
pandas.read_csv options defaults

"""

read_csvhelp = {
    'file':
    r"""str, path object or file-like object
    Any valid string path is acceptable.
    The string could be a URL. Valid URL schemes include http, ftp, s3, gs,
and file. For file URLs, a host is expected.
    A local file could be: file://localhost/path/to/table.csv.
    If you want to pass in a path object, pandas accepts any os.PathLike.
    By file-like object, we refer to objects with a read() method, such as
a file handle (e.g. via builtin open function) or StringIO.""",
    'sep':
    r"""str, default: ,
    Delimiter to use.
    If sep is None, the C engine cannot automatically detect the separator,
but the Python parsing engine can, meaning the latter will be used and
automatically detect the separator by Python's builtin sniffer tool,
csv.Sniffer.
    In addition, separators longer than 1 character and different from '\s+'
will be interpreted as regular expressions and will also force the use of the
Python parsing engine.
    Note that regex delimiters are prone to ignoring quoted data.
    Regex example: '\r\t'.""",
    'header':
    """int, list of int, None, default: infer
    Row number(s) to use as the column names, and the start of the data.
    Default behavior is to infer the column names: if no names are passed the
behavior is identical to header=0 and column names are inferred from the first
line of the file, if column names are passed explicitly then the behavior is
identical to header=None.
    Explicitly pass header=0 to be able to replace existing names. The header
can be a list of integers that specify row locations for a multi-index on the
columns e.g. 0,1,3. Intervening rows that are not specified will be skipped
(e.g. 2 in this example is skipped).
    Note that this parameter ignores commented lines and empty lines if
skip_blank_lines=True, so header=0 denotes the first line of data rather than
the first line of the file.""",
    'names':
    """array-like, optional
    List of column names to use.
    If the file contains a header row, then you should explicitly pass
header=0 to override the column names.
    Duplicates in this list are not allowed.""",
    'index_col':
    """int, str, sequence of int / str, or False, optional, default: None
    Column(s) to use as the row labels of the DataFrame, either given as
string name (without column index) or column index.
    If a sequence of int / str is given, a MultiIndex is used. dfvue converts
a MultiIndex to a single string index with blanks.
    Note: index_col=False can be used to force pandas to not use the first
column as the index, e.g. when you have a malformed file with delimiters at
the end of each line.""",
    'usecols':
    """list-like or callable, optional
    Return a subset of the columns.
    If list-like, all elements must either be positional (i.e. integer indices
into the document columns) or strings that correspond to column names provided
either by the user in names or inferred from the document header row(s).
    If names are given, the document header row(s) are not taken into account.
For example, a valid list-like usecols parameter would be 0, 1, 2 or
'foo', 'bar', 'baz'.
    Element order is ignored, so usecols=[0, 1] is the same as [1, 0].
    To instantiate a DataFrame from data with element order preserved use
pd.read_csv(data, usecols=['foo', 'bar'])[['foo', 'bar']]
for columns in ['foo', 'bar'] order or
pd.read_csv(data, usecols=['foo', 'bar'])[['bar', 'foo']]
for ['bar', 'foo'] order.
    If callable, the callable function will be evaluated against the column
names, returning names where the callable function evaluates to True. An
example of a valid callable argument would be
lambda x: x.upper() in ['AAA', 'BBB', 'DDD'].
Using this parameter results in much faster parsing time and lower memory
usage.""",
    'dtype':
    """Type name or dict of column -> type, optional
    Data type for data or columns.
    E.g. 'a': np.float64, 'b': np.int32, 'c': 'Int64'
    Use str or object together with suitable na_values settings to preserve and
not interpret dtype.
    If converters are specified, they will be applied INSTEAD of dtype
conversion.""",
    'engine':
    """{'c', 'python', 'pyarrow'}, optional
    Parser engine to use.
    The C and pyarrow engines are faster, while the python engine is currently
more feature-complete. Multithreading is currently only supported by the
pyarrow engine.""",
    'converters':
    """dict, optional
    Dict of functions for converting values in certain columns.
    Keys can either be integers or column labels.""",
    'true_values':
    """list, optional
    Values to consider as True in addition to case-insensitive variants
of 'True'.""",
    'false_values':
    """list, optional
    Values to consider as False in addition to case-insensitive variants
of 'False'.""",
    'skipinitialspace':
    """bool, default: False
    Skip spaces after delimiter.""",
    'skiprows':
    """list-like, int or callable, optional
    Line numbers to skip (0-indexed, must include comma, e.g. 1, for skipping
the second row) or number of lines to skip (int, without comma) at the start of
the file.
    If callable, the callable function will be evaluated against the row
indices, returning True if the row should be skipped and False otherwise.
An example of a valid callable argument would be lambda x: x in [0, 2].""",
    'skipfooter':
    """int, default: 0
    Number of lines at bottom of file to skip
(Unsupported with engine='c').""",
    'nrows':
    """int, optional
    Number of rows of file to read.
    Useful for reading pieces of large files.""",
    'na_values':
    """scalar, str, list-like, or dict, optional
    Additional strings to recognize as NA/NaN.
    If dict passed, specific per-column NA values.
    By default the following values are interpreted as NaN:
'', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan',
'1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 'NaN', 'None', 'n/a',
'nan', 'null'.""",
    'keep_default_na':
    """bool, default: True
    Whether or not to include the default NaN values when parsing the data.
    Depending on whether na_values is passed in, the behavior is as follows:
        If keep_default_na is True, and na_values are specified,
na_values is appended to the default NaN values used for parsing.
        If keep_default_na is True, and na_values are not specified,
only the default NaN values are used for parsing.
        If keep_default_na is False, and na_values are specified,
only the NaN values specified na_values are used for parsing.
        If keep_default_na is False, and na_values are not specified,
no strings will be parsed as NaN.
    Note that if na_filter is passed in as False, the keep_default_na and
na_values parameters will be ignored.""",
    'na_filter':
    """bool, default: True
    Detect missing value markers (empty strings and the value of na_values).
    In data without any NAs, passing na_filter=False can improve the
performance of reading a large file.""",
    'verbose':
    """bool, default: False
    Indicate number of NA values placed in non-numeric columns.""",
    'skip_blank_lines':
    """bool, default: True
    If True, skip over blank lines rather than interpreting as NaN values.""",
    'parse_dates':
    """bool or list of int or names or list of lists or dict, default: False
    The behavior is as follows:
        boolean. If True -> try parsing the index.
        list of int or names. e.g. If 1, 2, 3
-> try parsing columns 1, 2, 3 each as a separate date column.
        list of lists. e.g. If [1, 3]
-> combine columns 1 and 3 and parse as a single date column.
        dict, e.g. 'foo' : [1, 3]
-> parse columns 1, 3 as date and call result 'foo'
    If a column or index cannot be represented as an array of datetimes,
say because of an unparsable value or a mixture of timezones, the column or
index will be returned unaltered as an object data type. For non-standard
datetime parsing, use pd.to_datetime after pd.read_csv.
    Note: A fast-path exists for iso8601-formatted dates.""",
    'date_format':
    """str or dict of column -> format, default: None
    If used in conjunction with parse_dates, will parse dates according to
this format.
    For anything more complex, please read in as object and then apply
to_datetime() as-needed.""",
    'dayfirst':
    """bool, default: False
    DD/MM format dates, international and European format.""",
    'cache_dates':
    """bool, default: True
    If True, use a cache of unique, converted dates to apply the datetime
conversion.
    May produce significant speed-up when parsing duplicate date strings,
especially ones with timezone offsets.""",
    'iterator':
    """bool, default: False
    Return TextFileReader object for iteration or getting chunks
with get_chunk().""",
    'chunksize':
    """int, optional
    Return TextFileReader object for iteration.
    See the IO Tools docs for more information on iterator and chunksize.""",
    'compression':
    """str or dict, default: 'infer'
    For on-the-fly decompression of on-disk data.
    If 'infer' and 'filepath_or_buffer' is path-like, then detect compression
from the following extensions:
'.gz', '.bz2', '.zip', '.xz', '.zst', '.tar', '.tar.gz', '.tar.xz' or
'.tar.bz2' (otherwise no compression).
    If using 'zip' or 'tar', the ZIP file must contain only one data file to
be read in.
    Set to None for no decompression.
    Can also be a dict with key 'method' set to one of
{'zip', 'gzip', 'bz2', 'zstd', 'tar'} and other key-value pairs are forwarded
to zipfile.ZipFile, gzip.GzipFile, bz2.BZ2File, zstandard.ZstdDecompressor or
tarfile.TarFile, respectively. As an example, the following could be passed for
Zstandard decompression using a custom compression dictionary:
compression={'method': 'zstd', 'dict_data': my_compression_dict}.""",
    'thousands':
    """str, optional
    Thousands separator.""",
    'decimal':
    """str, default: '.'
    Character to recognize as decimal point
(e.g. use ',' for European data).""",
    'lineterminator':
    """str (length 1), optional
    Character to break file into lines. Only valid with C parser.""",
    'quotechar':
    """str (length 1), optional
    The character used to denote the start and end of a quoted item.
    Quoted items can include the delimiter and it will be ignored.""",
    'quoting':
    """int or csv.QUOTE_* instance, default: 0
    Control field quoting behavior per csv.QUOTE_* constants.
    Use one of QUOTE_MINIMAL (0), QUOTE_ALL (1), QUOTE_NONNUMERIC (2) or
QUOTE_NONE (3).""",
    'doublequote':
    """bool, default: True
    When quotechar is specified and quoting is not QUOTE_NONE, indicate whether
or not to interpret two consecutive quotechar elements INSIDE a field as a
single quotechar element.""",
    'escapechar':
    """str (length 1), optional
    One-character string used to escape other characters.""",
    'comment':
    r"""str, optional
    Indicates remainder of line should not be parsed.
    If found at the beginning of a line, the line will be ignored altogether.
    This parameter must be a single character. Like empty lines
(as long as skip_blank_lines=True), fully commented lines are ignored by the
parameter header but not by skiprows.
    For example, if comment='#', parsing
        #empty\na,b,c\n1,2,3
    with header=0 will result in 'a,b,c' being treated as the header.""",
    'encoding':
    """str, optional, default: 'utf-8'
    Encoding to use for UTF when reading/writing (ex. 'utf-8').
    List of Python standard encodings.""",
    'encoding_errors':
    """str, optional, default: 'strict'
    How encoding errors are treated.
    List of possible values.""",
    'dialect':
    """str or csv.Dialect, optional
    If provided, this parameter will override values (default or not) for the
following parameters: delimiter, doublequote, escapechar, skipinitialspace,
quotechar, and quoting.
    If it is necessary to override values, a ParserWarning will be issued.
See csv.Dialect documentation for more details.""",
    'on_bad_lines':
    """{'error', 'warn', 'skip'} or callable, default: 'error'
    Specifies what to do upon encountering a bad line
(a line with too many fields).
    Allowed values are:
        'error', raise an Exception when a bad line is encountered.
        'warn', raise a warning when a bad line is encountered and skip
that line.
        'skip', skip bad lines without raising or warning when they are
encountered.""",
    'delim_whitespace':
    r"""bool, default: False
    Specifies whether or not whitespace (e.g. ' ' or ' ') will be used
as the sep.
    Equivalent to setting sep='\s+'.
    If this option is set to True, nothing should be passed in for the
delimiter parameter.""",
    'low_memory':
    """bool, default: True
    Internally process the file in chunks, resulting in lower memory use
while parsing, but possibly mixed type inference.
    To ensure no mixed types either set False, or specify the type with
the dtype parameter.
    Note that the entire file is read into a single DataFrame regardless,
use the chunksize or iterator parameter to return the data in chunks.
(Only valid with C parser).""",
    'memory_map':
    """bool, default: False
    If a filepath is provided for filepath_or_buffer, map the file object
directly onto memory and access the data directly from there.
    Using this option can improve performance because there is no longer
any I/O overhead.""",
    'float_precision':
    """str, optional
    Specifies which converter the C engine should use for
floating-point values.
    The options are
        None or 'high' for the ordinary converter,
        'legacy' for the original lower precision pandas converter, and
        'round_trip' for the round-trip converter.""",
    'storage_options':
    """dict, optional
    Extra options that make sense for a particular storage connection,
e.g. host, port, username, password, etc.
    For HTTP(S) URLs the key-value pairs are forwarded to
urllib.request.Request as header options.
    For other URLs (e.g. starting with 's3://', and 'gcs://') the key-value
pairs are forwarded to fsspec.open.
    Please see fsspec and urllib for more details, and for more examples
on storage options refer here.""",
    'dtype_backend':
    """{'numpy_nullable', 'pyarrow'}, defaults to NumPy backed DataFrames
    Which dtype_backend to use, e.g. whether a DataFrame should have
NumPy arrays, nullable dtypes are used for all dtypes that have a nullable
implementation when 'numpy_nullable' is set, pyarrow is used for all dtypes
if 'pyarrow' is set.
    The dtype_backends are still experimental.""",
}
read_csvhelp.update({'missing_value':
                     'scalar or str\n'
                     '    Additional value to na_values set to NA/NaN.'})
"""
Tooltips for pandas.read_csv options from pandas v2.0.3

"""


class dfvReadcsv(QWidget):
    """
    Window for reading csv files.

    """

    #
    # Setup panel
    #

    def __init__(self, master, callback=None, **kwargs):

        super().__init__(**kwargs)

        self.name = 'dfvReadcsv'

        self.master = master
        self.top = master.top
        self.df = self.top.df
        
        self.setWindowTitle("Read csv file")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)

        # 1. table
        self.nrows = 10
        if self.df is None:
            print('No df')
            ncols = 5
            columns = [ f'Column {i:03d}' for i in range(ncols) ]
            dat = [ [''] * ncols for i in range(self.nrows * 4) ]
            df = pd.DataFrame(dat, columns=columns)
        else:
            df = self.df
        self.table = self.new_table(df)
        self.layout.addWidget(self.table)

        # 2. empty row
        self.rowspace = QHBoxLayout()
        self.rowspace.setContentsMargins(5, 0, 5, 0)
        self.rowspace.setSpacing(3)

        space = add_label(self.rowspace, text=' ' * 1)
        self.rowspace.addStretch()

        self.layout.addLayout(self.rowspace)

        # 3. label for read_csv options
        self.rowlab = QHBoxLayout()
        self.rowlab.setContentsMargins(5, 0, 5, 5)
        self.rowlab.setSpacing(3)

        self.lab1 = add_label(self.rowlab, text='Options for ')
        self.lab2 = add_label(self.rowlab,
                              text=('<a href="https://pandas.pydata.org/docs/'
                                    'reference/api/pandas.read_csv.html">'
                                    'pandas.read_csv</a>'))
        # self.lab2.setTextFormat(Qt.RichText)
        # self.lab2.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.lab2.setOpenExternalLinks(True)
        self.lab3 = add_label(self.rowlab, text=' (date_format: see ')
        self.lab4 = add_label(self.rowlab,
                              text=('<a href="https://docs.python.org/3/library/'
                                    'datetime.html#strftime-and-strptime-behavior">'
                                    'strftime</a>'))
        # self.lab4.setTextFormat(Qt.RichText)
        # self.lab4.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.lab4.setOpenExternalLinks(True)
        self.lab5 = add_label(self.rowlab, text=')')

        self.rowlab.addStretch()

        self.layout.addLayout(self.rowlab)

        # 4. rows with pandas.read_csv options
        self.rowopt = QGridLayout()
        self.rowopt.setContentsMargins(5, 0, 5, 0)
        self.rowopt.setSpacing(3)
        self.rowopt.setHorizontalSpacing(10)
        self.rowopt.setVerticalSpacing(5)

        rowheight = 25
        lwidth = 140
        ewidth = 70
        self.opt = {}
        oend = 0
        nopt = len(read_csvopts)
        noptrow = nopt // 4
        if (nopt % 5) > 0:
            noptrow += 1
        for nr in range(noptrow):
            ostart = oend
            oend = ostart + 5
            for oois, oo in enumerate(read_csvopts[ostart:oend]):
                ilabel = QLabel(oo)
                fm = ilabel.fontMetrics()
                iwidth = fm.size(0, oo)
                ilabel.setMinimumWidth(iwidth.width() + 5)
                ilabel.setMaximumWidth(lwidth)
                self.rowopt.addWidget(ilabel, nr, 2 * oois,
                                      alignment=Qt.AlignmentFlag.AlignRight)
                #
                self.opt[oo] = QLineEdit(**kwargs)
                self.opt[oo].setText(str(read_csvdefaults[oo]))
                self.opt[oo].setMinimumWidth(ewidth)
                self.opt[oo].setToolTip(read_csvhelp[oo])
                self.opt[oo].editingFinished.connect(self.read_again)
                self.opt[oo].returnPressed.connect(self.read_final)
                self.rowopt.addWidget(self.opt[oo], nr, 2 * oois + 1,
                                      alignment=Qt.AlignmentFlag.AlignLeft)
            # one empty column at the end of each row
            ilabel1 = QLabel(' ')
            ilabel1.setMinimumWidth(2.5 * ewidth)
            self.rowopt.addWidget(ilabel1, nr, 11,
                                  alignment=Qt.AlignmentFlag.AlignLeft)

        # overwrite defaults from command line
        self.set_command_line_options(defaults=self.top.newcsvfile)

        self.layout.addLayout(self.rowopt)

        # 5. cancel and read buttons
        self.rowdone = QHBoxLayout()
        self.rowdone.setContentsMargins(3, 0, 3, 10)  # left, top, tight, bottom
        self.rowdone.setSpacing(3)

        self.rowdone.addStretch()

        self.icancel = add_pushbutton(
            self.rowdone, text='Cancel', command=self.cancel,
            tooltip='Cancel reading csv file',
            alignment=Qt.AlignmentFlag.AlignRight)

        self.done = add_pushbutton(
            self.rowdone, text='Read csv', command=self.read_final,
            tooltip='Finished options for reading csv',
            alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addLayout(self.rowdone)

        if len(self.top.screen) == 0:
            screen = self.screen().availableGeometry()
            self.top.screen = (screen.width(), screen.height())
        xs, ys, xo, yo = readcsv_window_size(self.top.screen)
        self.resize(xs, ys)
        self.move(xo, yo)

        self.setLayout(self.layout)

        self.show()
        
        # # move tabs window behind - does not work
        # self.master.lower()
        # # activate the readcsv window - does not work
        # self.raise_()
        # self.activateWindow()

    #
    # Event bindings
    #

    def cancel(self):
        self.close()

    def new_table(self, df=None):
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

        return itable

    def read_again(self):
        self.table.close()

        self.df = self.read_df(nrows=4 * self.nrows)
        
        self.newtable = self.new_table(self.df)
        self.layout.replaceWidget(self.table, self.newtable)
        self.table = self.newtable

    def read_df(self, nrows=None):
        """
        pandas.read_csv using options from entry fields

        """
        opts = {}
        for oo in read_csvopts:
            text = self.opt[oo].text()
            tt = parse_entry(text)
            if (tt != '') and (tt is not None):
                opts.update({oo: tt})
        # skipfooter does not work with nrows
        if nrows is not None:
            opts['nrows'] = nrows
            del opts['skipfooter']
        # add missing_value to na_values
        if 'missing_value' in opts:
            if 'na_values' in opts:
                if isinstance(opts['na_values'], Iterable):
                    nn = list(opts['na_values'])
                    nn.append(opts['missing_value'])
                    opts['na_values'] = nn
                else:
                    opts['na_values'] = [opts['na_values'],
                                         opts['missing_value']]
            else:
                opts['na_values'] = opts['missing_value']
            del opts['missing_value']
        # date_format introduced in pandas v2.0.0
        if pd.__version__ < '2':
            if 'date_format' in opts:
                date_parser = lambda date: pd.to_datetime(
                    date, format=opts['date_format'])
                opts['date_parser'] = date_parser
                del opts['date_format']
        try:
            with warnings.catch_warnings():
                warnings.simplefilter(action='ignore', category=FutureWarning)
                if (nrows is None) and (len(self.top.csvfile) > 1):
                    dfl = []
                    for cfile in self.top.csvfile:
                        dfl.append(pd.read_csv(cfile, **opts))
                    df = pd.concat(dfl)
                else:
                    df = pd.read_csv(self.top.csvfile[0], **opts)
        except pd.errors.ParserError:
            if (nrows is None) and (len(self.top.csvfile) > 1):
                dfl = []
                for cfile in self.top.csvfile:
                    with open(cfile, 'r') as fi:
                        fin = fi.readlines()
                    dfl.append(pd.DataFrame(fin))
                df = pd.concat(dfl)

        return df

    def read_final(self, event=None):
        self.top.df = self.read_df()

        # add index as column
        idx = 'df.index'
        if self.top.df.index.name is not None:
            idx = self.top.df.index.name
        if isinstance(self.top.df.index, pd.MultiIndex):
            series = [ [ str(kk) for kk in ii ]
                       for ii in self.top.df.index ]
            series = [ ' '.join(ii) for ii in series ]
        else:
            series = self.top.df.index
        # self.top.df.insert(0, idx, pd.Series(series, index=self.top.df.index))
        self.top.df = pd.concat([pd.Series(series, index=self.top.df.index),
                                 self.top.df], axis=1)
        if isinstance(self.top.df.index, pd.MultiIndex):
            # replace MultiIndex with combined column
            self.top.df.set_index(idx, drop=False, inplace=True)

        rows = self.top.df.shape[0]
        self.top.cols = [ f'{cc} ({rows} {self.top.df[cc].dtype.name})'
                          for cc in self.top.df.columns ]

        self.master.top.df = self.top.df
        self.master.top.cols = self.top.cols
        
        self.master.resetvars(nosort=True)
        self.master.x.setCurrentIndex(0)
        self.master.y.setCurrentIndex(0)
        self.master.y2.setCurrentIndex(0)
        self.master.redraw()

        self.close()

    def set_command_line_options(self, defaults=False):
        """
        Set options possible on the command line

        If defaults=True, use default options otherwise set options
        from command line.

        """
        if defaults:
            self.opt['sep'].setText('')
            self.opt['index_col'].setText('None')
            self.opt['skiprows'].setText('None')
            self.opt['parse_dates'].setText('True')
            self.opt['date_format'].setText('None')
            self.opt['missing_value'].setText('None')
        else:
            if self.top.sep != '':
                self.opt['sep'].setText(self.top.sep)
            if self.top.index_col is not None:
                self.opt['index_col'].setText(str(self.top.index_col))
            if self.top.skiprows is not None:
                self.opt['skiprows'].setText(str(self.top.skiprows))
            if self.top.parse_dates is not None:
                self.opt['parse_dates'].setText(str(self.top.parse_dates))
            if self.top.date_format is not None:
                self.opt['date_format'].setText(self.top.date_format)
            if self.top.missing_value is not None:
                self.opt['missing_value'].setText(str(self.top.missing_value))

        return
