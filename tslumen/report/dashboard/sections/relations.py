"""Relations section and blocks."""
from typing import List, Tuple, Callable, Any

import pandas as pd

from tslumen.plot import interactive as viz
from tslumen.plot.interactive.base import go
from tslumen.report.dashboard._dash import dbc, html, Component, Plot, EmptyFigure
from tslumen.report.dashboard.base import DashInput, DashSection, DashBlock


__all__ = [
    "BlockTSRelSelect",
    "BlockTSCorrelations",
    "BlockTSGranger",
    "SectionRelations",
]


class BlockTSRelSelect(DashInput):
    """Block for selecting which timeseries details to display"""

    title = "Select series"

    @property
    def body(self) -> Component:
        return dbc.Checklist(
            options=[{"label": ser, "value": ser} for ser in self.result.result.series],
            value=list(self.result.result.series.keys()),
            id="select-relts",
            inline=False,
        )


class BlockTSCorrelations(DashBlock):
    """Block with correlations"""

    _height: int = 550
    title = "Correlations"
    style = {"height": "100%", "minWidth": "400px"}

    def _init_post(self) -> None:
        frame = self.result.result.frame
        self.df_corr = {corr: frame[f"corr_{corr}"] for corr in ["pearson", "kendall", "spearman"]}

    @property
    def body(self) -> Component:
        return Plot(pid="plot-correlations", height=self._height)

    @property
    def controls(self) -> Component:
        return dbc.Select(
            id="select-tscorrelations",
            options=[
                {"label": "Pearson", "value": "pearson"},
                {"label": "Kendall", "value": "kendall"},
                {"label": "Spearman", "value": "spearman"},
            ],
            value="pearson",
        )

    def _plot(self, names: List[str], method: str) -> Tuple[go.Figure]:
        if not names:
            return (EmptyFigure(height=self._height, text="Select a series"),)

        df_corr = self.df_corr[method].loc[names, names]
        df = self.df[names]
        return (viz.ScatterMatrix(df, df_corr, width=self._height, height=self._height).plot,)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-correlations", "figure")],
                [("select-relts", "value"), ("select-tscorrelations", "value")],
                [],
            )
        ]


class BlockTSGranger(DashBlock):
    """Block with Granger causality matrix"""

    _height: int = 500
    title = "Granger Causality"
    style = {"height": "100%", "minWidth": "500px"}

    def _init_post(self) -> None:
        frame = self.result.result.frame
        self.dfp, self.dfl, self.granger_diff = frame.get(
            "granger_causality", (pd.DataFrame(), pd.DataFrame(), None)
        )

    @property
    def controls(self) -> Component:
        return dbc.Input(
            type="number",
            min=0,
            max=1,
            step=0.01,
            value=0.05,
            id="input-grangercritical",
        )

    @property
    def body(self) -> Component:
        return html.Div([html.P(id="text-granger"), Plot(pid="plot-granger", height=self._height)])

    def _plot(self, names: List[str], critical: float) -> Tuple[go.Figure, Any]:
        if not names:
            return EmptyFigure(height=self._height, text="Select a series"), ""
        if self.dfp.empty:
            return EmptyFigure(height=self._height, text="No data"), ""

        dfp, dfl, granger_diff = self.dfp, self.dfl, self.granger_diff
        names_x, names_y = ([f"{c}[{s}]" for c in names] for s in ["x", "y"])
        dfp = dfp.loc[names_y, names_x]
        dfl = dfl.loc[names_y, names_x]
        text = ["Critical value ", html.Code(critical), ". "]
        if granger_diff > 0:
            text += [
                "Data differenced ",
                html.Code(f"{granger_diff}"),
                " time(s) to try to achieve stationarity.",
            ]
        return viz.GrangerMatrix(dfp, dfl, critical, height=self._height, xrotation=45).plot, text

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-granger", "figure"), ("text-granger", "children")],
                [("select-relts", "value"), ("input-grangercritical", "value")],
                [],
            )
        ]


class SectionRelations(DashSection):
    """Class holding the contents of the "Relations" section"""

    _block_classes = [BlockTSRelSelect, BlockTSCorrelations, BlockTSGranger]
    title = "Relations"

    @property
    def body(self) -> Component:
        return dbc.Row(
            [
                dbc.Col(self.blocks["BlockTSRelSelect"].layout, className="col-sm-auto"),
                dbc.Col(self.blocks["BlockTSCorrelations"].layout),
                dbc.Col(self.blocks["BlockTSGranger"].layout),
            ]
        )
