"""Time series section and blocks."""
from typing import List, Tuple, Callable, Dict, Optional

import pandas as pd

from tslumen.plot import interactive as viz
from tslumen.plot.utils import cmap_to_list
from tslumen.plot.interactive.base import go
from tslumen.report.dashboard._dash import (
    dbc,
    html,
    Component,
    StatsTable,
    Plot,
    EmptyFigure,
    SimpleTable,
)
from tslumen.jinja_utils import filter_numberformat
from tslumen.report.dashboard.base import DashInput, DashSection, DashBlock


__all__ = [
    "BlockTSSelect",
    "BlockTSDetails",
    "BlockTSPlot",
    "BlockTSStats",
    "BlockTSDist",
    "BlockTSSmoothing",
    "BlockTSComponents",
    "BlockTSSeasonality",
    "BlockTSAutoCorrelation",
    "BlockTSLagPlots",
    "SectionTimeSeries",
]


class BlockTSSelect(DashInput):
    """Block for selecting which timeseries details to display"""

    title = "Select a series"

    @property
    def body(self) -> Component:
        return dbc.RadioItems(
            options=[{"label": ser, "value": ser} for ser in self.result.result.series],
            value=list(self.result.result.series.keys())[0],
            id="select-timeseries",
            inline=False,
        )


class BlockTSDetails(DashBlock):
    """Block with the time series details"""

    title = "Series Details"
    style = {"width": "225px", "height": "100%"}

    def _init_post(self) -> None:
        self.df_details = pd.DataFrame(
            [
                pd.Series(
                    {
                        "Mean": filter_numberformat(result["mean"]),
                        "Deviation": filter_numberformat(result["std"]),
                        "Maximum": filter_numberformat(result["maximum"]),
                        "Minimum": filter_numberformat(result["minimum"]),
                        "Zeros": filter_numberformat(result["zeros"]),
                        "Missing": filter_numberformat(result["missing"]),
                        "Infinite": filter_numberformat(result["infinite"]),
                    },
                    name=name,
                )
                for name, result in self.result.result.series.items()
            ]
        ).T

    @property
    def body(self) -> Component:
        return dbc.Spinner(html.Div(id="table-tsdetails"))

    def _render(self, name: str) -> Tuple[Component]:
        return (StatsTable(self.df_details[[name]]),)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._render,
                [("table-tsdetails", "children")],
                [("select-timeseries", "value")],
                [],
            )
        ]


class BlockTSPlot(DashBlock):
    """Block with a preview of the time series on a line plot"""

    _height = 300
    title = "Preview"
    style = {"height": "100%", "minWidth": "500px"}

    @property
    def body(self) -> Component:
        return Plot(pid="plot-tsplot", height=self._height)

    def _plot(self, name: str) -> Tuple[go.Figure]:
        return (
            viz.TS(
                self.df[[name]],
                title=name,
                height=self._height,
                show_legend=False,
                rangeslider=False,
            ).plot,
        )

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-tsplot", "figure")],
                [("select-timeseries", "value")],
                [],
            )
        ]


