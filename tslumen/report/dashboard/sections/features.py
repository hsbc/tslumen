"""Features section and blocks."""
from typing import List, Tuple, Callable

import pandas as pd

from tslumen.plot import interactive as viz
from tslumen.plot.interactive.base import go
from tslumen.report.dashboard.base import DashInput, DashSection, DashBlock
from tslumen.report.dashboard._dash import dbc, html, Component, Plot, EmptyFigure


__all__ = [
    "BlockTSFTSelect",
    "BlockTSFeaturesHeatmap",
    "BlockTSFeaturesRadar",
    "SectionFeatures",
]


_PROFILERS_TSFEATURES = [
    "ft_stl",
    "ft_entropy",
    "ft_acf",
    "ft_pacf",
    "ft_tilewin",
    "ft_kpss",
    "ft_adfuller",
]
_FTS_MAIN = [
    "trend",
    "seasonality",
    "entropy",
    "entropy_acf",
    "instability",
    "lumpiness",
]
_FTS_STAT = [
    "kpss(c)",
    "kpss(ct)",
    "adfuller(c)",
    "adfuller(ct)",
    "adfuller(ctt)",
    "adfuller(nc)",
]
_FTS_ACF = [
    "acf1(d=0)",
    "acf1(d=1)",
    "acf1(d=2)",
    "acf10(d=0)",
    "acf10(d=1)",
    "acf10(d=2)",
    "acf1(error)",
    "acf10(error)",
    "acf(season)",
]
_FTS_PACF = ["pacf5(d=0)", "pacf5(d=1)", "pacf5(d=2)", "pacf(season)"]
_FTS = dict(main=_FTS_MAIN, stat=_FTS_STAT, acf=_FTS_ACF, pacf=_FTS_PACF)


class BlockTSFTSelect(DashInput):
    """Block for selecting which timeseries details to display"""

    @property
    def body(self) -> Component:
        features = dbc.Select(
            id="select-ftfeatures",
            options=[
                {"label": "Main features", "value": "main"},
                {"label": "Stationarity", "value": "stat"},
                {"label": "ACF", "value": "acf"},
                {"label": "PACF", "value": "pacf"},
            ],
            value="main",
        )
        select = dbc.Checklist(
            options=[{"label": ser, "value": ser} for ser in self.result.result.series],
            value=list(self.result.result.series.keys()),
            id="select-ftts",
            inline=False,
        )
        return html.Div(
            [
                html.H4("Group"),
                features,
                html.Hr(),
                html.H4("Select series"),
                select,
            ]
        )


class BlockTSFeaturesHeatmap(DashBlock):
    """Block with ts features heatmap"""

    _height: int = 400
    title = "Heatmap"
    style = {"height": "100%", "minWidth": "400px"}

    def _init_post(self) -> None:
        series = self.result.result.series
        self.df_fts = pd.concat(
            [
                pd.concat([ser[ft] for ft in _PROFILERS_TSFEATURES]).rename(name)
                for name, ser in series.items()
            ],
            axis=1,
        )

    @property
    def body(self) -> Component:
        return Plot(pid="plot-ftheat", height=self._height)

    def _plot(self, features: str, names: List[str]) -> Tuple[go.Figure, ...]:
        if not names:
            return (EmptyFigure(height=self._height, text="Select a series"),)

        df_fts = self.df_fts.loc[_FTS[features], names].T
        lim_min = 0 if features == "main" else df_fts.min().min()
        lim_max = max(df_fts.max().max(), 1)
        plot_heat = viz.Heatmap(
            df_fts,
            colorbar_limit=(lim_min, lim_max),
            xrotation=45,
            height=min(self._height, 100 + 50 * len(names)),
        ).plot
        return (plot_heat,)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-ftheat", "figure")],
                [("select-ftfeatures", "value"), ("select-ftts", "value")],
                [],
            )
        ]


class BlockTSFeaturesRadar(DashBlock):
    """Block with ts features radar"""

    _height: int = 400
    title = "Radar"
    style = {"height": "100%", "minWidth": "400px"}

    def _init_post(self) -> None:
        series = self.result.result.series
        self.df_fts = pd.concat(
            [
                pd.concat([ser[ft] for ft in _PROFILERS_TSFEATURES]).rename(name)
                for name, ser in series.items()
            ],
            axis=1,
        )

    @property
    def body(self) -> Component:
        return Plot(pid="plot-ftradar", height=self._height)

    def _plot(self, features: str, names: List[str]) -> Tuple[go.Figure, ...]:
        if not names:
            return (EmptyFigure(height=self._height, text="Select a series"),)

        df_fts = self.df_fts.loc[_FTS[features], names].T
        plot_radar = viz.Radar(
            df_fts, height=self._height, show_legend=True, legend_position="bottom"
        ).plot
        return (plot_radar,)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-ftradar", "figure")],
                [("select-ftfeatures", "value"), ("select-ftts", "value")],
                [],
            )
        ]


class SectionFeatures(DashSection):
    """Class holding the contents of the "Features" section"""

    _block_classes = [BlockTSFTSelect, BlockTSFeaturesHeatmap, BlockTSFeaturesRadar]
    title = "Features"

    @property
    def body(self) -> Component:
        return dbc.Row(
            [
                dbc.Col(self.blocks["BlockTSFTSelect"].layout, className="col-sm-auto"),
                dbc.Col(self.blocks["BlockTSFeaturesHeatmap"].layout),
                dbc.Col(self.blocks["BlockTSFeaturesRadar"].layout),
            ]
        )
