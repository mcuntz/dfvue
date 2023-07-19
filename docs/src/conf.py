#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# dfvue documentation build configuration file.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# NOTE:
# pip install sphinx_rtd_theme
# is needed in order to build the documentation
import datetime
import warnings
import os
import sys
# this line is needed, if dfvue is not installed yet
sys.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)) + '/../../src')
from dfvue import __version__ as ver

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=("Matplotlib is currently using agg, which is a non-GUI backend,"
             " so cannot show the figure."),
)

def skip(app, what, name, obj, skip, options):
    if name in ["__call__"]:
        return False
    return skip


def setup(app):
    app.connect("autodoc-skip-member", skip)


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    # "sphinx.ext.imgmath",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # parameters look better than with numpydoc only
    "numpydoc",
]

# autosummaries from source-files
autosummary_generate = True
# dont show __init__ docstring
autoclass_content = "class"
# sort class members
autodoc_member_order = "groupwise"
# autodoc_member_order = 'bysource'

# don't add full path to module
add_module_names = False

# Notes in boxes
napoleon_use_admonition_for_notes = True
# Attributes like parameters
# napoleon_use_ivar = True
# this is a nice class-doc layout
numpydoc_show_class_members = True
# class members have no separate file, so they are not in a toctree
numpydoc_class_members_toctree = False
# for the covmodels alot of classmembers show up...
numpydoc_show_inherited_class_members = True
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = [".rst", ".md"]
source_suffix = ".rst"

# The master toctree document.
# --> this is the sitemap (or content-list in latex -> needs a heading)
# for html: the quickstart (in index.rst)
# gets the "index.html" and is therefore opened first
master_doc = "index"

# General information about the project.
curr_year = datetime.datetime.now().year
project = "dfvue"
copyright = "2020-{}, Matthias Cuntz".format(curr_year)
author = "Matthias Cuntz"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ver
# The full version, including alpha/beta/rc tags.
release = ver

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['.DS_Store']
# exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

# html_theme = "sphinx_rtd_theme"
# html_theme_options = {
#     #    'canonical_url': '',
#     #    'analytics_id': '',
#     "logo_only": False,
#     "display_version": True,
#     "prev_next_buttons_location": "top",
#     #    'style_external_links': False,
#     #    'vcs_pageview_mode': '',
#     # Toc options
#     "collapse_navigation": False,
#     "sticky_navigation": True,
#     "navigation_depth": 4,
#     "includehidden": True,
#     "titles_only": False,
# }

html_theme = 'alabaster'
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}
html_theme_options = {
    'description': 'A minimal GUI for a quick view of csv files.',
    'extra_nav_links': {
        'dfvue @ GitHub': "https://github.com/mcuntz/dfvue",
        'dfvue @ Zenodo': "https://doi.org/10.5281/zenodo.5574388",
        'dfvue @ PyPI': "https://pypi.org/project/dfvue",
        'dfvue @ conda-forge': "https://anaconda.org/conda-forge/dfvue"
    },
}

# # Add any paths that contain custom static files (such as style sheets) here,
# # relative to this directory. They are copied after the builtin static files,
# # so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# # These paths are either relative to html_static_path
# # or fully qualified paths (eg. https://...)
html_css_files = ['css/custom.css']

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "dfvuedoc"


# -- Options for LaTeX output ---------------------------------------------

# latex_show_urls = 'footnote'
# http://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output
latex_elements = {
    "preamble": r"""
\setcounter{secnumdepth}{1}
\setcounter{tocdepth}{2}
\pagestyle{fancy}
""",
    "pointsize": "10pt",
    "papersize": "a4paper",
    "fncychap": "\\usepackage[Glenn]{fncychap}",
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "dfvue.tex",
        "Documentation of dfvue",
        author,
        "manual",
    )
]
# latex_use_parts = True

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, "dfvue", "Documentation of dfvue", [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "dfvue",
        "Documentation of dfvue",
        author,
        "dfvue",
        "A minimal GUI for a quick view of csv files.",
        "Miscellaneous",
    )
]

suppress_warnings = [
    "image.nonlocal_uri",
    # "app.add_directive",  # this suppresses the numpydoc induced warning
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "Python":      ("https://docs.python.org/3/",                    None),
    "NumPy":       ("https://numpy.org/doc/stable/",                 None),
    "SciPy":       ("https://docs.scipy.org/doc/scipy/reference/",   None),
    "matplotlib":  ("https://matplotlib.org/",                       None),
    "Pandas":      ("https://pandas.pydata.org/docs/",               None),
    "cython":      ("https://cython.readthedocs.io/en/latest/",      None),
    "cftime":      ("https://unidata.github.io/cftime/",             None),
    # "netcdf4-python": ("https://unidata.github.io/netcdf4-python/",  None),
    "openpyxl":    ("https://openpyxl.readthedocs.io/en/stable/",    None),
    "Sphinx":      ("https://www.sphinx-doc.org/en/master/",         None),
    "schwimmbad":  ("https://schwimmbad.readthedocs.io/en/latest/",  None),
    "mpi4py":      ("https://mpi4py.readthedocs.io/en/latest/",      None),
    "emcee":       ("https://emcee.readthedocs.io/en/latest/",       None),
    "partialwrap": ("https://partialwrap.readthedocs.io/en/latest/", None),
    "pyeee":       ("https://pyeee.readthedocs.io/en/latest/",       None),
}
