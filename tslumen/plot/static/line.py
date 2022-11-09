"""Line plots."""
from typing import Tuple, Optional, List, Union
from dataclasses import dataclass
from itertools import cycle

import pandas as pd
import matplotlib.pyplot as plt

from tslumen.plot.utils import cmap_to_list
from tslumen.plot.static.base import Figure


__all__ = ["TS", "TSStack"]


@dataclass
class TS(Figure):
    """Time series line plot."""

    df: pd.DataFrame
    figsize: Tuple[float, float] = (8, 3)
    xaxis: bool = True
    yaxis: bool = True
    legend: bool = True
    line_width: Optional[List[float]] = None
    colors: Optional[Union[str, List[str]]] = None

    @property
    def _plot(self) -> plt.figure:
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(1, 1, 1)
        ncols = self.df.shape[1]
        line_width = (self.line_width or []) + [1] * ncols
        if isinstance(self.colors, str):
            colors = cycle(cmap_to_list(self.colors, self.df.shape[1]))
        else:
            colors = cycle((self.colors or []) + self.PALETTE)
        for ix, col in enumerate(self.df.columns):
            ax.plot(
                self.df.index,
                self.df[col],
                label=col,
                linewidth=line_width[ix],
                color=next(colors),
            )
        fig.autofmt_xdate()
        if self.df.shape[1] > 20:
            xticks = ax.xaxis.get_major_ticks()
            for n in range(1, len(xticks), 2):
                xticks[n].label1.set_visible(False)

        if not self.yaxis:
            ax.tick_params(axis="y", which="both", labelleft=False, left=False)
        if not self.xaxis:
            ax.tick_params(axis="x", which="both", labelbottom=False, bottom=False)

        plt.tight_layout()
        if self.legend:
            box = ax.get_position()
            x0 = box.x0 if self.yaxis else 0.05
            y0 = box.y0 if self.xaxis else 0.05
            width = box.width * 0.75
            height = box.height
            ax.set_position([x0, y0, width, height])
            fontsize = ["medium", "small", "x-small", "xx-small"][min(max(0, ncols - 14), 3)]
            ax.legend(bbox_to_anchor=(1, 1), loc="upper left", fontsize=fontsize)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.close(fig)
        return fig


@dataclass
class TSStack(Figure):
    """Stacked time series line plot."""

    df: pd.DataFrame
    figsize: Tuple[float, float] = (10, 3)

    @property
    def _plot(self) -> plt.figure:
        fig = plt.figure(figsize=self.figsize)
        layout = (self.df.shape[1], 1)

        for ix, col in enumerate(self.df.columns):
            ax = plt.subplot2grid(layout, (ix, 0))
            ax.plot(self.df.index, self.df[col], linewidth=0.75, color=self.PALETTE[0])
            ax.set_ylabel(col)
        plt.tight_layout()
        plt.close(fig)
        return fig
