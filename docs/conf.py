import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'Recipe Bot'
author = 'Орлова Лилиана, Юргенсон Ника'
copyright = '2025, Орлова Лилиана, Юргенсон Ника'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
]

language = 'ru'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**/.ipynb_checkpoints']

# HTML output settings
html_theme = 'sphinx_rtd_theme'  # More modern theme with better code display
html_static_path = ['_static']
html_title = f"{project} v{release}"

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__str__',
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}


# Make sure the target is unique
autosectionlabel_prefix_document = True
