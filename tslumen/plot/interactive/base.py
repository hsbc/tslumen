"""Base classes and functions for the interactive plots package"""
from typing import Optional, Any, Type
from collections.abc import Mapping
from abc import ABC, abstractmethod
from copy import deepcopy
import inspect

try:
    import plotly.graph_objs as go
    from plotly.colors import qualitative as palettes
    from plotly.subplots import make_subplots
except ImportError:
    from tslumen.misc import import_error_module, import_error_function

    go = import_error_module("plotly")
    palettes = import_error_module("plotly")
    make_subplots = import_error_function("plotly")

__all__ = ["dict_deep_update", "VizBase"]


def dict_deep_update(original: dict, *update: Mapping) -> dict:
    """Same as built-in dict.update, but deals with nesting

    Args:
        original (dict): Dictionary on which to apply the updates.
        update (dict): Dictionary with the updates to apply to `original`.

    Returns:
        dict: Updated dictionary.
    """

    def _dict_update(original_: dict, update_: Mapping) -> dict:
        for key, val in update_.items():
            if isinstance(val, Mapping):
                original_[key] = _dict_update(original_.get(key, {}), val)
            else:
                original_[key] = val
        return original_

    updated: dict = deepcopy(original)
    for up_ in update:
        updated = _dict_update(updated, up_)
    return updated


class VizBase(ABC):
    """Base for all Viz classes."""

    PALETTE = ["#a09ebb"]

    COLORBAR_POSITION = {
        "left": {"xanchor": "right", "yanchor": "bottom", "y": 0, "x": -0.1},
        "right": {"xanchor": "left", "yanchor": "bottom", "y": 0, "x": 1},
        "bottom": {"xanchor": "left", "yanchor": "top", "y": -0.2, "x": 0},
        "top": {"xanchor": "left", "yanchor": "bottom", "y": 1, "x": 0},
        "middle_left": {"xanchor": "left", "yanchor": "bottom", "y": 0, "x": 0},
        "middle_right": {"xanchor": "right", "yanchor": "bottom", "y": 0, "x": 1},
    }

    LEGEND_POSITION = {
        "left": {
            "xanchor": "right",
            "yanchor": "top",
            "orientation": "v",
            "y": 1,
            "x": -0.08,
        },
        "right": {
            "xanchor": "left",
            "yanchor": "top",
            "orientation": "v",
            "y": 1,
            "x": 1,
        },
        "bottom": {
            "xanchor": "left",
            "yanchor": "top",
            "orientation": "h",
            "y": -0.2,
            "x": 0,
        },
        "top": {
            "xanchor": "left",
            "yanchor": "bottom",
            "orientation": "h",
            "y": 1,
            "x": 0,
        },
        "top_left": {
            "xanchor": "left",
            "yanchor": "top",
            "orientation": "v",
            "y": 0.97,
            "x": 0.004,
        },
        "top_right": {
            "xanchor": "right",
            "yanchor": "top",
            "orientation": "v",
            "y": 0.97,
            "x": 0.996,
        },
        "bottom_left": {
            "xanchor": "left",
            "yanchor": "bottom",
            "orientation": "v",
            "y": 0.03,
            "x": 0.004,
        },
        "bottom_right": {
            "xanchor": "right",
            "yanchor": "bottom",
            "orientation": "v",
            "y": 0.03,
            "x": 0.996,
        },
    }

    VIZBASE_LAYOUT_OPTS = {
        "hovermode": "closest",
        "plot_bgcolor": "#ffffff",
        "font_family": '"Segoe UI", "Helvetica Neue", Helvetica, sans-serif',
        "margin": {"l": 10, "r": 10, "b": 10, "t": 10},
        "title": {"x": 0.5, "y": 0.99, "yanchor": "top", "xanchor": "center"},
        "xaxis": {
            "linecolor": "#678",
            "showgrid": True,
            "gridcolor": "#ddd",
            "zeroline": False,
        },
        "yaxis": {
            "linecolor": "#678",
            "showgrid": True,
            "gridcolor": "#ddd",
            "zeroline": False,
        },
    }

    def __init__(
        self, title: str = "", width: Optional[int] = None, height: int = 400, **layout_opts: Any
    ) -> None:
        self.PALETTE += palettes.Vivid + palettes.Plotly
        self.__plot: Any = None
        self.title = title
        self.width = width
        self.height = height
        self.layout_opts = layout_opts

    @staticmethod
    def extend_init(klass: Type) -> Type:
        """Decorator to fix sig+docs of subclasses passing kwargs to super"""
        sig_klass = inspect.signature(klass.__init__)
        params = [p for p in sig_klass.parameters.values() if p.name != "kwargs"]
        for base in klass.__bases__:
            base_init = getattr(base, "__init__", None)
            if base_init:
                sig_base = inspect.signature(base_init)
                params += [
                    p
                    for p in sig_base.parameters.values()
                    if p.name not in sig_klass.parameters.keys()
                ]
        klass.__init__.__signature__ = sig_klass.replace(parameters=params)
        return klass

    @staticmethod
    def _listw(item: Any) -> list:
        """Wraps item around a list"""
        return [] if item is None else item if isinstance(item, list) else [item]

    @staticmethod
    def _pfix(
        original: Any,
        default: Any,
        exclude: Any = None,
        fill: Any = None,
        size: Optional[int] = None,
    ) -> Any:
        """Return a list that is a combination of the `original` and `default`
        values.

        Args:
            original: Original values that is placed first in the return list.
            default: Default values in return list if `original` values is not specified.
            exclude: Values that should not be in the return list.
            fill: Values that should be added to return list to meet list `size` requirement.
            size: Max size of the return list. Default value is the length of `default`.
        """
        exclude = exclude or {}
        dsize = size or len(default)
        original = VizBase._listw(original)
        if not original:
            for cdef in default:
                if cdef not in exclude:
                    original.append(cdef)
                if len(original) >= dsize:
                    break
        if fill:
            original += fill[len(original) :]
            original = original[: len(fill)]
        if size:
            original *= size
            original = original[:size]
        return original

    def _ipython_display_(self) -> None:
        self.plot.show(config={"displaylogo": False})

    @property
    def plot(self) -> go.Figure:
        """
        Returns:
            Plotly object representing the actual plot.
        """
        if not self.__plot:
            self.__plot = self._create_plot()
        return self.__plot

    @property
    def _base_opts(self) -> dict:
        return {}

    @abstractmethod
    def _create_figure(self) -> go.Figure:
        pass

    def _create_plot(self) -> go.Figure:
        fig = self._create_figure()
        return self._apply_base_opts(fig)

    def _apply_base_opts(self, plot: go.Figure, *overrides: dict) -> go.Figure:
        calc_opts = {
            "width": self.width,
            "height": self.height,
            "title": {"text": self.title},
        }
        opts = dict_deep_update(
            self.VIZBASE_LAYOUT_OPTS, calc_opts, self._base_opts, self.layout_opts, *overrides
        )
        return plot.update_layout(**opts)
