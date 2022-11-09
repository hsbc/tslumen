"""Line plots."""
from typing import Union, Optional, Any

import pandas as pd

from tslumen.plot.interactive.base import VizBase, go, make_subplots


__all__ = ["TS", "TSStack"]


@VizBase.extend_init
class TS(VizBase):
    """TimeSeries plot, displaying each column in the input dataframe as a curve over time."""

    def __init__(
        self,
        df: pd.DataFrame,
        columns: Optional[Union[str, list]] = None,
        labels: Optional[Union[str, list]] = None,
        colors: Optional[Union[str, list]] = None,
        line_width: Optional[Union[float, list]] = 1.5,
        label_xaxis: str = "",
        label_yaxis: str = "",
        fmt_x: str = "%b/%Y",
        fmt_y: str = "",
        xaxis: Optional[Union[bool, str]] = "bottom",
        yaxis: Optional[Union[bool, str]] = "left",
        show_legend: bool = True,
        legend_position: str = "right",
        rangeslider: bool = True,
        rangeselector: bool = True,
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label}</b>: %{y:.2f}"
        "<extra></extra>",
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.df = df.copy()
        self.columns = columns
        self.labels = labels
        self.colors = colors
        self.line_width = line_width
        self.label_xaxis = label_xaxis
        self.label_yaxis = label_yaxis
        self.fmt_y = fmt_y
        self.fmt_x = fmt_x
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.show_legend = show_legend
        self.legend_position = legend_position
        self.rangeslider = rangeslider
        self.rangeselector = rangeselector
        self.hovertemplate = hovertemplate

    @property
    def _base_opts(self) -> dict:
        rangeselector = {}
        if self.rangeselector:
            rangeselector = {
                "rangeselector": {
                    "buttons": [
                        {"step": "all"},
                        {
                            "step": "year",
                            "count": 1,
                            "label": "YTD",
                            "stepmode": "todate",
                        },
                        {
                            "step": "year",
                            "count": 2,
                            "label": "2y",
                            "stepmode": "backward",
                        },
                        {
                            "step": "year",
                            "count": 1,
                            "label": "1y",
                            "stepmode": "backward",
                        },
                        {
                            "step": "month",
                            "count": 6,
                            "label": "6m",
                            "stepmode": "backward",
                        },
                    ],
                    "y": 1.02,
                    "yanchor": "bottom",
                },
            }

        return {
            "legend": self.LEGEND_POSITION[self.legend_position],
            "showlegend": self.show_legend,
            "xaxis": {
                "type": "date" if isinstance(self.df.index, pd.DatetimeIndex) else "-",
                **rangeselector,
                "visible": bool(self.xaxis),
                "title": self.label_xaxis,
                "tickformat": self.fmt_x,
                "rangeslider": {"visible": self.rangeslider},
                "side": self.xaxis if isinstance(self.xaxis, str) else "bottom",
            },
            "yaxis": {
                "visible": bool(self.yaxis),
                "title": self.label_yaxis,
                "tickformat": self.fmt_y,
                "side": self.yaxis if isinstance(self.yaxis, str) else "left",
            },
        }

    def _create_figure(self) -> Any:
        pfix = self._pfix
        df = self.df if isinstance(self.df, pd.DataFrame) else self.df.data
        columns = pfix(self.columns, df.columns)
        ncols = len(columns)
        labels = pfix(self.labels, columns, fill=columns)
        colors = pfix(self.colors, self.PALETTE, None, self.PALETTE, ncols)
        line = [1.5] * ncols
        line = pfix(self.line_width, line, None, line, ncols)
        fig = go.Figure()
        for col, label, color, l_width in zip(columns, labels, colors, line):
            fig.add_trace(
                go.Scatter(
                    x=df.index.tolist(),
                    y=df[col].tolist(),
                    name=label,
                    meta={
                        "label_xaxis": self.label_xaxis or "Date",
                        "label_yaxis": self.label_yaxis,
                        "column": col,
                        "label": label,
                        "color": color,
                    },
                    mode="lines",
                    line={"color": color, "width": l_width},
                    hovertemplate=self.hovertemplate,
                )
            )

        return fig


@TS.extend_init
class TSStack(TS):
    """TimeSeries Stacked plot for stacking a set of plots in one single vertical column. One
    trace per plot and all plots reading from the same date index.
    """

    def __init__(self, df: pd.DataFrame, show_all_xaxis: bool = False, **kwargs: Any) -> None:
        super().__init__(df, **kwargs)
        self.kwargs = kwargs
        self.show_all_xaxis = show_all_xaxis

    def _create_figure(self) -> go.Figure:
        self.rangeslider = False
        labels = self.label_xaxis, self.label_yaxis
        self.label_xaxis, self.label_yaxis = "", ""
        ts = super()._apply_base_opts(super()._create_figure())
        traces, layout = ts.data, ts.layout
        self.label_xaxis, self.label_yaxis = labels
        shared_xaxes = not self.show_all_xaxis

        fig = make_subplots(
            rows=len(traces),
            cols=1,
            start_cell="top-left",
            shared_xaxes=shared_xaxes,
            shared_yaxes=False,
            vertical_spacing=0.02 if shared_xaxes else 0.08,
        )
        fig.update_layout(layout)
        xaxis = {
            k: layout["xaxis"][k]
            for k in ["gridcolor", "linecolor", "showgrid", "type", "zeroline"]
        }
        label_y = self.kwargs.get("label_yaxis", [])
        for i, trace in enumerate(traces):
            row = i + 1
            fig.add_trace(trace, row=row, col=1)
            fig.update_xaxes(
                xaxis,
                row=row,
                col=1,
                title_text="" if row < len(traces) else self.label_xaxis,
            )
            fig.update_yaxes(
                layout["yaxis"],
                row=row,
                col=1,
                title_text=label_y[i] if label_y else trace.meta["label"],
            )
        return fig

    def _apply_base_opts(self, plot: go.Figure, *overrides: dict) -> go.Figure:
        return plot
