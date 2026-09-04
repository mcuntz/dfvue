# version, author
try:
    from ._version import __version__
except ImportError:  # pragma: nocover
    # package is not installed
    __version__ = "0.0.0.dev0"
__author__  = "Matthias Cuntz"

# current state
from .top import *
# utilities
from .dfvutils import *
# widgets
from .vuewidgets import *

# read csv file window
from .dfvreadcsv import *
# manipulate DataFrame window
from .dfvtransform import *

# scatter/line panel
from .dfvscatter import *
# main window with panel(s)
from .dfvmain import *
# calling routine
from .dfvue import *
