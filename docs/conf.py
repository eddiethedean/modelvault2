"""Sphinx configuration for ModelVault."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelvault._version import __version__  # noqa: E402

project = "ModelVault"
copyright = "2026, ModelVault contributors"
author = "ModelVault contributors"
release = __version__
version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "internal"]

html_theme = "sphinx_rtd_theme"

html_static_path = ["_static"]

autodoc_member_order = "bysource"
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

myst_heading_anchors = 3
myst_linkify_fuzzy_links = False
