"""Correlation plots."""
from typing import Union, Optional, Any
from copy import deepcopy

import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde

from tslumen.plot.interactive.base import VizBase, go, make_subplots
from tslumen.plot.utils import cmapper


__all__ = ["LagCorrelation", "LagMatrix", "ScatterMatrix"]


@VizBase.extend_init
class LagCorrelation(VizBase):
    """Lag correlation (ACF/PACF) plots, commonly known as lollipop, for analysing correlation on
    a given lag. Useful for auto-, partial-, cross- and partial-cross-correlation.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        col_corr: Optional[str] = "correlation",
        col_lag: Optional[str] = "lag",
        col_up_bound: Optional[str] = "up",
        col_lo_bound: Optional[str] = "low",
        label_corr: Optional[str] = None,
        label_lag: Optional[str] = None,
        label_up_bound: Optional[str] = None,
        label_lo_bound: Optional[str] = None,
        label_xaxis: str = "Lag",
        label_yaxis: str = "Correlation",
        color_area: str = "rgba(160, 158, 187, 0.25)",
        color_vlines: str = "black",
        color_up_bound: str = VizBase.PALETTE[0],
        color_lo_bound: str = VizBase.PALETTE[0],
        color_circle: str = VizBase.PALETTE[0],
        scatter_size: int = 6,
        vlines_width: float = 2,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            data (pd.DataFrame): Dataframe with lag, correlation and optionally upper and lower CI.
            col_corr (str): Name of the correlation column.
            col_lag (str): Name of the lag column.
            col_up_bound (str): Name of the upper boundary column.
            col_lo_bound (str): Name of the lower boundary column.
            label_corr (str): Label for the correlation, defaults to `col_corr` if not provided.
            label_lag (str): Label for the lag, defaults to `col_lag` if not provided.
            label_up_bound (str): Label for the upper boundary, defaults to `col_up_bound`.
            label_lo_bound (str): Label for the upper boundary, defaults to `col_lo_bound`.
            legend_position (str): Where to position the legend, default 'right'.
            label_xaxis (str): X-axis label, default 'Lag'.
            label_yaxis (str): Y-axis label, default 'Correlation'.
            color_area (str): Color of the shaded area between the boundaries.
            color_vlines (str): Color of the vertical lines/spikes.
            color_up_bound (str): Color of the upper boundary line.
            color_lo_bound (str): Color of the lower boundary line.
            color_circle (str): Color of the scatter points.
            scatter_size (float): Size of the scatter points, default 6.
            vlines_width (float): Width of the vertical lines/spikes, default 2.
        """
        super().__init__(**kwargs)
        self._data = data

        self._col_corr = col_corr
        self._col_lag = col_lag
        self._col_up_bound = col_up_bound
        self._col_lo_bound = col_lo_bound

        self._label_corr = label_corr if label_corr else self._col_corr
        self._label_lag = label_lag if label_lag else self._col_lag
        self._label_up_bound = label_up_bound if label_up_bound else self._col_up_bound
        self._label_lo_bound = label_lo_bound if label_lo_bound else self._col_lo_bound

        self._label_xaxis = label_xaxis
        self._label_yaxis = label_yaxis

        self._color_area = color_area
        self._color_vlines = color_vlines
        self._color_up_bound = color_up_bound
        self._color_lo_bound = color_lo_bound
        self._color_circle = color_circle

        self._scatter_size = scatter_size
        self._vlines_width = vlines_width

        self._padding = 0.1
        self._h_line_width = 1
        self._h_line_color = "black"

    def _create_figure(self) -> go.Figure:
        fig = go.Figure()

        fig.add_shape(
            x0=0,
            y0=0,
            x1=1,
            y1=0,
            xref="paper",
            yref="y",
            line={"color": self._h_line_color, "width": self._h_line_width},
        )

        data = self._data

        if self._col_lo_bound in data.columns and self._col_up_bound in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data[self._col_lag],
                    y=data[self._col_up_bound],
                    mode="lines",
                    hovertemplate=f"<b>{self._label_lag}</b>: "
                    "%{x}<br>"
                    f"<b>{self._label_up_bound}</b>: "
                    "%{y}<extra></extra>",
                    name=self._label_up_bound,
                    line={"color": self._color_up_bound},
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=data[self._col_lag],
                    y=data[self._col_lo_bound],
                    mode="none",
                    hoverinfo="skip",
                    name=self._label_lo_bound,
                    line={"color": self._color_lo_bound},
                    fillcolor=self._color_area,
                    showlegend=False,
                    fill="tonexty",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=data[self._col_lag],
                    y=data[self._col_lo_bound],
                    mode="lines",
                    hovertemplate=f"<b>{self._label_lag}</b>: "
                    "%{x}<br>"
                    f"<b>{self._label_lo_bound}</b>: "
                    "%{y}<extra></extra>",
                    name=self._label_lo_bound,
                    line={"color": self._color_lo_bound},
                )
            )

        for lag, corr in data[[self._col_lag, self._col_corr]].values:
            fig.add_shape(
                type="line",
                xref="x",
                yref="y",
                x0=lag,
                y0=0,
                x1=lag,
                y1=corr,
                line={"color": self._color_vlines, "width": self._vlines_width},
                layer="below",
            )

        fig.add_trace(
            go.Scatter(
                x=data[self._col_lag],
                y=data[self._col_corr],
                hovertemplate=f"<b>{self._label_lag}</b>: "
                "%{x}<br>"
                f"<b>{self._label_corr}</b>: "
                "%{y}<extra></extra>",
                mode="markers",
                name=self._label_corr,
                marker={"color": self._color_circle, "size": self._scatter_size},
            )
        )

        return fig

    @property
    def _base_opts(self) -> dict:
        return {
            "margin": {"l": 30, "r": 30, "b": 10, "t": 30},
            "xaxis": {"showgrid": False, "zeroline": False, "title": self._label_xaxis},
            "yaxis": {"showgrid": True, "zeroline": True, "title": self._label_yaxis},
            "showlegend": False,
        }


