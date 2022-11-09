"""Correlation plots."""
from typing import Tuple, Optional
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
import matplotlib as mpl
import matplotlib.pyplot as plt

from tslumen.plot.static.base import Figure


__all__ = [
    "LagCorrelation",
    "LagMatrix",
    "ScatterMatrix",
]


@dataclass
class LagCorrelation(Figure):
    """Lag correlation (ACF/PACF) plots, commonly known as lollipop, for analysing correlation on
    a given lag. Useful for auto-, partial-, cross- and partial-cross-correlation.
    """

    df: pd.DataFrame
    title: Optional[str] = None
    col_lag: str = "lag"
    col_correlation: str = "correlation"
    col_up: str = "up"
    col_low: str = "low"
    figsize: Tuple[float, float] = (3.3, 2)

    @property
    def _plot(self) -> plt.figure:
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(1, 1, 1)

        lag = self.df[self.col_lag]
        corr = self.df[self.col_correlation]
        up = self.df[self.col_up]
        low = self.df[self.col_low]

        ax.vlines(lag, [0], corr, color="0.1")
        ax.axhline(color="0")
        ax.plot(lag, corr, marker="o", markersize=4, linestyle="None", color=self.PALETTE[0])
        ax.fill_between(lag, up, low, alpha=0.25, color=self.PALETTE[0])
        if self.title:
            ax.set_title(self.title)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        plt.close(fig)
        return fig


@dataclass
class LagMatrix(Figure):
    """Lag Matrix plot."""

    original: pd.Series
    lags: pd.DataFrame
    corr: pd.Series
    ncols: int = 4
    cellsize: Tuple[float, ...] = (1.7, 1.7)

    @property
    def _plot(self) -> plt.figure:
        ncols = self.ncols
        nrows = int(np.ceil(self.lags.shape[1] / ncols))
        fig = plt.figure(figsize=(self.cellsize[0] * ncols, self.cellsize[1] * nrows))
        layout = (nrows, ncols)

        for ix, col in enumerate(self.lags.columns):
            ix_row = ix // ncols
            ix_col = ix % ncols
            ax = plt.subplot2grid(layout, (ix_row, ix_col))
            ax.plot(
                self.original,
                self.lags[col],
                marker="o",
                markersize=1,
                linestyle="None",
                color=self.PALETTE[0],
            )
            if ix_col > 0:
                ax.tick_params(axis="y", which="both", labelleft=False, left=False)
            if ix_row > 0:
                ax.tick_params(axis="x", which="both", labelbottom=False, bottom=False)
            else:
                ax.tick_params(
                    axis="x",
                    which="both",
                    labelbottom=False,
                    bottom=False,
                    labeltop=True,
                    top=True,
                )
            ax.text(
                0.5,
                0.5,
                f"{col}: {self.corr[col]:.3f}",
                transform=ax.transAxes,
                horizontalalignment="center",
                verticalalignment="center",
                bbox=dict(facecolor="white", alpha=0.75, linewidth=0),
            )
        plt.tight_layout()
        plt.close(fig)
        return fig


@dataclass
class ScatterMatrix(Figure):
    """Scatter matrix (aka pair plot) with scatters, KDE and correlation Heatmap."""

    df: pd.DataFrame
    df_corr: pd.DataFrame
    figsize: Tuple[float, float] = (0.8, 0.8)
    min_figsize: Tuple[float, float] = (8, 8)

    @property
    def _plot(self) -> plt.figure:
        ncols = self.df.shape[1]
        figsize = max(self.min_figsize, (self.figsize[0] * ncols, self.figsize[1] * ncols))
        fig = plt.figure(figsize=figsize)
        layout = (ncols, ncols)
        minima = -1.0
        maxima = 1.0
        thresh = 0.0

        norm = mpl.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
        mapper = mpl.cm.ScalarMappable(norm=norm, cmap="PuBu")

        for i, a in enumerate(self.df.columns):
            for j, b in enumerate(self.df.columns):
                ax = plt.subplot2grid(layout, (i, j))
                ax.xaxis.set_visible(False)
                ax.yaxis.set_visible(False)
                corr = self.df_corr.loc[a, b]
                color = mapper.to_rgba(corr)
                acolor = "black" if corr < thresh else "white"
                xcolor = mapper.to_rgba(0.7) if corr < thresh else mapper.to_rgba(0)
                if i > j:
                    ax.plot(
                        self.df[b],
                        self.df[a],
                        marker="o",
                        color=color,
                        markersize=2,
                        linestyle="None",
                        alpha=0.5,
                        markeredgewidth=0.1,
                        markeredgecolor=xcolor,
                    )
                elif i < j:
                    ax.set_facecolor(color)
                    ax.text(
                        0.5,
                        0.5,
                        f"{corr:.3f}",
                        color=acolor,
                        fontsize=8,
                        transform=ax.transAxes,
                        horizontalalignment="center",
                        verticalalignment="center",
                    )

        for i, a in enumerate(self.df.columns):
            ax = plt.subplot2grid(layout, (i, i))
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)
            kde = gaussian_kde(self.df[a].dropna())
            sp = np.linspace(self.df[a].dropna().min(), self.df[a].dropna().max(), 1000)
            ax.plot(sp, kde.evaluate(sp), color=self.PALETTE[0], linewidth=0.75)
            ax.text(
                0.5,
                0.5,
                a,
                fontsize=8,
                transform=ax.transAxes,
                horizontalalignment="center",
                verticalalignment="center",
                rotation=45,
                bbox=dict(facecolor="white", alpha=0.7, linewidth=0),
            )

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.tight_layout()
        fig.subplots_adjust(wspace=0, hspace=0)
        plt.close(fig)
        return fig
