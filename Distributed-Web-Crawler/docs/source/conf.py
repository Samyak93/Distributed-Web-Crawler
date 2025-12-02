# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../../Orchestrator'))
sys.path.insert(0, os.path.abspath('../../Worker'))

autosummary_generate = True

project = 'Distributed Web Crawler'
copyright = '2025, Samyak Shah, Uzair Islam, Nimisha Mathew'
author = 'Samyak Shah, Uzair Islam, Nimisha Mathew'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',       # Automatically documents docstrings
    'sphinx.ext.napoleon',      # Supports Google/NumPy style docstrings
    'sphinx.ext.viewcode',      # Adds links to source code
    'sphinx.ext.autosummary',   # Generates summary tables for modules/classes
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

latex_elements = {
    'papersize': 'letterpaper',  # or 'a4paper'
    'pointsize': '10pt',
    'classoptions': ',oneside',   # <- this fixes the blank pages
    'babel': '\\usepackage[english]{babel}',  # optional
    'figure_align': 'H',
}

