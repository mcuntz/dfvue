dfvue
=====

A simple GUI to view csv files
------------------------------
..
  pandoc -f rst -o README.html -t html README.rst
  As docs/src/readme.rst:
    replace _small.png with .png
    replace
      higher resolution images can be found in the documentation_
    with
      click on figures to open larger pictures

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.10372631.svg
  :target: https://doi.org/10.5281/zenodo.10372631
  :alt: Zenodo DOI
	   
.. image:: https://badge.fury.io/py/dfvue.svg
   :target: https://badge.fury.io/py/dfvue
   :alt: PyPI version

.. image:: https://img.shields.io/conda/vn/conda-forge/dfvue.svg
   :target: https://anaconda.org/conda-forge/dfvue
   :alt: Conda version

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat
   :target: https://github.com/mcuntz/dfvue/blob/master/LICENSE
   :alt: License

.. image:: https://github.com/mcuntz/dfvue/workflows/Continuous%20Integration/badge.svg?branch=main
   :target: https://github.com/mcuntz/dfvue/actions
   :alt: Build status


About dfvue
-----------

``dfvue`` is a minimal GUI for a quick view of csv files. It uses an
input panel similar to Microsoft Excel to check visually that the csv
file is read correctly. It provides most options of the
`pandas.read_csv`_ method to be very versatile on possible csv
formats.

``dfvue`` is a Python script that can be called from within Python or
as a command line tool. It is not supposed to produce
publication-ready plots but rather provide a quick overview of the csv
file.

A more complete documentation for ``dfvue`` is available from:

   https://mcuntz.github.io/dfvue/


Installation
------------

``dfvue`` is an application written in Python. It can be installed
with `pip`:

.. code-block:: bash

   python -m pip install customtkinter dfvue

or via Conda_:

.. code-block:: bash

   conda install -c conda-forge dfvue

``dfvue`` uses CustomTkinter_ if it is installed. CustomTkinter_ is
not on Conda_.  One can install CustomTkinter_ with pip on Conda_, which works well except for Linux.

Sometimes `tkinter` is not enabled in the system's Python version. One
has to do, for example, ``sudo apt install python3-tk`` on Linux or
``brew install python3 python-tk`` on macOS with Homebrew_.

We also provide standalone applications for macOS that
come with everything needed to run ``dfvue`` including Python:

  - `dfvue 6.2 CTk Intel`_ and `dfvue 6.2 CTk ARM`_ for Intel and ARM
    processors, resp., for macOS 15 [Sequoia] using CustomTkinter_
  - `dfvue 6.2 Intel`_ and `dfvue 6.2 ARM`_ for in Aqua look

`dfvue > 6.0` is either for Intel processors or for Apple
Silicon (ARM) chips. It comes in the standard Aqua look or uses the
CustomTkinter_ UI-library. The apps >= v6.0 are notarized by Apple and
might take a short while on first opening.


Quick usage guide
-----------------

``dfvue`` can be run from the command line:

.. code-block:: bash

   dfvue csv_file*.csv

or from within Python:

.. code-block:: python

   from dfvue import dfvue
   dfvue('csv_file.csv')

where the csv file is optional. The latter can be left out and csv
file(s) can be opened with the "Open File" button from within
``dfvue``.

Note, ``dfvue`` uses the `TkAgg` backend of `matplotlib`. It must be
called before any other call to `matplotlib`. This also means that you
cannot launch it from within `iPython` if it was launched with
`--pylab`. It can be called from within a standard `iPython`, though,
or using `ipython --gui tk`.


General layout
^^^^^^^^^^^^^^

On opening, ``dfvue`` presents currently only one panel for producing
scatter/line plots. Here is the look in macOS light mode (higher
resolution images can be found in the documentation_):

.. image:: https://mcuntz.github.io/dfvue/images/scatter_panel_light.png
   :width: 860 px
   :align: left
   :alt: Graphical documentation of dfvue layout

..
   :height: 462 px

