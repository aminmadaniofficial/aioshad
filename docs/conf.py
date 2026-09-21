# Configuration file for the Sphinx documentation builder.
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "aioshad"
copyright = "2026, Mohammadamin Madani"
author = "Mohammadamin Madani"
release = "0.1.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "aioshad documentation"
html_static_path = ["_static"]
html_logo = "_static/logo.svg"
html_favicon = "_static/logo.svg"
html_css_files = ["custom.css"]

_FONT_SANS = (
    "Geist, Vazirmatn, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', "
    "Roboto, 'Helvetica Neue', Arial, sans-serif"
)
_FONT_MONO = (
    "'Geist Mono', 'JetBrains Mono', 'Fira Code', ui-monospace, Menlo, monospace"
)

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "light_css_variables": {
        "font-stack": _FONT_SANS,
        "font-stack--monospace": _FONT_MONO,
        "color-brand-primary": "#1F4FE0",
        "color-brand-content": "#1F4FE0",
        "color-background-primary": "#F3F1EC",
        "color-background-secondary": "#FAF9F6",
        "color-background-hover": "#eef3fd",
        "color-background-border": "#DAD6CD",
        "color-foreground-primary": "#16161A",
        "color-foreground-secondary": "#5F5E5A",
        "color-foreground-muted": "#5F5E5A",
        "color-sidebar-background": "#FAF9F6",
        "color-sidebar-background-border": "#DAD6CD",
    },
    "dark_css_variables": {
        "font-stack": _FONT_SANS,
        "font-stack--monospace": _FONT_MONO,
        "color-brand-primary": "#5B82FF",
        "color-brand-content": "#5B82FF",
        "color-background-primary": "#0E0F12",
        "color-background-secondary": "#14161A",
        "color-background-hover": "#1c1f26",
        "color-background-border": "#26282D",
        "color-foreground-primary": "#ECEAE4",
        "color-foreground-secondary": "#9A988F",
        "color-foreground-muted": "#9A988F",
        "color-sidebar-background": "#14161A",
        "color-sidebar-background-border": "#26282D",
        "color-sidebar-link-text": "#ECEAE4",
        "color-sidebar-caption-text": "#9A988F",
        "color-sidebar-item-background--current": "#1c2230",
        "color-inline-code-background": "#1c1f26",
        "color-code-background": "#14161A",
        "color-code-foreground": "#ECEAE4",
    },
    "source_repository": "https://github.com/aminmadaniofficial/aioshad/",
    "source_branch": "main",
    "source_directory": "docs/",
}
