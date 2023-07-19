Installation
============

``dfvue`` is an application written in Python. If you have Python installed,
then the best is to install ``dfvue`` within the Python universe. The easiest
way to install ``dfvue`` is thence via `pip`:

.. code-block:: bash

   python -m pip install dfvue

or via Conda_:

.. code-block:: bash

   conda install -c conda-forge dfvue

..
   Binary distributions
   --------------------

   We also provide standalone macOS and Windows applications that come with
   everything needed to run ``dfvue`` including Python:

   - `macOS app`_ (macOS > 10.13, High Sierra on Intel)
   - `Windows executable`_ (Windows 10)

   The macOS app should work from macOS 10.13 (High Sierra) onward on Intel
   processors. There is no standalone application for macOS on Apple Silicon (M1)
   chips because I do not have a paid Apple Developer ID. The installation via
   `pip` works, though.

   A dialog box might pop up on macOS saying that the ``dfvue.app`` is from an
   unidentified developer. This is because ``dfvue`` is an open-source software.
   Depending on the macOS version, it offers to open it anyway. In later versions
   of macOS, this option is only given if you right-click (or control-click) on the
   ``dfvue.app`` and choose `Open`. You only have to do this once. It will open like
   any other application the next times.

Building from source
--------------------

The latest version of ``dfvue`` can be installed from source:

.. code-block:: bash

   python -m pip install git+https://github.com/mcuntz/dfvue.git

You can use the `\-\-user` option with `pip install` if you do not have proper
privileges to install Python packages (and you are not using a virtual
environment).

You probably also have to run the Command prompt or the Powershell Prompt as
Administrator (Right click > More > Run as administrator) on Windows to install
Python packages.

Dependencies
------------

``dfvue`` uses the Python packages :mod:`numpy`, :mod:`pandas`, and
:mod:`matplotlib`, which are easily installed with `pip` from PyPI.

Linux
^^^^^

``dfvue`` also uses :mod:`tkinter`, which normally comes with any Python
installation. However, it is not always included on Linux. It can be installed
on Ubuntu, for example, with:

.. code-block:: bash

   sudo apt install python3-tk

macOS
^^^^^

It is possible that your Python version, e.g. installed with pyenv_, might clash
with Apple's Tcl/Tk library. This gives in the best case a deprecation warning
like:

.. code-block::

   DEPRECATION WARNING: The system version of Tk is deprecated and
   may be removed in a future release. Please don't rely on it.
   Set TK_SILENCE_DEPRECATION=1 to suppress this warning.

You have to install `tcl-tk` from homebrew_ first and then reinstall Python
(example with Python version 3.11.1):

.. code-block:: bash

   brew install tcl-tk
   env PYTHON_CONFIGURE_OPTS=" \
       --with-tcltk-includes='-I${HOMEBREW_PREFIX}/opt/tcl-tk/include' \
       --with-tcltk-libs='-L${HOMEBREW_PREFIX}/opt/tcl-tk/lib -ltcl8.6 -ltk8.6' \
       --enable-optimizations --enable-framework=${HOME}/Library/Frameworks" \
       CFLAGS="-I$(brew --prefix xz)/include" \
       LDFLAGS="-L$(brew --prefix xz)/lib" \
       PKG_CONFIG_PATH="$(brew --prefix xz)/lib/pkgconfig" \
       pyenv install 3.11.1

Note that `tcl-tk` is keg-only in homebrew_. Using `env` in the above command
allows using the homebrew version of Tcl/Tk with Python while not interfering
with the macOS provided Tcl/Tk installation.


.. _Anaconda: https://www.anaconda.com/products/individual
.. _Conda: https://docs.conda.io/projects/conda/en/latest/
.. _homebrew: https://brew.sh/
.. _macOS app: http://www.macu.de/extra/dfvue-4.0.dmg
.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _Miniforge: https://github.com/conda-forge/miniforge
.. _pyenv: https://github.com/pyenv/pyenv
.. _Windows executable: http://www.macu.de/extra/dfvue-1.0-amd64.msi