The pane is organised in this fashion: the plotting canvas, the
Matplotlib navigation toolbar and the pane, where one can choose the
plotting variables and plotting options. You can open another,
identical window for the same csv file with the button "New Window" on
the top right. You can then also read in a new csv file in one of the
windows with the button "Open File".


Reading a csv file
^^^^^^^^^^^^^^^^^^

The "Read csv file" window opens when a csv file is given.

.. image:: https://mcuntz.github.io/dfvue/images/read_csv_panel.png
   :width: 860 px
   :align: left
   :alt: Read csv file window

One or several csv files can be given on the command line:

.. code-block:: bash

   dfvue csv_file*.csv

or from within Python:

.. code-block:: python

   from dfvue import dfvue
   dfvue('csv_file.csv')

or being selected from the "Choose csv file(s)" selector that opens
when hitting the button "Open File".

The "Read csv file(s)" window reads the first 40 rows of the (first)
csv file with the `pandas.read_csv`_ method using the options given in
the pane. It shows the resulting `pandas.DataFrame`_ in tabulated
format. Changing focus from one option entry to another, for example
by hitting the <tab> key, re-reads the first 40 rows of the csv file
with `pandas.read_csv`_ using the selected options in the
form. Hitting <enter> or <return> within the window reads the entire
csv file(s) using the selected options and returns to the plotting
panels. This is the same than pressing the "Read csv" button in the
lower right corner. Multiple csv files will be read one by one with
`pandas.read_csv`_ using the same options and then concatenated with
`pandas.concat`_.

The options in the form are default options of `pandas.read_csv`_
except for `parse_date`, which is set to `True` instead of
`False`. Hover over the entry boxes to see explanations of the options
in the tooltips.

If the csv file includes a Date/Time column, it is best to set this
column as the index of the `pandas.DataFrame`_ by using
`index_col`. Correct `datetime` is indicated if the index has the data
type `datetime64[ns]` in the plot panels.  This is then correctly
interpreted by the underlying Matplotlib when plotting, zooming, or
panning the axes.

`missing_value` is not an option of `pandas.read_csv`_. It is here for
convenience and any number entered in `missing_value` will be added to
pandas `na_values`.


Reading a csv file with options on the command line
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following options of `pandas.read_csv`_ can be given on the command line:

.. code-block:: bash

   -s separator, --sep separator
                         Delimiter to use.
   -i columns, --index_col columns
                         Column(s) to use as index, either given as column index
                         or string name.
   -k rows, --skiprows rows
                         Line number(s) to skip (0-indexed, must include comma,
                         e.g. "1," for skipping the second row) or number of lines
                         to skip (int, without comma) at the start of the file.
   -p bool/list/dict, --parse_dates bool/list/dict
                         boolean, if True -> try parsing the index.
                         list of int or names, e.g. 1,2,3
                             -> try parsing columns 1, 2, and 3 each as a separate
                                date column.
                         list of lists, e.g. [1,3]
                             -> combine columns 1 and 3 and parse as a single
                                date column.
                         dict, e.g. "foo":[1,3]
                             -> parse columns 1 and 3 as date and call result "foo"
   -d format_string, --date_format format_string
                         Will parse dates according to this format.
                         For example: "%Y-%m-%d %H:%M%S". See
                         https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
   -m missing_value, --missing_value missing_value
                        Missing or undefined value set to NaN. For negative values,
                        use long format, e.g. --missing_value=-9999.


Examples of pandas.read_csv options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`pandas.read_csv`_ is very powerful and can read a lot of different
formats. Here are some examples of csv files and the options for
`pandas.read_csv`_.

The most simple csv file would be like:

.. code-block::

   DATETIME,TA_1_1_1,RH_1_1,ALB_1_1_1
   2015-01-01 00:30:00,-2.17794549084,97.2958103396,0.0
   2015-01-01 01:00:00,-2.02584908489,98.2103903979,0.0

