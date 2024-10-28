import os
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'LUMEX'
copyright = '2024, Daniel Mačura'
author = 'Daniel Mačura'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "sphinx.ext.inheritance_diagram",
]

templates_path = ['_templates']
exclude_patterns = []

sys.path.insert(0, os.path.abspath('../../../src/'))

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

autodoc_default_options = {
    'member-order': 'bysource',
    'special-members': '__init__',
}
