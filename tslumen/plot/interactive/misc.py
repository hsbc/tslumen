"""Miscellaneous plots."""
from typing import Any

import pandas as pd

from tslumen.plot.interactive.base import go
from tslumen.plot.interactive.comparison import Heatmap
from tslumen.plot.utils import cmapper, cmap_to_list, ccontrast


__all__ = ["GrangerMatrix"]


@Heatmap.extend_init
class GrangerMatrix(Heatmap):
    """Granger causality matrix."""

    def __init__(
        self,
        data: pd.DataFrame,
        dfl: pd.DataFrame,
        critical: float = 0.05,
        cmap: str = "PuBu_r",
        bg_reject: str = "#ffffff",
        fg_reject: str = "#dddddd",
        labels_format: str = "{:.5f}",
        hovertemplate: str = "<b>%{x} => %{y}</b>: %{z}<extra></extra>",
        xrotation: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            data=data,
            colorbar_limit=(0, critical),
            colorbar=False,
            cmap=cmap_to_list(cmap, 9) + [bg_reject],
            xrotation=xrotation,
            labels_format=labels_format,
            hovertemplate=hovertemplate,
            **kwargs,
        )
        self.dfl = dfl
        self.critical = critical
        self.accept_cmap = cmap
        self.fg_reject = fg_reject

    def _annotate(self) -> None:
        df = self.data
        cmap = cmapper(
            self.colorbar_limit[0], self.colorbar_limit[1], self.accept_cmap, as_hex=False
        )
        self._annotations = []
        for i, row in enumerate(df.values):
            for j, val in enumerate(row):
                if not val or val != val:
                    continue
                *bg, _ = cmap(val)
                fg = ccontrast(*bg) if val < self.critical else self.fg_reject
                lag = self.dfl.iloc[i, j]
                self._annotations.append(
                    go.layout.Annotation(
                        text=self.labels_format.format(val) + f"<br>lag: {lag}",
                        font=dict(color=fg, size=10),
                        x=df.columns[j],
                        y=df.index[i],
                        xref="x1",
                        yref="y1",
                        showarrow=False,
                    )
                )