This can simply be read by setting `index_col=0`. The first column
including date and time can simply a be a `ISO8601`_ date, for example
'2015-01-01 00:30:00' or '2015-01-01T00:30:00', or be given by
`date_format`, which would be '%Y-%m-%d %H:%M:%S' in this case. See
the documentation of `pandas.to_datetime`_ or `strftime`_.

Command line options would be:

    `dfvue -i 0 csv-file`

or

    `dfvue -i 0 -d '%Y-%m-%d %H:%M:%S' csv-file`

A common practice is to put a special value for measurement errors or
similar such as -9999:

.. code-block::

   DATETIME,TA_1_1_1,RH_1_1,ALB_1_1_1
   2015-01-01 00:30:00,-2.17794549084,97.2958103396,-9999
   2015-01-01 01:00:00,-2.02584908489,98.2103903979,-9999
  
This can be read by setting `missing_value=-9999`. On the command
line, this is:

    `dfvue -i 0 --missing_value=-9999 csv-file`

or

    `dfvue -i 0 -d '%Y-%m-%d %H:%M:%S' -m '-9999' csv-file`

You have to use either put -9999 in quotes (`-m '-9999`) or use the
long form `--missing_value=-9999` instead of the short form `-m -9999`
in case of negative missing values because the command line would
interpret *-9999* as a separate option and would fail.
    
Date and time information can be given in different formats, for example:

.. code-block::

   Date;rho H1 (kg/m3);alb H1 (-);T_Psy H1 (degC);WS_EC H1 (m/s);Prec H1 (mm/30min)
   01.01.2015 00:30;97.2958103396;-9999;-2.17794549084
   01.01.2015 01:00;98.2103903979;-9999;-2.02584908489

which can be read by setting the date format:
`date_format=%d.%m.%Y %H:%M`, `index_col=0`, `missing_value=-9999`, as
well as the field separator `sep=;`. On the the command line, this is:

    `dfvue -s ';' -i 0 -d '%d.%m.%Y %H:%M' --missing_value=-9999 csv-file`

Or in `FLUXNET`_ / `ICOS`_ / `europe-fluxdata.eu`_ format with a
second row that shows the variable units:

.. code-block::

   TIMESTAMP_END,TA_1_1_1,RH_1_1_1,ALB_1_1_1
   YYYYMMDDhhmm,degC,%,adimensional
   201501010030,-2.17794549084,97.2958103396,-9999
   201501010100,-2.02584908489,98.2103903979,-9999

which is read with `date_format=%Y%M%d%H%M`, `index_col=0`,
`skiprows=1,`, and `missing_value=-9999`. Note the comma after '1' in
`skiprows`. Without the command, *skiprows* would be the number of rows
to skip at the beginning, i.e. the first row, which would be
wrong. The comma indicates that *skiprows* is a list and hence a list
of row indexes, that means *1* here and thus skip the second row. This
would be on the command line

    `dfvue -i 0 -d '%Y%m%d%H%M' --skiprows=1, --missing_value=-9999 csv-file`

Date and time information can also be in different columns. Here the
second column is the day-of-the-year:

.. code-block::

   year,jday,hour,min,tair,rhair,albedo
   2015,1,0,30,-2.17794549084,97.2958103396,-9999
   2015,1,1,0,-2.02584908489,98.2103903979,-9999

which can be read by setting `parse_dates=[0,1,2,3]`, `index_col=0`,
and `date_format=%Y %j %H %M`, as well as `missing_value=-9999`. Note
the brackets '[]' around `parse_dates`. Without brackets it would
parse columns 0, 1, 2, and 3 each as a separate date column, whereas
with brackets it combines columns 0, 1, 2, and 3 and parses it as a
single date column, with index '0'. It will use a space between column
entries. Hence `index_col=0` sets this combined column as the index,
parsing the dates with the format '%Y %j %H %M' with spaces between
the `strftime`_ formats.

On the command line, this would be:

    `dfvue -i 0 -p [0,1,2,3] -d '%Y %j %H %M' --missing_value=-9999 csv-file`

