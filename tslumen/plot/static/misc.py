"""Miscellaneous plots."""
from typing import Tuple, Callable
import warnings
from dataclasses import dataclass

import pandas as pd
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

from tslumen.plot.static.base import Figure


__all__ = ["GrangerMatrix", "GrangerGraph"]


@dataclass
class GrangerMatrix(Figure):
    """Granger causality matrix."""

    dfl: pd.DataFrame
    dfp: pd.DataFrame
    figsize: Tuple[float, float] = (0.8, 0.4)
    min_figsize: Tuple[float, float] = (8, 4)
    critical: float = 0.05

    @property
    def _plot(self) -> plt.figure:
        nvars = len(self.dfp)
        figsize = max(self.min_figsize, (self.figsize[0] * nvars, self.figsize[1] * nvars))
        fig = plt.figure(figsize=figsize)
        layout = (nvars, nvars)

        norm_reject = mpl.colors.Normalize(vmin=self.critical, vmax=1, clip=True)
        norm_accept = mpl.colors.Normalize(vmin=0, vmax=self.critical, clip=True)
        mapper_reject = mpl.cm.ScalarMappable(norm=norm_reject, cmap="Greys")
        mapper_accept = mpl.cm.ScalarMappable(norm=norm_accept, cmap="PuBu_r")

        for i, a in enumerate(self.dfp.index):
            for j, b in enumerate(self.dfp.columns):
                ax = plt.subplot2grid(layout, (i, j))

                if i == nvars - 1:
                    label = self.shorten(b[:-3]) + b[-3:]
                    ax.set_xlabel(label, rotation=30, ha="right", rotation_mode="anchor")
                    ax.tick_params(axis="x", which="both", labelbottom=False, bottom=False)
                else:
                    ax.xaxis.set_visible(False)

                if j == 0:
                    label = self.shorten(a[:-3]) + a[-3:]
                    ax.set_ylabel(label, rotation=30, ha="right", rotation_mode="anchor")
                    ax.tick_params(axis="y", which="both", labelleft=False, left=False)
                else:
                    ax.yaxis.set_visible(False)

                if i == j:
                    ax.set_facecolor("black")
                    continue

                pval = self.dfp.loc[a, b]
                lag = self.dfl.loc[a, b]
                if pval < self.critical:
                    color = mapper_accept.to_rgba(pval)
                    acolor = "black" if pval > (self.critical / 2.0) else "white"
                else:
                    color = mapper_reject.to_rgba(pval)
                    acolor = (
                        "#aaaaaa"
                        if pval > ((1 - self.critical) / 2.0 + self.critical)
                        else "#888888"
                    )
                ax.set_facecolor(color)
                ax.text(
                    0.5,
                    0.6,
                    f"{pval:.5f}",
                    color=acolor,
                    fontsize=9,
                    transform=ax.transAxes,
                    horizontalalignment="center",
                    verticalalignment="center",
                )
                ax.text(
                    0.5,
                    0.25,
                    f"lag: {lag:d}",
                    color=acolor,
                    fontsize=7,
                    transform=ax.transAxes,
                    horizontalalignment="center",
                    verticalalignment="center",
                )

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            plt.tight_layout()
        fig.subplots_adjust(wspace=0, hspace=0)
        plt.close(fig)
        return fig


@dataclass
class GrangerGraph(Figure):
    """Granger causality graph."""

    dfp: pd.DataFrame
    figsize: Tuple[float, float] = (8, 6)
    critical: float = 0.05
    cmap: str = "PuBu_r"
    node_color: str = "white"
    edgecolors: str = "#555555"
    edge_hi: str = "#b60982"

    @property
    def _plot(self) -> plt.figure:
        alpha_: Callable[[tuple], list] = lambda rgba: list(rgba[:-1]) + [0.15]
        edges = []
        edges_h = []
        for y in self.dfp.index:
            s = self.dfp.loc[y].sort_values()
            if s[0] < self.critical:
                n_x, n_y = s.index[0][:-3], y[:-3]
                edges_h.append((self.wrap(n_x), self.wrap(n_y)))
            for x in self.dfp.columns:
                pval = self.dfp.loc[y, x]
                if pval < self.critical:
                    n_x, n_y = x[:-3], y[:-3]
                    edges.append((self.wrap(n_x), self.wrap(n_y), pval))
        weights = sorted([e[2] for e in edges])
        if len(edges) < 1:
            fig = plt.figure(figsize=(0.5, 0.5))
            plt.close(fig)
            return fig
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(1, 1, 1)

        vmin, vmax = weights[0], weights[-1]
        mapper = mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=vmin, vmax=vmax, clip=True), cmap=self.cmap
        )

        g = nx.DiGraph()
        g.add_weighted_edges_from(edges)
        pos = nx.circular_layout(g)
        nx.draw(
            g,
            pos=pos,
            with_labels=True,
            node_color=self.node_color,
            edgecolors=self.edgecolors,
            node_size=4500,
            font_size=8,
            edge_color=[alpha_(mapper.to_rgba(e[2]["weight"])) for e in g.edges(data=True)],
            width=[(self.critical - e[2]["weight"]) * 30 for e in g.edges(data=True)],
            ax=ax,
        )
        nx.draw_networkx_edges(
            g,
            pos=pos,
            edgelist=edges_h,
            node_size=4500,
            edge_color=self.edge_hi,
            width=1,
            alpha=0.75,
            ax=ax,
        )
        plt.tight_layout()
        plt.close(fig)
        return fig