class BlockTSStats(DashBlock):
    """Block with the dataframe's statistics and stats tests"""

    title = "Statistics"
    style = {"height": "100%", "width": "450px"}

    def _init_post(self) -> None:
        self.df_stats = pd.DataFrame(
            [
                pd.Series(
                    {
                        name: filter_numberformat(result[fun])
                        for name, fun in {
                            "Mean": "mean",
                            "Variance": "var",
                            "Standard deviation": "std",
                            "Median": "median",
                            "Median absolute deviation": "mad",
                            "Coefficient of variation": "cov",
                            "Interquartile range": "iqr",
                            "Minimum": "minimum",
                            "25%": "q25",
                            "50%": "q50",
                            "75%": "q75",
                            "Maximum": "maximum",
                            "Kurtosis": "kurtosis",
                            "Skewness": "skew",
                        }.items()
                    },
                    name=name,
                )
                for name, result in self.result.result.series.items()
            ]
        ).T

        self.df_stests = {}
        for name, result in self.result.result.series.items():
            series_tests = {}
            for tname in [
                "levene_constant_variance",
                "ljungbox_autocorrelation",
                "jarque_bera_normality",
                "omnibus_normality",
                "adfuller_stationarity",
                "kpss_stationarity",
            ]:
                tr = result[tname]
                if not tr:
                    continue
                series_tests[tr.test] = {
                    "Null Hypothesis": tr.null_hypothesis,
                    "Reject": "Yes" if tr.reject_null_hypothesis else "No",
                    "pvalue": f"{tr.p_value:.3f}",
                    "Conf": f"{tr.confidence_level:.2f}",
                }
            self.df_stests[name] = pd.DataFrame(series_tests).T.rename_axis(index="Test")

    @property
    def body(self) -> Component:
        return dbc.Tabs(
            [
                dbc.Tab(
                    dbc.Spinner(html.Div(id="table-tsstats")),
                    label="Descriptive statistics",
                ),
                dbc.Tab(
                    dbc.Spinner(html.Div(id="table-tsstests")),
                    label="Statistical Tests",
                ),
            ]
        )

    def _render_stats(self, name: str) -> Tuple[Component]:
        df = self.df_stats[[name]].reset_index()
        df = df.iloc[:7].join(df.iloc[7:].reset_index(drop=True), rsuffix="x", how="outer")
        df.columns = ["Indicator", "Value", "Indicator ", "Value "]
        return (SimpleTable(df, classes="small", show_index=False),)

    def _render_stests(self, name: str) -> Tuple[Component]:
        return (SimpleTable(self.df_stests[name], classes="small"),)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        selector = [("select-timeseries", "value")]
        return [
            (self._render_stats, [("table-tsstats", "children")], selector, []),
            (self._render_stests, [("table-tsstests", "children")], selector, []),
        ]


class BlockTSDist(DashBlock):
    """Block with the distribution plots"""

    _height: int = 375
    title = "Distribution"
    style = {"height": "100%", "minWidth": "300px"}

    def _init_post(self) -> None:
        self.df_binned = {
            name: result["binned"] for name, result in self.result.result.series.items()
        }
        self.df_quantiles = {
            name: result["pd_quantiles"] for name, result in self.result.result.series.items()
        }
        self.df_percentiles = {
            name: result["pd_percentiles"] for name, result in self.result.result.series.items()
        }

    @property
    def controls(self) -> Component:
        return dbc.Select(
            id="select-tsdist",
            options=[
                {"label": "Histogram", "value": "histogram"},
                {"label": "QQ-Plot", "value": "qq"},
                {"label": "PP-Plot", "value": "pp"},
            ],
            value="histogram",
        )

    @property
    def body(self) -> Component:
        return Plot(pid="plot-tsdist", height=self._height)

    def _plot_dist(self, name: str) -> Tuple[go.Figure]:
        return (viz.Histogram(self.df_binned[name], height=self._height, title=name).plot,)

    def _plot_qq(self, name: str) -> Tuple[go.Figure]:
        return (
            viz.SampleTheoretical(
                self.df_quantiles[name],
                "theoretical_quantiles",
                "sample_quantiles",
                "reference",
                title=name,
                label_xaxis="Theoretical Quantiles",
                label_yaxis="Sample Quantiles",
                height=self._height,
            ).plot,
        )

    def _plot_pp(self, name: str) -> Tuple[go.Figure]:
        return (
            viz.SampleTheoretical(
                self.df_percentiles[name],
                "theoretical_percentiles",
                "sample_percentiles",
                "reference",
                title=name,
                label_xaxis="Theoretical Percentiles",
                label_yaxis="Sample Percentiles",
                height=self._height,
            ).plot,
        )

    def _plot(self, name: str, plot: str) -> Tuple[go.Figure]:
        return {"histogram": self._plot_dist, "pp": self._plot_pp, "qq": self._plot_qq}[plot](name)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-tsdist", "figure")],
                [("select-timeseries", "value"), ("select-tsdist", "value")],
                [],
            )
        ]


