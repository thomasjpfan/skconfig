#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.abspath('..'))


extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinx.ext.napoleon',
              'sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('http://docs.scipy.org/doc/numpy/', None),
}

templates_path = ['_templates']

source_suffix = '.rst'
master_doc = 'index'

project = u'skconfig'
copyright = u"2019, Thomas J Fan"
author = u"Thomas J Fan"

with open('../VERSION', 'r') as f:
    release = f.read().strip()
    version = release.rsplit('.', 1)[0]

language = 'en'

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

# HTML output theme
html_theme = 'sphinx_rtd_theme'

htmlhelp_basename = 'skconfigdoc'

# Latex
latex_elements = {}

latex_documents = [
    (master_doc, 'skconfig.tex',
     u'skconfig Documentation',
     u'Thomas J Fan', 'manual'),
]

# Manual page output
man_pages = [
    (master_doc, 'skconfig',
     u'skconfig Documentation',
     [author], 1)
]

# Textinfo output
texinfo_documents = [
    (master_doc, 'skconfig',
     u'skconfig Documentation',
     author,
     'skconfig',
     'One line description of project.',
     'Miscellaneous'),
]
