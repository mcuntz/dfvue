Changelog
---------

v6.1 (Mar 2025)
   * Larger entry fields for Windows.
   * Add xlim, ylim, and y2lim options.
   * Increased number of digits in format_coord_scatter.
   * Use ncvue theme with customtkinter.
   * Removed addition of index to column names when sorting variable
     names.
   * Keep NaN values as str when reading csv.
   * Bugfix when no file given on command line.
   * Possibility to pass `pandas.DataFrame` directly to dfvue in
     Python.
   * Bugfix when checking if csvfile was given.
   * Add low_memory to read_csv switches.

v6.0 (Dec 2024)
   * Make standalone packages.
   * Sync `ncvwidgets` with developments in `ncvue`.

v5.0 (Nov 2024)
   * Back to pack layout manager for resizing of plotting window.
   * pyplot was not imported on Windows in `dfvue`.
   * `Transform` window to manipulate DataFrame.
   * Correct datetime formatting in coordinate printing.
   * Move from token to trusted publisher on PyPI.
   * Silence FutureWarning from `pandas.read_csv`.

v4.0 (Oct 2024)
   * Allow multiple input files that will be concatenated.

v3.0 (Jun 2024)
   * Use Azure theme if CustomTkinter is not installed such as in
     conda environments.
   * Increased size of ReadCSV window to fit widgets on Windows.

v2.0 (Jun 2024)
   * Exclusively use CustomTkinter.
   * Updated documentation with new screenshots.

v1.9 (Jun 2024)
   * Using CustomTkinter on top of Tkinter.
   * Use mix of grid and pack layout managers.

v1.0 (May 2024)
   * Works with newer and older matplotlib versions.

v0.99 (Dec 2023)
   * First public version.