class BlockTSSmoothing(DashBlock):
    """Block with smooth series"""

    _height: int = 375
    title = "Smoothing"
    style = {"height": "100%", "minWidth": "300px"}

    def _init_post(self) -> None:
        self.df_smooth = {
            name: {var: result[var] for var in ["rolling_avg", "lowess", "supsmu"]}
            for name, result in self.result.result.series.items()
        }

    @property
    def controls(self) -> Component:
        return dbc.Select(
            id="select-tssmooth",
            options=[
                {"label": "Rolling Average", "value": "rolling_avg"},
                {"label": "LOWESS", "value": "lowess"},
                {"label": "Super Smoother", "value": "supsmu"},
            ],
            value="rolling_avg",
        )

    @property
    def body(self) -> Component:
        return Plot(pid="plot-tssmooth", height=self._height)

    def _plot(self, name: str, smoother: str) -> Tuple[go.Figure, ...]:
        df = self.df_smooth[name][smoother]
        if df is None:
            return (EmptyFigure(height=self._height),)
        return (
            viz.TS(
                df=df,
                colors="#cecce0",
                height=self._height,
                title=name,
                rangeslider=False,
                rangeselector=False,
                line_width=[5, 1.5],
                legend_position="bottom",
            ).plot,
        )

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-tssmooth", "figure")],
                [("select-timeseries", "value"), ("select-tssmooth", "value")],
                [],
            )
        ]


class BlockTSComponents(DashBlock):
    """Block with a time series decomposition"""

    _height = 600
    title = "Decomposition"
    style = {"height": "100%", "minWidth": "500px"}

    def _init_post(self) -> None:
        self.df_stl: Dict[str, Optional[pd.DataFrame]] = {}
        for name, result in self.result.result.series.items():
            df = result["stl"]
            if df is None or df.empty:
                self.df_stl[name] = None
            else:
                self.df_stl[name] = self.df[[name]].join(df)

    @property
    def body(self) -> Component:
        return Plot(pid="plot-tscomponents", height=self._height)

    def _plot(self, name: str) -> Tuple[go.Figure]:
        df = self.df_stl[name]
        if df is None:
            return (EmptyFigure(height=self._height),)
        else:
            return (
                viz.TSStack(
                    df,
                    height=self._height,
                    show_legend=False,
                    colors=["#a09ebb"] * 4,
                    rangeselector=False,
                    rangeslider=False,
                ).plot,
            )

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-tscomponents", "figure")],
                [("select-timeseries", "value")],
                [],
            )
        ]


class BlockTSSeasonality(DashBlock):
    """Block with seasonality plots"""

    _height = 200
    title = "Seasonality"
    style = {"height": "100%", "minWidth": "500px"}

    def _init_post(self) -> None:
        self.df_split = {
            name: result["seasonal_split"] for name, result in self.result.result.series.items()
        }
        self.df_box1 = {
            name: self.df_split[name]
            .dropna(axis=1, how="all")
            .iloc[:, -10:]
            .fillna(method="bfill")
            .fillna(method="ffill")
            for name, result in self.result.result.series.items()
        }
        self.df_box2 = {
            name: self.df_split[name]
            .T.dropna(how="all")
            .fillna(method="bfill")
            .fillna(method="ffill")
            for name, result in self.result.result.series.items()
        }

    @property
    def body(self) -> Component:
        return html.Div(
            [Plot(pid=f"plot-season{p}", height=self._height) for p in ["ts", "box1", "box2"]]
        )

    def _plot(self, name: str) -> Tuple[go.Figure, ...]:
        df = self.df_split[name]
        dfb1 = self.df_box1[name]
        dfb2 = self.df_box2[name]
        plot_ts = viz.TS(
            df,
            title=name,
            colors=cmap_to_list("Purples", df.shape[1]),
            height=self._height,
            show_legend=False,
            rangeselector=False,
            rangeslider=False,
        ).plot
        plot_box1 = viz.BoxPlot(dfb1, height=self._height, color=["#a09ebb"] * dfb1.shape[1]).plot
        plot_box2 = viz.BoxPlot(dfb2, height=self._height, color=["#a09ebb"] * dfb2.shape[1]).plot
        return plot_ts, plot_box1, plot_box2

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [(f"plot-season{p}", "figure") for p in ["ts", "box1", "box2"]],
                [("select-timeseries", "value")],
                [],
            )
        ]


