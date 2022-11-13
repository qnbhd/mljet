# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

import plotly.io as pio
from sphinx_gallery.sorting import FileNameSortKey

sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'deployme'
copyright = '2022, Konstantin Templin & Kristina Zheltova'
author = 'Konstantin Templin, Kristina Zheltova'

# The full version, including alpha/beta/rc tags
release = '0.0.5'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
    'sphinx_gallery.gen_gallery',
    'sphinx_autodoc_typehints',
    'sphinx_git',
]

source_suffix = ".rst"

master_doc = "index"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '*/*tests',
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

html_theme_options = {
    "sidebar_hide_name": True,
    "navigation_with_keys": True,
    "source_repository": "https://github.com/qnbhd/deployme",
    "source_branch": "main",
    "source_directory": "docs/",
}

html_logo = "deployme-logo-p.svg"
html_show_sourcelink = False

# Extensions

copybutton_prompt_text = "$ "
pio.renderers.default = "sphinx_gallery"

sphinx_gallery_conf = {
    "examples_dirs": [
        "../../tutorial",
    ],
    "gallery_dirs": [
        "tutorial",
    ],
    "within_subsection_order": FileNameSortKey,
    "filename_pattern": r"/*\.py",
    "first_notebook_cell": None,
}

# matplotlib plot directive
plot_include_source = True
plot_formats = [("png", 90)]
plot_html_show_formats = False
plot_html_show_source_link = False

# sphinx plotly directive
plotly_include_source = True
plotly_formats = ["html"]
plotly_html_show_formats = False
plotly_html_show_source_link = False

autosummary_generate = True

autodoc_typehints = "none"
autodoc_default_options = {
    "members": True,
    "inherited-members": True,
    "exclude-members": "with_traceback",
    "undoc-members": True,
}
autoclass_content = 'both'

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scikit-learn': ('https://scikit-learn.org/stable/', None),
    'rich': ('https://rich.readthedocs.io/en/latest/', None),
    'docker': ('https://docker-py.readthedocs.io/en/stable/', None),
    'black': ('https://black.readthedocs.io/en/stable/', None),
    'mypy': ('https://mypy.readthedocs.io/en/stable/', None),
    'returns': ('https://returns.readthedocs.io/en/latest/', None),
    'emoji': ('https://emoji.readthedocs.io/en/latest/', None),
    'xgboost': ('https://xgboost.readthedocs.io/en/latest/', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
}