@VizBase.extend_init
class LagMatrix(VizBase):
    """Lag Matrix plot."""

    def __init__(
        self,
        data: pd.DataFrame,
        corr: Union[pd.DataFrame, dict],
        col_original: str = "original",
        ncols: int = 2,
        show_legend: bool = False,
        xrotation: int = 0,
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label_yaxis}</b>: %{y}"
        "<extra></extra>",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.corr = corr
        self.col_original = col_original
        self.ncols = ncols
        self.show_legend = show_legend
        self.xrotation = xrotation
        self.hovertemplate = hovertemplate

    def _create_figure(self) -> go.Figure:
        original = self.data[self.col_original]
        lags = self.data[[c for c in self.data.columns if c != self.col_original]]
        ncols = self.ncols
        nrows = int(np.ceil(lags.shape[1] / ncols))
        color_m = self.PALETTE[0]
        opt_xaxis = deepcopy(self.VIZBASE_LAYOUT_OPTS.get("xaxis", {}))
        opt_yaxis = deepcopy(self.VIZBASE_LAYOUT_OPTS.get("yaxis", {}))

        fig = make_subplots(
            rows=nrows,
            cols=ncols,
            start_cell="top-left",
            shared_xaxes=True,
            shared_yaxes=True,
            horizontal_spacing=0.08,
            vertical_spacing=0.02,
        )
        for ix, col in enumerate(lags.columns):
            ix_row = ix // ncols
            ix_col = ix % ncols
            fig.add_trace(
                go.Scatter(
                    x=original,
                    y=lags[col],
                    meta={"label_xaxis": "level", "label_yaxis": col},
                    mode="markers",
                    marker={"color": color_m},
                    name=col,
                    hovertemplate=self.hovertemplate,
                ),
                row=ix_row + 1,
                col=ix_col + 1,
            )
            fig.update_xaxes(
                {
                    **opt_xaxis,  # type: ignore
                    "visible": True,
                    "tickangle": self.xrotation,
                },
                row=ix_row + 1,
                col=ix_col + 1,
                title_text="",
            )
            fig.update_yaxes(
                {
                    **opt_yaxis,  # type: ignore
                },
                row=ix_row + 1,
                col=ix_col + 1,
                title_text=f"{col}: {self.corr[col]:.3f}",
            )

        return fig

    @property
    def _base_opts(self) -> dict:
        return {
            "showlegend": self.show_legend,
        }


