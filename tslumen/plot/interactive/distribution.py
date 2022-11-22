"""Distribution plots."""
from typing import Union, Optional, Any

import pandas as pd

from tslumen.plot.interactive.base import VizBase, go


__all__ = ["Histogram", "SampleTheoretical", "BoxPlot"]


@VizBase.extend_init
class Histogram(VizBase):
    """Histogram plot, displaying the distribution of continuous values."""

    def __init__(
        self,
        data: Union[pd.DataFrame, pd.Series],
        labels: Optional[list] = None,
        label_xaxis: Optional[str] = "Bin",
        label_yaxis: Optional[str] = "Count",
        xrotation: int = 0,
        show_legend: bool = False,
        legend_position: str = "right",
        color: Optional[Union[str, list]] = None,
        bargap: Union[int, float] = 0.1,
        barmode: str = "stack",
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label_yaxis}</b>: %{y:d}"
        "<extra></extra>",
        **kwargs: Any
    ) -> None:
        """
        Args:
            data (Union[pd.DataFrame, pd.Series]): Values to be plotted on the histogram.
            labels (list): Optional labels.
            label_xaxis (str): X-axis label, default to 'Bins'.
            label_yaxis (str): Y-axis label, default to 'Count'.
            xrotation (int): Rotation degree to apply to the x axis, default 0.
            show_legend (bool): Whether to show the legend, default False.
            legend_position (str): Where to position the legend, default 'right'.
            color (Union[str, list]): Color of the plot bars.
            bargap (Union[float, int]): Gap between each bar of the histogram, default 0.1.
            barmode (str): Options include "stack" (default), "relative", "group" and "overlay".
            width (int): The width of the plot.
            height (int): The height of the plot.
        """
        super().__init__(**kwargs)
        self.data = data
        self.color = color
        self.labels = labels
        self.label_xaxis = label_xaxis
        self.label_yaxis = label_yaxis
        self.xrotation = xrotation
        self.show_legend = show_legend
        self.legend_position = legend_position
        self.barmode = barmode
        self.bargap = bargap
        self.hovertemplate = hovertemplate

    def _create_figure(self) -> go.Figure:
        df = self.data if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)

        color = self._pfix(self.color, self.PALETTE, fill=self.PALETTE, size=len(df.columns))
        label_yaxis = self.label_yaxis

        hists = [
            go.Bar(
                x=df.index,
                y=df[col],
                name=col,
                meta={
                    "label_xaxis": self.label_xaxis,
                    "label_yaxis": label_yaxis,
                    "column": col,
                    "color": color[ix],
                },
                marker={"color": color[ix]},
                hovertemplate=self.hovertemplate,
            )
            for ix, col in enumerate(df.columns)
        ]

        return go.Figure(data=hists)

    @property
    def _base_opts(self) -> dict:
        opts = {
            "legend": self.LEGEND_POSITION[self.legend_position],
            "bargap": self.bargap,
            "barmode": self.barmode,
            "showlegend": self.show_legend,
            "xaxis": {
                "visible": True,
                "title": self.label_xaxis,
                "tickangle": self.xrotation,
                "tickvals": self.labels,
            },
            "yaxis": {"title": self.label_yaxis},
        }
        return opts


@VizBase.extend_init
class SampleTheoretical(VizBase):
    """PP/QQ plot."""

    def __init__(
        self,
        data: pd.DataFrame,
        col_theoretical: str,
        col_sample: str,
        col_reference: str,
        label_xaxis: Optional[str] = "Theoretical",
        label_yaxis: Optional[str] = "Sample",
        xrotation: int = 0,
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label_yaxis}</b>: %{y}"
        "<extra></extra>",
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.col_sample = col_sample
        self.col_theoretical = col_theoretical
        self.col_reference = col_reference
        self.label_xaxis = label_xaxis
        self.label_yaxis = label_yaxis
        self.xrotation = xrotation
        self.hovertemplate = hovertemplate

    def _create_figure(self) -> go.Figure:
        df = self.data
        color_m = self.PALETTE[0]
        color_l = "blue"
        label_yaxis = self.label_yaxis

        kwargs = dict(
            meta={"label_xaxis": self.label_xaxis, "label_yaxis": label_yaxis},
            hovertemplate=self.hovertemplate,
        )
        return go.Figure(
            [
                go.Scatter(
                    x=df[self.col_theoretical],
                    y=df[self.col_reference],
                    marker={"color": color_l},
                    **kwargs
                ),
                go.Scatter(
                    x=df[self.col_theoretical],
                    y=df[self.col_sample],
                    mode="markers",
                    marker={"color": color_m},
                    **kwargs
                ),
            ]
        )

    @property
    def _base_opts(self) -> dict:
        opts = {
            "showlegend": False,
            "xaxis": {
                "visible": True,
                "title": self.label_xaxis,
                "tickangle": self.xrotation,
            },
            "yaxis": {"title": self.label_yaxis},
        }
        return opts


@VizBase.extend_init
class BoxPlot(VizBase):
    """BoxPlot w/ whiskers."""

    def __init__(
        self,
        data: Union[pd.DataFrame, pd.Series],
        labels: Optional[list] = None,
        label_xaxis: Optional[str] = "",
        label_yaxis: Optional[str] = "",
        xrotation: int = 0,
        show_legend: bool = False,
        legend_position: str = "right",
        color: Optional[Union[str, list]] = None,
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label_yaxis}</b>: %{y:d}"
        "<extra></extra>",
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.color = color
        self.labels = labels
        self.label_xaxis = label_xaxis
        self.label_yaxis = label_yaxis
        self.xrotation = xrotation
        self.show_legend = show_legend
        self.legend_position = legend_position
        self.hovertemplate = hovertemplate

    def _create_figure(self) -> go.Figure:
        df = self.data if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)

        color = self._pfix(self.color, self.PALETTE, fill=self.PALETTE, size=len(df.columns))
        label_yaxis = self.label_yaxis

        boxes = [
            go.Box(
                y=df[col],
                name=col,
                meta={
                    "label_xaxis": self.label_xaxis,
                    "label_yaxis": label_yaxis,
                    "column": col,
                    "color": color[ix],
                },
                marker={"color": color[ix]},
                hovertemplate=self.hovertemplate,
            )
            for ix, col in enumerate(df.columns)
        ]

        return go.Figure(data=boxes)

    @property
    def _base_opts(self) -> dict:
        opts = {
            "legend": self.LEGEND_POSITION[self.legend_position],
            "showlegend": self.show_legend,
            "xaxis": {
                "visible": True,
                "title": self.label_xaxis,
                "tickangle": self.xrotation,
                "tickvals": self.labels,
            },
            "yaxis": {"title": self.label_yaxis},
        }
        return opts
