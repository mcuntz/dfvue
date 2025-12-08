Changelog
---------

v6.5.1 (Dec 2025)
  - Finetuned sizes without CustomTkinter.
  - Corrected bug/typo in transfom window.
  - Set window size on Linux systems that do not support
    state('zoomed') on tkinter windows.

v6.5 (Dec 2025)
   - Draw canvas as last element so that UI controls are displayed
     as long as possible.
   - Get size from fullscreen window to deal with multiple monitors.

v6.4 (Nov 2025)
   - Deduce datetime in xlim and ylim.

v6.3 (Nov 2025)
   - Use screen size to determine window sizes.

v6.2 (Jul 2025)
   - Focus on first option upon calling of readcsv window.
   - New position for readcsv window.
   - Bugfix for setting axes limits.
   - Use button, label, and combobox from ncvwidgets.
   - Use updated ncvue-blue CustomTkinter scheme.
   - Separate rows for x- and y-limits.
   - Smaller entry fields for non-Windows OS.

v6.1 (Mar 2025)
   - Larger entry fields for Windows.
   - Add xlim, ylim, and y2lim options.
   - Increased number of digits in format_coord_scatter.
   - Use ncvue theme with CustomTkinter.
   - Removed addition of index to column names when sorting variable
     names.
   - Keep NaN values as str when reading csv.
   - Bugfix when no file given on command line.
   - Possibility to pass `pandas.DataFrame` directly to dfvue in
     Python.
   - Bugfix when checking if csvfile was given.
   - Add low_memory to read_csv switches.

v6.0 (Dec 2024)
   - Make standalone packages.
   - Sync `ncvwidgets` with developments in `ncvue`.

v5.0 (Nov 2024)
   - Back to pack layout manager for resizing of plotting window.
   - pyplot was not imported on Windows in `dfvue`.
   - `Transform` window to manipulate DataFrame.
   - Correct datetime formatting in coordinate printing.
   - Move from token to trusted publisher on PyPI.
   - Silence FutureWarning from `pandas.read_csv`.

v4.0 (Oct 2024)
   - Allow multiple input files that will be concatenated.

v3.0 (Jun 2024)
   - Use Azure theme if CustomTkinter is not installed such as in
     conda environments.
   - Increased size of ReadCSV window to fit widgets on Windows.

v2.0 (Jun 2024)
   - Exclusively use CustomTkinter.
   - Updated documentation with new screenshots.

v1.9 (Jun 2024)
   - Using CustomTkinter on top of Tkinter.
   - Use mix of grid and pack layout managers.

v1.0 (May 2024)
   - Works with newer and older matplotlib versions.

v0.99 (Dec 2023)
   - First public version.
