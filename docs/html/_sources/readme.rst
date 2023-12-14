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
    remove section "Installation"

..
  image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4459598.svg
  :target: https://doi.org/10.5281/zenodo.4459598
  :alt: Zenodo DOI

.. image:: https://badge.fury.io/py/dfvue.svg
   :target: https://badge.fury.io/py/dfvue
   :alt: PyPI version

.. image:: http://img.shields.io/badge/license-MIT-blue.svg?style=flat
   :target: https://github.com/mcuntz/dfvue/blob/master/LICENSE
   :alt: License

.. image:: https://github.com/mcuntz/dfvue/workflows/Continuous%20Integration/badge.svg?branch=main
   :target: https://github.com/mcuntz/dfvue/actions
   :alt: Build status

About dfvue
-----------

``dfvue`` is a minimal GUI for a quick view of csv files. It uses an input panel
similar to Excel to check visually that the csv file is read correctly. It
provides most options of pandas' read_csv_ method to be very versatile on the
possible csv format.

``dfvue`` is a Python script that can be called from within Python or as a
command line tool. It is not supposed to produce publication-ready plots but
rather provide a quick overview of the csv file.

The complete documentation for ``dfvue`` is available from:

   https://mcuntz.github.io/dfvue/

Quick usage guide
-----------------

``dfvue`` can be run from the command line:

.. code-block:: bash

   dfvue csv_file.csv

or from within Python:

.. code-block:: python

   from dfvue import dfvue
   dfvue('csv_file.csv')

where the csv file is optional. The latter can be left out and a csv file can be
opened with the "Open File" button from within ``dfvue``.

Note, ``dfvue`` uses the `TkAgg` backend of `matplotlib`. It must be called
before any other call to `matplotlib`. This also means that you cannot launch it
from within `iPython` if it was launched with `--pylab`. It can be called from
within a standard `iPython`, though, or using `ipython --gui tk`.

..
   One can also install standalone macOS or Windows applications that come with
   everything needed to run ``dfvue`` including Python:

   - `macOS app`_ (macOS > 10.13 [High Sierra] on Intel)
   - `Windows executable`_ (Windows 10)

   The macOS app should work from macOS 10.13 (High Sierra) onward on Intel
   processors. There is no standalone application for macOS on Apple Silicon (M1)
   chips because I do not have a paid Apple Developer ID. Other installation
   options work, though.

   A dialog box might pop up on macOS saying that the ``dfvue.app`` is from an
   unidentified developer. This is because ``dfvue`` is an open-source software.
   Depending on the macOS version, it offers to open it anyway. In later versions
   of macOS, this option is only given if you right-click (or control-click) on the
   ``dfvue.app`` and choose `Open`. You only have to do this once. It will open
   like any other application the next times.

General layout
^^^^^^^^^^^^^^

On opening, ``dfvue`` presents currently only one panel for producing
scatter/line plots. This is the look in macOS light mode (click on figures to
open larger pictures):

.. image:: https://mcuntz.github.io/dfvue/images/scatter_panel_light.png
   :width: 860 px
   :align: left
   :alt: Graphical documentation of dfvue layout

..
   :height: 462 px

The pane is organised in this fashion: the plotting canvas, the Matplotlib
navigation toolbar and the pane, where one can choose the plotting variables and
plotting options. You can open another, identical window for the same csv file
with the button "New Window" on the top right. You can then also read in a new
csv file in one of the windows with the button "Open File".

Reading a csv file
^^^^^^^^^^^^^^^^^^

The "Read csv file" window opens when a csv file is given.

.. image:: https://mcuntz.github.io/dfvue/images/read_csv_panel.png
   :width: 860 px
   :align: left
   :alt: Read csv file window

The csv file can be given on the command line:

.. code-block:: bash

   dfvue csv_file.csv

from within Python:

.. code-block:: python

   from dfvue import dfvue
   dfvue('csv_file.csv')

or being selected from the "Choose csv file" selector that opens when hitting
the button "Open File".

The "Read csv file" window reads the first 40 rows of the csv file with pandas'
read_csv_ method using the options given in the pane. It shows the resulting
`pandas.DataFrame` in tabulated format. Changing focus from one option entry to
another, for example by hitting the <tab> key, re-reads the first 40 rows of the
csv file with `pandas.read_csv` using the selected options in the form. Hitting
<enter> or <return> within the window reads the entire csv file using the
selected options and returns to the plotting panels. This is the same than
pressing the "Read csv" button in the lower right corner.

The options in the form are pandas' read_csv_ default options except for
`parse_date`, which is set to `True` instead of `False` here. Hover over the
entry boxes to see explanations of the options in the tooltip.

If the csv file includes a Date/Time column, it is best to set this column as
the index of the `pandas.DataFrame` by using `index_col`. Correct `datetime` is
indicated if the index has the data type `datetime64[ns]` in the plot panels.
This is then correctly interpreted by the underlying Matplotlib when plotting,
zooming, or panning the axes. ``dfvue`` sets the index if `index_col` is used
but also provides the original column.

`missing_value` is not an option of pandas' read_csv_. It is here for
convenience and any number entered in `missing_value` will be added to pandas
`na_values`.

Scatter/Line panel
^^^^^^^^^^^^^^^^^^

Here is the Scatter/Line panel in macOS dark mode, describing all buttons,
sliders, entry boxes, spinboxes, and menus:

.. image:: https://mcuntz.github.io/dfvue/images/scatter_panel_dark.png
   :width: 860 px
   :align: left
   :alt: Graphical documentation of Scatter/Line panel

The default plot is a line plot with solid lines (line style 'ls' is '-'). One
can set line style 'ls' to None and set a marker symbol, e.g. 'o' for circles,
to get a scatter plot. A large variety of line styles, marker symbols and color
notations are supported.

License
-------

``dfvue`` is distributed under the MIT License. See the LICENSE_ file for
details.

Copyright (c) 2023- Matthias Cuntz

``dfvue`` uses the Azure_ theme (v2.0) by rdbende_ on Linux and Windows.

Standalone applications are produced with `cx_Freeze`_, currently maintained by
`Marcelo Duarte`_.


.. _read_csv: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
.. _macOS app: http://www.macu.de/extra/dfvue-4.0.dmg
.. _Windows executable: http://www.macu.de/extra/dfvue-3.7-amd64.msi
.. _documentation: https://mcuntz.github.io/dfvue/
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _instructions: https://mcuntz.github.io/dfvue/html/install.html
.. _LICENSE: https://github.com/mcuntz/dfvue/blob/main/LICENSE
.. _Azure: https://github.com/rdbende/Azure-ttk-theme
.. _rdbende: https://github.com/rdbende
.. _cx_Freeze: https://cx-freeze.readthedocs.io/en/latest/
.. _Marcelo Duarte: https://github.com/marcelotduarte