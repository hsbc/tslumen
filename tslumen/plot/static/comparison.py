"""Comparison plots."""
from typing import Tuple, Any
from dataclasses import dataclass
from itertools import cycle

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.ticker import StrMethodFormatter

from tslumen.plot.static.base import Figure


__all__ = ["Radar", "Heatmap"]


def _radar_factory(num_vars: int) -> np.ndarray:
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):  # type: ignore
        """For projecting to a radial axis based on
        https://matplotlib.org/stable/gallery/specialty_plots/radar_chart.html"""

        name = "radar"

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location("N")

        def fill(self, *args: Any, closed: bool = True, **kwargs: Any) -> Any:
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args: Any, **kwargs: Any) -> None:
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line: Any) -> None:
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels: Any) -> None:
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self) -> Circle:
            return Circle((0.5, 0.5), 0.5)

    register_projection(RadarAxes)
    return theta


@dataclass
class Radar(Figure):
    """Radar (aka spider) plot for comparing data bearing multiple dimensions."""

    df: pd.DataFrame
    nticks: int = 5
    figsize: Tuple[float, float] = (2.1, 2.1)
    linewidth: float = 0.75
    alpha: float = 0.45
    legend: bool = False

    @property
    def _plot(self) -> plt.figure:
        theta = _radar_factory(len(self.df))
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(1, 1, 1, projection="radar")

        ylo = np.round(self.df.min().min(), 2)
        yhi = np.round(self.df.max().max(), 2)
        ax.set_rgrids(np.round(np.linspace(ylo, yhi, num=self.nticks), 2))
        colors = cycle(self.PALETTE)
        for i, col in enumerate(self.df.columns):
            color = next(colors)
            ax.plot(
                theta,
                self.df[col].values,
                color=color,
                linewidth=self.linewidth,
            )
            ax.fill(theta, self.df[col].values, color=color, alpha=self.alpha)
        ax.set_varlabels(self.df.index)
        if self.legend:
            ax.legend(self.df.columns, loc=(0.9, 0.9), labelspacing=0.1, fontsize="small")

        plt.tight_layout()
        plt.close(fig)
        return fig


@dataclass
class Heatmap(Figure):
    """Heatmap plot."""

    df: pd.DataFrame
    figsize: Tuple[float, float] = (4, 0.45)
    min_figsize: Tuple[float, float] = (4, 4)
    cmap: str = "PuBu"
    valfmt: str = "{x:.3f}"
    textcolors: Tuple[str, ...] = ("black", "white")

    @property
    def _plot(self) -> plt.figure:
        nrows, ncols = self.df.shape
        figsize = max((self.figsize[0], self.figsize[1] * nrows), self.min_figsize)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1, 1, 1)

        im = ax.imshow(self.df.values, cmap=self.cmap)

        ylabels = [self.shorten(label) for label in self.df.index]
        ax.set_yticks(np.arange(nrows))
        ax.set_yticklabels(ylabels)
        ax.set_yticks(np.arange(nrows + 1) - 0.5, minor=True)

        ax.set_xticks(np.arange(ncols))
        ax.set_xticklabels(self.df.columns)
        ax.set_xticks(np.arange(ncols + 1) - 0.5, minor=True)
        ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
        plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")

        threshold = im.norm(self.df.max().max()) / 2.0
        valfmt = StrMethodFormatter(self.valfmt)
        kw = dict(horizontalalignment="center", verticalalignment="center")
        for i in range(nrows):
            for j in range(ncols):
                val = self.df.iloc[i, j]
                kw.update(color=self.textcolors[int(im.norm(val) > threshold)])
                im.axes.text(j, i, valfmt(val, None), **kw)

        plt.tight_layout()
        plt.close(fig)
        return fig
