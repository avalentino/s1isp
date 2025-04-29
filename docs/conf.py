# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Version utils -----------------------------------------------------------

import pathlib


def _get_version(filename):
    import re

    with open(filename) as fd:
        data = fd.read()

    mobj = re.search(
        r"""^__version__\s*=\s*(?P<quote>['"])(?P<version>.*)(?P=quote)""",
        data,
        re.MULTILINE,
    )
    return mobj.group("version")


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "s1isp"
copyright = "2023-2025, Antonio Valentino"
author = "Antonio Valentino"
release = _get_version(
    pathlib.Path(__file__).parent.parent / "s1isp" / "__init__.py"
)


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    # "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.duration",
    "sphinx.ext.extlinks",
    # "sphinx.ext.githubpages",
    # "sphinx.ext.graphviz",
    "sphinx.ext.ifconfig",
    # "sphinx.ext.imgconverter",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    # "sphinx.ext.linkcode",  # needs_sphinx = "1.2"
    # "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    # "sphinx.ext.imgmath",
    # "sphinx.ext.jsmath",
    # "sphinx.ext.mathjax",
    "sphinx_rtd_theme",
]

try:
    import sphinxcontrib.spelling  # noqa: F401
except ImportError:
    pass
else:
    extensions.append("sphinxcontrib.spelling")

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    # 'vcs_pageview_mode': 'blob',
}
html_context = {
    # 'github_url': 'https://github.com/avalentino/bpack/',
    "display_github": True,
    "github_user": "avalentino",
    "github_repo": "s1isp",
    "github_version": "main",
    "conf_py_path": "/docs/",  # Path in the checkout to the docs root
}

html_last_updated_fmt = ""


# -- Options for LaTeX output ------------------------------------------------
latex_documents = [
    # (startdocname, targetname, title, author, theme, toctree_only)
    (
        project,
        project + ".tex",
        "Sentinel-1 Instrument Source Packets decoder",
        author,
        "manual",
        False,
    ),
]

latex_domain_indices = False

latex_elements = {
    # 'papersize': 'a4paper',
    "pointsize": "12pt",
}


# -- Extension configuration -------------------------------------------------

# -- Options for autodoc extension -------------------------------------------
# autoclass_content = 'both'
autodoc_member_order = "groupwise"
# autodoc_default_options = {
#     "members": True,
#     "undoc-members": True,
#     "show-inheritance": True,
# }
autodoc_mock_imports = []
for module_name in ["bpack", "tqdm"]:
    try:
        __import__(module_name)
    except ImportError:
        autodoc_mock_imports.append(module_name)


# -- Options for autosummary extension ---------------------------------------
autosummary_generate = True
# autosummary_mock_imports = []
# autosummary_ignore_module_all = False


# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}


# -- Options for extlinks extension ------------------------------------------

extlinks = {
    "issue": ("https://github.com/avalentino/s1isp/issues/%s", "gh-%s"),
}


# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
