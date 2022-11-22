"""Comparison plots."""
from typing import Optional, Any, List, Union, Tuple

import pandas as pd

from tslumen.plot.interactive.base import VizBase, go
from tslumen.plot.utils import cmapper, ccontrast


__all__ = ["Radar", "Heatmap"]


@VizBase.extend_init
class Radar(VizBase):
    """Radar (aka spider) plot for comparing data bearing multiple dimensions."""

    def __init__(
        self,
        data: pd.DataFrame,
        columns: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        axis_range: Optional[tuple] = None,
        show_legend: bool = False,
        legend_position: str = "bottom_left",
        fill: Optional[str] = "toself",
        **kwargs: Any
    ) -> None:
        """
        Args:
            data (pd.DataFrame): Dataframe to be plotted.
            columns (list): Subset of columns to use (optional).
            labels (list): Option to re-label the columns (defined positionally).
            colors (list): For coloring each of the series being plotted.
            axis_range (Tuple[Number, Number]): Manually define the range of values to plot.
            show_legend (bool): Switches legend on/off.
            legend_position (str): Controls the legend positioning.
        """
        super().__init__(**kwargs)
        self.data = data
        self.columns = columns
        self.labels = labels
        self.colors = colors
        self.show_legend = show_legend
        self.legend_position = legend_position
        self.axis_range = axis_range
        self.fill = fill

    def _create_figure(self) -> Any:
        df = self.data
        columns = self._pfix(self.columns, df.columns)
        df = df[columns].copy()
        labels = self.labels or columns
        colors = self._pfix(self.colors, self.PALETTE, fill=self.PALETTE, size=len(df.index))

        fig = go.Figure()
        theta = labels + [labels[0]]
        for num, idx in enumerate(df.index):
            radial = df.loc[idx].tolist() + [df.loc[idx][0]]
            fig.add_trace(
                go.Scatterpolar(
                    theta=theta,
                    r=radial,
                    name=idx,
                    meta=idx,
                    fill=self.fill,
                    line_color=colors[num],
                    hovertemplate="<b>Group: %{meta}<br>"
                    "<b>Category</b>: %{theta}<br>"
                    "<b>Value</b>: %{r}<extra></extra>",
                )
            )
        return fig

    @property
    def _base_opts(self) -> dict:
        return {
            "legend": self.LEGEND_POSITION[self.legend_position],
            "showlegend": self.show_legend,
            "margin": {"l": 10, "r": 10, "b": 40, "t": 50},
        }

    def _apply_base_opts(self, plot: go.Figure, *overrides: dict) -> go.Figure:
        plot = super()._apply_base_opts(plot, *overrides)
        plot.update_polars(
            bgcolor=self.VIZBASE_LAYOUT_OPTS["plot_bgcolor"],
            radialaxis={
                **{
                    k: v
                    for k, v in self.VIZBASE_LAYOUT_OPTS["xaxis"].items()  # type: ignore
                    if k in ["linecolor", "showgrid", "gridcolor"]
                },
                "range": self.axis_range,
            },
        )
        return plot


@VizBase.extend_init
class Heatmap(VizBase):
    """Heatmap plot."""

    def __init__(
        self,
        data: pd.DataFrame,
        label_xaxis: str = "",
        label_yaxis: str = "",
        xrotation: int = 0,
        show_labels: bool = True,
        labels_format: str = "{:.2f}",
        cmap: Union[str, List[str]] = "PuBu",
        colorbar: bool = True,
        colorbar_position: str = "right",
        colorbar_limit: Tuple[float, float] = (-1.0, 1.0),
        fmt_colorbar: str = "0.00 a",
        hovertemplate: str = "<b>%{meta.label_xaxis}</b>: %{x}<br>"
        "<b>%{meta.label_yaxis}</b>: %{y}<br>"
        "<b>Value</b>: %{z}"
        "<extra></extra>",
        **kwargs: Any
    ) -> None:
        """
        Args:
            data (pd.DataFrame): Matrix with the coefficient values.
            label_xaxis (str): X-axis label, default ''.
            label_yaxis (str): X-axis label,  default ''.
            xrotation (int): Rotation degree to apply to the x axis, default 0.
            show_labels (bool): Whether to show the coefficient on the heatmap, default True.
            labels_format (str): Format to apply to the labels, default '{0:.2f}'.
            cmap (str): Color map or palette, default 'PuBu'.
            colorbar (bool): Whether to show the color bar, default True.
            colorbar_position (str): Where to position the colorbar, e.g. 'left', 'right', etc.
            colorbar_limit (Tuple[float, float]): Min and max colorbar range, default (-1, 1).
        """
        super().__init__(**kwargs)
        self.data = data
        self.label_xaxis = label_xaxis
        self.label_yaxis = label_yaxis
        self.xrotation = xrotation
        self.show_labels = show_labels
        self.labels_format = labels_format
        self.cmap = cmap
        self.colorbar = colorbar
        self.colorbar_position = colorbar_position
        self.fmt_colorbar = fmt_colorbar
        self.colorbar_limit = colorbar_limit
        self.hovertemplate = hovertemplate
        self._annotations: list = []

    def _annotate(self) -> None:
        df = self.data
        cmap = cmapper(
            self.colorbar_limit[0],
            self.colorbar_limit[1],
            self.cmap if isinstance(self.cmap, str) else "PuBu",
            as_hex=False,
        )
        self._annotations = []
        for i, row in enumerate(df.values):
            for j, val in enumerate(row):
                if not val or val != val:
                    continue
                *bg, _ = cmap(val)
                fg = ccontrast(*bg)
                self._annotations.append(
                    go.layout.Annotation(
                        text=self.labels_format.format(val),
                        font=dict(color=fg),
                        x=df.columns[j],
                        y=df.index[i],
                        xref="x1",
                        yref="y1",
                        showarrow=False,
                    )
                )

    def _create_figure(self) -> go.Figure:
        df = self.data
        colorbar_position = self.COLORBAR_POSITION[self.colorbar_position]
        fig = go.Figure(
            go.Heatmap(
                z=df.values.tolist(),
                zmid=(self.colorbar_limit[0] + self.colorbar_limit[1]) / 2,
                zmin=self.colorbar_limit[0],
                zmax=self.colorbar_limit[1],
                x=df.columns.tolist(),
                y=df.index.tolist(),
                meta={"label_xaxis": "Category", "label_yaxis": "Group"},
                colorscale=self.cmap,
                colorbar={
                    "tickmode": "array",
                    "tickformat": self.fmt_colorbar,
                    **colorbar_position,  # type: ignore
                },
                showscale=self.colorbar,
                hovertemplate=self.hovertemplate,
            )
        )
        self._annotations = []
        if self.show_labels:
            self._annotate()
        return fig

    @property
    def _base_opts(self) -> dict:
        return {
            "xaxis": {
                "type": "category",
                "title": self.label_xaxis,
                "tickangle": self.xrotation,
                "showgrid": False,
                "mirror": True,
                "side": "top",
            },
            "yaxis": {
                "showgrid": False,
                "type": "category",
                "title": self.label_yaxis,
                "mirror": True,
            },
            "annotations": self._annotations,
        }
