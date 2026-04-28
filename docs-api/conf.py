import os
import sys

# Lets Sphinx resolve your package if needed
sys.path.insert(0, os.path.abspath("../src"))

project = "Response Generator API"
copyright = "2026"
author = "Your Name"

extensions = [
    "autoapi.extension",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"

# AutoAPI config
autoapi_type = "python"
autoapi_dirs = ["../src"]

autoapi_python_use_implicit_namespaces = True
autoapi_mapper_config = {"use_module_imported_members": False}

autoapi_root = "autoapi"
autoapi_keep_files = True

# Optional but helpful
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]

napoleon_google_docstring = True
napoleon_numpy_docstring = True