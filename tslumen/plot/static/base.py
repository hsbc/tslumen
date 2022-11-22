"""Base class `Figure` definition."""
from abc import ABC, abstractmethod
from typing import Generator, Any
from io import BytesIO
import contextlib
import warnings
import base64
import textwrap

from pandas.plotting import register_matplotlib_converters
import matplotlib as mpl
import matplotlib.pyplot as plt


class Figure(ABC):
    """Base class for all plot objects."""

    PALETTE = [
        # tslumen theme color
        "#a09ebb",
        # From bokeh palettes.Colorblind8
        "#0072B2",
        "#E69F00",
        "#F0E442",
        "#009E73",
        "#56B4E9",
        "#D55E00",
        "#CC79A7",
        "#000000",
        # From bokeh palettes.Category10
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    # See https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/mpl-data/stylelib/
    rc_params = {
        "figure.facecolor": "white",
        "text.color": ".15",
        "axes.labelcolor": ".15",
        "legend.frameon": False,
        "legend.numpoints": 1,
        "legend.scatterpoints": 1,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.color": ".15",
        "ytick.color": ".15",
        "axes.axisbelow": True,
        "image.cmap": "Greys",
        "font.family": ["sans-serif"],
        "font.sans-serif": [
            "Segoe UI",
            "Roboto",
            "Helvetica Neue",
            "Arial",
            "Liberation Sans",
            "Bitstream Vera Sans",
            "sans-serif",
        ],
        "grid.linestyle": "-",
        "lines.solid_capstyle": "round",
        # Seaborn white parameters
        "axes.grid": False,
        "axes.facecolor": "white",
        "axes.edgecolor": "0.15",
        "axes.linewidth": 0.75,
        "grid.color": "0.8",
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.minor.size": 0,
        "ytick.minor.size": 0,
        # custom
        "font.size": 8.0,
        "figure.edgecolor": "0.50",
        "patch.antialiased": True,
        "axes.labelsize": 9,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
    }
    _wrap_width: int = 15
    _wrap_placeholder: str = "..."

    def shorten(self, text: str) -> str:
        """Util function for shortening text -- useful for fitting large strings in small plots.
        A wrapper of ``textwrap``'s ``shorten`` function, where ``width`` and ``placeholder`` are
        configured centrally in this class and thus inherited by all subclasses.

        Args:
            text (str): The text to shorten.

        Returns:
            str: The shortened text.
        """
        return textwrap.shorten(text, width=self._wrap_width, placeholder=self._wrap_placeholder)

    def wrap(self, text: str) -> str:
        """Util function for wrapping text -- useful for fitting large strings in small plots.
        A wrapper of ``textwrap``'s ``wrap`` function, where ``width`` is configured centrally in
        this class and thus inherited by all subclasses.

        Args:
            text (str): The text to wrap.

        Returns:
            str: The wrapped text.
        """
        return "\n".join(textwrap.wrap(text, width=self._wrap_width))

    @property
    @abstractmethod
    def _plot(self) -> plt.figure:
        pass

    @property
    def plot(self) -> plt.figure:
        """
        Returns:
           plt.figure: The plotted object.
        """
        with self.mplcontext():
            return self._plot

    @contextlib.contextmanager
    def mplcontext(self) -> Generator:
        """
        Returns:
            Generator: The context in which to create the matplotlib figure, which ensures the
            right parameters are appropriately set, registers the necessary converters, etc.
        """
        original = mpl.rcParams.copy()
        try:
            mpl.rcParams.update(self.rc_params)
            register_matplotlib_converters()
            yield
        finally:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=mpl.cbook.mplDeprecation)
                mpl.rcParams.update(original)

    def _savefig(self, *args: Any, **kwargs: Any) -> bytes:
        with BytesIO() as buffer:
            fig = self.plot
            fig.savefig(buffer, *args, **kwargs)
            data = buffer.getvalue()
            return data

    def to_svg(self) -> str:
        """
        Returns:
            str: Figure rendered in SVG format.
        """
        data = self._savefig(format="svg")
        return data.decode("utf8")

    def to_png(self, **kwargs: Any) -> str:
        """
        Returns:
            str: Figure rendered in PNG format.
        """
        kwargs.pop("format", None)
        kwargs["dpi"] = kwargs.get("dpi", 100)
        data = self._savefig(format="png", **kwargs)
        return base64.b64encode(data).decode("utf-8")

    def _repr_html_(self) -> str:
        return f'<img src="data:image/png;base64,{self.to_png()}" />'
