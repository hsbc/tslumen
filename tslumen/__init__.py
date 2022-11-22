"""tslumen helps bring to light the key characteristics of your time series data with rich,
pre-canned artifacts, packed with charts and statistical information. The primary goal of
tslumen is to expedite and bring consistency to how time series EDA is performed, allowing you to
uncover the fundamental aspects in seconds rather than hours or days.
"""
from pkg_resources import get_distribution, DistributionNotFound

from tslumen.profile import DefaultProfiler
from tslumen.report import HtmlReport, Dashboard


try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = ""

del get_distribution, DistributionNotFound


CORE_DEPENDENCIES = [
    "numpy",
    "pandas",
    "scipy",
    "statsmodels",
    "ipywidgets",
    "matplotlib",
    "hydra",
    "joblib",
    "plotly",
    "dash",
    "jupyter_dash",
    "dash_bootstrap_components",
]


def show_versions() -> None:
    """Prints out information about the python environment and key libraries, useful for
    debugging."""
    import platform
    import sys
    import importlib
    from collections import OrderedDict

    versions = OrderedDict()
    versions["python"] = sys.version.replace("\n", " ")
    versions["executable"] = sys.executable
    versions["machine"] = platform.platform()
    versions["tslumen"] = __version__
    for mod in CORE_DEPENDENCIES:
        try:
            ver = getattr(importlib.import_module(mod), "__version__", "cannot determine version")
        except ImportError:
            ver = "not installed"
        versions[mod] = ver

    for key, val in versions.items():
        print(f"{key:>25s}: {val}")


__all__ = ["__version__", "show_versions", "DefaultProfiler", "HtmlReport", "Dashboard"]
