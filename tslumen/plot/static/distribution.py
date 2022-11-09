"""Distribution plots."""
from typing import Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tslumen.plot.static.base import Figure


__all__ = ["Distribution", "BoxPlot"]


@dataclass
class Distribution(Figure):
    """Combined Histogram, P-P and Q-Q plots."""

    series: pd.Series
    df_quantiles: pd.DataFrame
    df_percentiles: pd.DataFrame
    col_theoretical_quantiles: str = "theoretical_quantiles"
    col_sample_quantiles: str = "sample_quantiles"
    col_qq_ref = "reference"
    col_theoretical_percentiles: str = "theoretical_percentiles"
    col_sample_percentiles: str = "sample_percentiles"
    col_pp_ref = "reference"
    figsize: Tuple[float, float] = (8, 6)

    def _pplot(
        self,
        ax: plt.Axes,
        x: pd.Series,
        y: pd.Series,
        reference: pd.Series,
        xlabel: str,
        ylabel: str,
    ) -> None:
        ax.plot(x, y, "o", color=self.PALETTE[0])
        ax.plot(x, reference, color="blue")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    @property
    def _plot(self) -> plt.figure:
        fig = plt.figure(figsize=self.figsize)
        layout = (2, 2)

        ax_hist = plt.subplot2grid(layout, (0, 0), colspan=2)
        ax_qq = plt.subplot2grid(layout, (1, 0))
        ax_pp = plt.subplot2grid(layout, (1, 1))

        ax_hist.bar(
            self.series.index,
            self.series.values,
            width=0.75 * np.diff(self.series.index).mean(),
            color=self.PALETTE[0],
        )
        ax_hist.spines["top"].set_visible(False)
        ax_hist.spines["right"].set_visible(False)

        self._pplot(
            ax=ax_qq,
            x=self.df_quantiles[self.col_theoretical_quantiles],
            y=self.df_quantiles[self.col_sample_quantiles],
            reference=self.df_quantiles[self.col_qq_ref],
            xlabel="Theoretical Quantiles",
            ylabel="Sample Quantiles",
        )

        self._pplot(
            ax=ax_pp,
            x=self.df_percentiles[self.col_theoretical_percentiles],
            y=self.df_percentiles[self.col_sample_percentiles],
            reference=self.df_percentiles[self.col_pp_ref],
            xlabel="Theoretical Percentiles",
            ylabel="Sample Percentiles",
        )
        ax_pp.set_xlim([0.0, 1.0])
        ax_pp.set_ylim([0.0, 1.0])

        plt.tight_layout()
        plt.close(fig)
        return fig


@dataclass
class BoxPlot(Figure):
    """BoxPlot w/ whiskers."""

    df: pd.DataFrame
    figsize: Tuple[float, float] = (8, 3)

    @property
    def _plot(self) -> plt.figure:
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(1, 1, 1)
        props = dict(linewidth=0.75)
        ax.boxplot(
            self.df,
            labels=self.df.columns,
            sym=self.PALETTE[0],
            medianprops={"linewidth": 1, "color": self.PALETTE[0]},
            boxprops=props,
            capprops=props,
            whiskerprops=props,
        )
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")
        if self.df.shape[1] > 20:
            xticks = ax.xaxis.get_major_ticks()
            for n in range(1, len(xticks), 2):
                xticks[n].label1.set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        plt.close(fig)
        return fig
