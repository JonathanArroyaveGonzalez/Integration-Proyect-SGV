# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Integration-Proyect-SGV'
copyright = '2025, Daniel Giraldo, Luis Gonzales, Jonathan Arroyave'
author = 'Daniel Giraldo, Luis Gonzales, Jonathan Arroyave'
release = '1.0'

# -- General configuration ---------------------------------------------------
import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath(".."))

# Configuración de Django
import sys
import os
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Mock de módulos externos que no estén instalados localmente
autodoc_mock_imports = [
    'django',
    'rest_framework',
    'requests',
    'mercadopago',
    'psycopg2',
    'mysqlclient',
    'pymongo',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'es'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme' 
html_static_path = ['_static']