class BlockTSAutoCorrelation(DashBlock):
    """Block with ACF and PACF plot"""

    _height = 200
    title = "Auto Correlation"
    style = {"height": "100%", "minWidth": "500px"}

    @property
    def body(self) -> Component:
        return dbc.Row(
            [
                dbc.Col(
                    [
                        Plot(pid=f"plot-tsacf{diff}", height=self._height)
                        for diff in ["", "_1d", "_2d"]
                    ]
                ),
                dbc.Col(
                    [
                        Plot(pid=f"plot-tspacf{diff}", height=self._height)
                        for diff in ["", "_1d", "_2d"]
                    ]
                ),
            ],
            className="no-gutters",
        )

    def _plot(self, name: str) -> Tuple[go.Figure, ...]:
        result = self.result.result.series[name]
        plots = [
            viz.LagCorrelation(
                result[f"{acf}{diff}"],
                label_xaxis="",
                label_yaxis=f'{acf.upper()}{diff.replace("_", " ").replace("d", "diff")}',
                height=self._height,
            ).plot
            for col, acf in enumerate(["acf", "pacf"])
            for row, diff in enumerate(["", "_1d", "_2d"])
        ]
        return tuple(plots)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [
                    (f"plot-ts{acf}{diff}", "figure")
                    for acf in ["acf", "pacf"]
                    for diff in ["", "_1d", "_2d"]
                ],
                [("select-timeseries", "value")],
                [],
            )
        ]


class BlockTSLagPlots(DashBlock):
    """Block with a lag (scatter) plots"""

    _height = 600
    title = "Lag Plots"
    style = {"height": "100%", "minWidth": "500px"}

    def _init_post(self) -> None:
        self.df_lag = {
            name: result["lag_corr"] for name, result in self.result.result.series.items()
        }

    @property
    def body(self) -> Component:
        return Plot(pid="plot-tslag", height=self._height)

    def _plot(self, name: str) -> Tuple[go.Figure]:
        df, corr = self.df_lag[name]
        return (viz.LagMatrix(df, corr, height=self._height, show_legend=False).plot,)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-tslag", "figure")],
                [("select-timeseries", "value")],
                [],
            )
        ]


class SectionTimeSeries(DashSection):
    """Class holding the contents of the "TimeSeries" section"""

    _block_classes = [
        BlockTSSelect,
        BlockTSDetails,
        BlockTSPlot,
        BlockTSStats,
        BlockTSDist,
        BlockTSSmoothing,
        BlockTSComponents,
        BlockTSSeasonality,
        BlockTSAutoCorrelation,
        BlockTSLagPlots,
    ]
    title = "Time Series"

    @property
    def anchors(self) -> List[Tuple[str, str]]:
        return [
            (block.block_id, block.title or block.block_id)
            for block in self.blocks.values()
            if not isinstance(block, DashInput)
        ]

    @property
    def body(self) -> Component:
        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(self.blocks["BlockTSSelect"].layout, className="col-sm-auto"),
                        dbc.Col(
                            self.blocks["BlockTSDetails"].layout,
                            className="col-sm-auto",
                        ),
                        dbc.Col(self.blocks["BlockTSPlot"].layout),
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(self.blocks["BlockTSStats"].layout, className="col-sm-auto"),
                        dbc.Col(self.blocks["BlockTSDist"].layout),
                        dbc.Col(self.blocks["BlockTSSmoothing"].layout),
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(self.blocks["BlockTSComponents"].layout),
                        dbc.Col(self.blocks["BlockTSSeasonality"].layout),
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [
                        dbc.Col(self.blocks["BlockTSAutoCorrelation"].layout),
                        dbc.Col(self.blocks["BlockTSLagPlots"].layout),
                    ],
                    className="mb-4",
                ),
            ]
        )
