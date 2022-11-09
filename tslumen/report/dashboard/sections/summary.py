"""Summary section and blocks."""
from typing import List, Tuple, Callable, Any
from pprint import pformat

import pandas as pd
import yaml
from jinja2.filters import do_filesizeformat

import tslumen
from tslumen.jinja_utils import format_date_freq
from tslumen.plot import interactive as viz
from tslumen.plot.interactive.base import go
from tslumen.report.dashboard._dash import (
    dbc,
    html,
    Component,
    StatsTable,
    Plot,
    PopoverButton,
    SimpleTable,
)
from tslumen.report.dashboard.base import DashSection, DashBlock


__all__ = [
    "BlockStats",
    "BlockPreview",
    "BlockStatus",
    "SectionSummary",
]


class BlockStats(DashBlock):
    """Block with the dataframe's summary stats"""

    title = "Frame statistics"
    style = {"width": "350px", "height": "100%"}

    def _init_post(self) -> None:
        frame = self.result.result.frame
        freq = frame.get("freq", "")
        self.df_stats = pd.DataFrame(
            [
                {
                    "Number of series": frame.get("n_series", ""),
                    "Time series length": frame.get("length", -1),
                    "Start date": format_date_freq(freq).format(frame.get("dt_start", "")),
                    "End date": format_date_freq(freq).format(frame.get("dt_end", "")),
                    "Frequency": freq,
                    "Period": frame.get("period", ""),
                    "Total size in memory": do_filesizeformat(frame.get("sz_total", -1)),
                    "Average series size": do_filesizeformat(
                        frame.get("sz_total", 0) / frame.get("n_series", 1)
                    ),
                }
            ]
        ).T

    @property
    def body(self) -> Any:
        return StatsTable(self.df_stats)


class BlockPreview(DashBlock):
    """Block with a preview of the time series on a line plot"""

    _height = 350
    title = "Preview"
    style = {"height": "100%", "minWidth": "600px"}

    def _init_post(self) -> None:
        df_scaled = self.result.result.frame.get("df_scaled", pd.DataFrame())
        self.df_scaled = self.df if df_scaled.empty else df_scaled

    @property
    def controls(self) -> Any:
        return dbc.Checklist(
            id="checklist-scaled",
            options=[{"label": "Scaled", "value": 1}],
            switch=True,
        )

    @property
    def body(self) -> Any:
        return Plot(pid="plot-preview", height=self._height)

    def _plot(self, scaled: bool) -> Tuple[go.Figure]:
        return (viz.TS(self.df_scaled if scaled else self.df, height=self._height).plot,)

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return [
            (
                self._plot,
                [("plot-preview", "figure")],
                [("checklist-scaled", "value")],
                [],
            )
        ]


class BlockStatus(DashBlock):
    """Block with metadata, execution stats, config and issues"""

    def _init_post(self) -> None:
        self.df_exec = pd.DataFrame(
            [
                {
                    "Started": f"{self.result.start}",
                    "Endend": f"{self.result.end}",
                    "Duration": f"{self.result.end - self.result.start}",
                    "Package": f"tslumen=={tslumen.__version__}",
                }
            ]
        ).T

        config = {k: val for k, val in self.result.result.config.items() if val}
        self.config_dict = pformat(config)
        self.config_yaml = yaml.dump(config)

        self.issues = (
            self.result.result.exec_details.query("~ Succeeded")[
                ["Profiler", "Scope", "Target", "Exceptions"]
            ]
            .sort_values(["Profiler", "Target"])
            .reset_index(drop=True)
            .astype("str")
        )

        self.meta_frame = pd.DataFrame([self.meta.get("frame", {})]).T.dropna()
        meta_series = pd.DataFrame([self.meta.get("series", {})]).T
        self.meta_series = meta_series[meta_series != ""].dropna()

    @property
    def layout(self) -> Component:
        stats = PopoverButton(
            StatsTable(self.df_exec, "Execution statistics", classes="small"),
            "bi bi-stopwatch",
            "exec",
            div_class="float-right px-1",
        )
        config = PopoverButton(
            html.Div(
                [
                    html.H4("Configuration details"),
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                html.Textarea(
                                    self.config_dict,
                                    className="ta-config border p-1 small",
                                ),
                                label="Dict",
                            ),
                            dbc.Tab(
                                html.Textarea(
                                    self.config_yaml,
                                    className="ta-config border p-1 small",
                                ),
                                label="YAML",
                            ),
                        ]
                    ),
                ]
            ),
            "bi bi-gear-wide-connected",
            "config",
            div_class="float-right px-1",
        )
        bar = [config, stats]

        if not self.issues.empty:
            issues = PopoverButton(
                SimpleTable(self.issues, "Issues", classes="small", show_index=False),
                "bi bi-exclamation-circle",
                "issues",
                div_class="float-right px-1",
            )
            bar.insert(0, issues)
        if not self.meta_frame.empty or not self.meta_series.empty:
            meta = PopoverButton(
                dbc.Row(
                    [
                        dbc.Col(
                            StatsTable(self.meta_frame, "Frame details", classes="small"),
                            width=7,
                        ),
                        dbc.Col(
                            StatsTable(self.meta_series, "Time Series", classes="small"),
                            width=5,
                        ),
                    ],
                    style={"width": "600px"},
                ),
                "bi bi-card-heading",
                "meta",
                div_class="float-right px-1",
            )
            bar.append(meta)
        return html.Div(bar)


class SectionSummary(DashSection):
    """Class holding the contents of the "Summary" section"""

    _block_classes = [BlockStatus, BlockStats, BlockPreview]
    title = "Summary"

    controls = ["BlockStatus"]

    @property
    def body(self) -> Component:
        return dbc.Row(
            [
                dbc.Col(self.blocks["BlockStats"].layout, className="col-sm-auto"),
                dbc.Col(self.blocks["BlockPreview"].layout),
            ]
        )