If you want to have spaces in the list of `parse_dates` on the command
line, you have to use the long form: `--parse_dates='[0, 1, 2, 3]'`.


Scatter/Line panel
^^^^^^^^^^^^^^^^^^

Here is the Scatter/Line panel in macOS light mode, describing all
buttons, sliders, entry boxes, spinboxes, and menus:

.. image:: https://mcuntz.github.io/dfvue/images/scatter_panel_light_multiline.png
   :width: 860 px
   :align: left
   :alt: Graphical documentation of Scatter/Line panel

The default plot is a line plot with solid lines (line style 'ls' is
'-'). One can set line style 'ls' to None and set a marker symbol,
e.g. 'o' for circles, to get a scatter plot. A large variety of line
styles, marker symbols and color notations are supported.


Transform panel
^^^^^^^^^^^^^^^

You can do calculations on the Pandas DataFrame. Use the "Transform df" button to open the transform panel:

.. image:: https://mcuntz.github.io/dfvue/images/transform_panel_light.png
   :width: 860 px
   :align: left
   :alt: Graphical documentation of Scatter/Line panel

You can do calculations with the DataFrame. The DataFrame is called
self.df. Its column names are the names of the x, y, and y2 variables
in the drop-down menus without (size, datatype).

You can transform the DataFrame such as doing daily means of all
columns. This transformation is preset in the transform panel for an
easier start on writing DataFrame calculations and transformations:
`self.df = self.df.resample('1D').mean().squeeze()`.  Calculations can
have multiple lines, import libraries, etc.


License
-------

``dfvue`` is distributed under the MIT License. See the LICENSE_ file
for details.

Copyright (c) 2023- Matthias Cuntz

``dfvue`` uses CustomTkinter_ if installed. Otherwise it uses the
Azure_ 2.0 theme by rdbende_ on Linux and Windows.

Standalone applications are produced with `cx_Freeze`_, currently
maintained by `Marcelo Duarte`_.


.. _cx_Freeze: https://cx-freeze.readthedocs.io/en/latest/
.. _dfvue 6.2 Windows: https://www.macu.de/extra/dfvue-6.2-win64.msi
.. _dfvue 6.2 CTk Intel: https://www.macu.de/extra/dfvue-6.2.ctk.intel.dmg
.. _dfvue 6.2 CTk ARM: https://www.macu.de/extra/dfvue-6.2.ctk.arm.dmg
.. _dfvue 6.2 Intel: https://www.macu.de/extra/dfvue-6.2.aqua.intel.dmg
.. _dfvue 6.2 ARM: https://www.macu.de/extra/dfvue-6.2.aqua.arm.dmg
.. _documentation: https://mcuntz.github.io/dfvue/
.. _europe-fluxdata.eu: https://www.europe-fluxdata.eu
.. _macOS app: https://www.macu.de/extra/dfvue-4.0.dmg
.. _pandas.concat: https://pandas.pydata.org/docs/reference/api/pandas.concat.html
.. _pandas.read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
.. _pandas.DataFrame: https://pandas.pydata.org/docs/reference/frame.html
.. _pandas.to_datetime: https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
.. _read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
.. _rdbende: https://github.com/rdbende
.. _strftime: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
.. _this thread: https://github.com/ContinuumIO/anaconda-issues/issues/6833
.. _Azure: https://github.com/rdbende/Azure-ttk-theme
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _CustomTkinter: https://customtkinter.tomschimansky.com
.. _FLUXNET: https://fluxnet.org
.. _Homebrew: https://brew.sh
.. _ICOS: https://www.icos-cp.eu
.. _ISO8601: https://en.wikipedia.org/wiki/ISO_8601
.. _LICENSE: https://github.com/mcuntz/dfvue/blob/main/LICENSE
.. _Marcelo Duarte: https://github.com/marcelotduarte
.. _Tom Schimansky: https://github.com/TomSchimansky
.. _Windows executable: https://www.macu.de/extra/dfvue-3.7-amd64.msi