@VizBase.extend_init
class ScatterMatrix(VizBase):
    """Scatter matrix (aka pair plot) with scatters, KDE and correlation Heatmap."""

    def __init__(
        self,
        data: pd.DataFrame,
        corr: pd.DataFrame,
        show_legend: bool = False,
        xrotation: int = 0,
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label_yaxis}</b>: %{y}"
        "<extra></extra>",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.corr = corr
        self.show_legend = show_legend
        self.xrotation = xrotation
        self.hovertemplate = hovertemplate

    def _create_figure(self) -> go.Figure:
        nrows, ncols = self.corr.shape
        opt_xaxis = deepcopy(self.VIZBASE_LAYOUT_OPTS.get("xaxis", {}))
        opt_yaxis = deepcopy(self.VIZBASE_LAYOUT_OPTS.get("yaxis", {}))
        cmap_pos = cmapper(0, 1, cmap="Blues")
        cmap_neg = cmapper(-1, 0, cmap="Purples_r")

        fig = make_subplots(
            rows=nrows,
            cols=ncols,
            start_cell="top-left",
            shared_xaxes=False,
            shared_yaxes=False,
            horizontal_spacing=0,
            vertical_spacing=0,
        )
        ix = 0
        tcolors = []
        annotations = []
        for ix_row in range(nrows):
            for ix_col in range(ncols):
                ix += 1
                col_x = self.data.columns[ix_row]
                col_y = self.data.columns[ix_col]
                corr = self.corr.loc[col_x, col_y]
                color = (cmap_pos if corr > 0 else cmap_neg)(corr)
                if ix_row == ix_col:
                    series = self.data[col_x].dropna()
                    x = np.linspace(series.min(), series.max(), 500)
                    y = gaussian_kde(series).evaluate(x)
                    trace = go.Scatter(
                        x=x,
                        y=y,
                        mode="lines",
                        marker={"color": self.PALETTE[0]},
                        textposition="middle center",
                        name=col_x,
                    )
                    annotations.append((ix, x.mean(), (y.max() + y.min()) / 2, col_x))

                elif ix_row > ix_col:
                    trace = go.Scatter(
                        x=self.data[col_x],
                        y=self.data[col_y],
                        meta={"label_xaxis": col_x, "label_yaxis": col_y},
                        mode="markers",
                        marker={"color": color},
                        textposition="middle center",
                        name=f"{col_x} x {col_y}",
                        hovertemplate=self.hovertemplate,
                    )
                else:
                    tcolors.append((ix, color))
                    trace = go.Scatter(
                        x=[0.5],
                        y=[0.5],
                        mode="text",
                        textposition="middle center",
                        text=[f"{corr: .3f}"],
                        textfont={"color": "black" if abs(corr) < 0.6 else "white"},
                        name=f"{col_x} x {col_y}",
                        hovertemplate=f"<b>{col_x}</b> x <b>{col_y}</b>: "
                        f"{corr:.3f}<extra></extra>",
                    )

                if isinstance(trace, list):
                    for t in trace:
                        fig.add_trace(t, row=ix_row + 1, col=ix_col + 1)
                else:
                    fig.add_trace(trace, row=ix_row + 1, col=ix_col + 1)
                fig.update_xaxes(
                    {
                        **opt_xaxis,  # type: ignore
                        "mirror": ix_row == 0,
                        "visible": True,
                        "showgrid": False,
                        "showticklabels": False,
                        "tickangle": self.xrotation,
                    },
                    row=ix_row + 1,
                    col=ix_col + 1,
                )
                fig.update_yaxes(
                    {
                        **opt_yaxis,  # type: ignore
                        "mirror": ix_col == ncols - 1,
                        "visible": True,
                        "showgrid": False,
                        "showticklabels": False,
                    },
                    row=ix_row + 1,
                    col=ix_col + 1,
                )

        fig = fig.update_layout(
            {
                "shapes": [
                    {
                        "type": "rect",
                        "x0": 0,
                        "y0": 0,
                        "x1": 1,
                        "y1": 1,
                        "opacity": 1,
                        "layer": "below",
                        "line_width": 0,
                        "xref": f"x{ix}",
                        "yref": f"y{ix}",
                        "fillcolor": c,
                    }
                    for ix, c in tcolors
                ]
            }
        )
        for ix, x, y, text in annotations:
            fig.add_annotation(
                go.layout.Annotation(
                    text=text,
                    x=x,
                    y=y,
                    xref=f"x{ix}",
                    yref=f"y{ix}",
                    showarrow=False,
                    font=dict(size=10),
                    textangle=-45,
                )
            )
        return fig

    @property
    def _base_opts(self) -> dict:
        return {
            "showlegend": self.show_legend,
            "xaxis": {"showgrid": False},
            "yaxis": {"showgrid": False},
        }
