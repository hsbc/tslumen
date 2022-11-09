"""Module with the main class ``Dashboard``."""
from typing import Optional, Any
import warnings

import pandas as pd

from tslumen.scheduling import Scheduler
from tslumen.profile.base import BundledProfiler, BundledResult
from tslumen.report.base import Report
from tslumen.report.dashboard.base import TslumenDash
from tslumen.report.dashboard import sections
from tslumen.report.dashboard._dash import html

__all__ = ["Dashboard"]


class Dashboard(Report):
    """Renders the profiling results as an interactive Dash application, either directly in/from a
    Jupyter notebook or as a standalone web app. Requires a live kernel or server."""

    SECTIONS = [
        sections.SectionSummary,
        sections.SectionTimeSeries,
        sections.SectionFeatures,
        sections.SectionRelations,
    ]

    def __init__(
        self,
        df: pd.DataFrame,
        meta: Optional[dict] = None,
        result: Optional[BundledResult] = None,
        profiler: Optional[BundledProfiler] = None,
        profiler_config: Optional[dict] = None,
        scheduler: Optional[Scheduler] = None,
        scheduler_config: Optional[dict] = None,
        name: Optional[str] = None,
        server_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            df (pd.DataFrame): Timeseries data.
            meta (Optional[dict]): Timeseries metadata, a 2-level dictionary, first level indexed
                by ``{'frame': {<key>: <value>}, {'series': {<series name>: <desc>}}``.
            result (Optional[BundledResult]): For instantiating the report with pre-computed
                results from a profiler.
            profiler (Optional[BundledProfiler]): The `BundledProfiler` to run the profiling,
                defaults to `DefaultProfiler`.
            profiler_config (Optional[dict]): Profiler's configurations.
            scheduler (Optional[Scheduler]): A `Scheduler`, default's to `Scheduler`.
            scheduler_config (Optional[dict]): Scheduler's configurations.
            name (Optional[str]): The name Flask should use for your app. Even if you provide your
                own ``server``, ``name`` will be used to help find assets. Typically ``__name__``
                (the magic global var, not a string) is the best value to use.
                Default ``'__main__'``, env: ``DASH_APP_NAME``
            server_url (Optional[str]):  The base URL that the app will be served at, from the
                perspective of the client. If not specified, will default to the host argument
                passed to the ``run_server`` method.
            kwargs: Refer to ``dash.Dash`` documentation.
        """
        super().__init__(
            df=df,
            meta=meta,
            result=result,
            profiler=profiler,
            profiler_config=profiler_config,
            scheduler=scheduler,
            scheduler_config=scheduler_config,
        )
        assert df.shape[1] <= 20 and (
            result is None or len(result.result.series) <= 20
        ), "Dashboard not suitable for sets with more than 20 time series."
        assert (
            df.shape[0] < 10000
        ), "Dashboard not suitable time series with more than 10,000 datapoints."
        if df.shape[0] > 3500:
            warnings.warn("performance degrades significantly with long time series", UserWarning)

        self._app = TslumenDash(name=name, server_url=server_url, **kwargs)
        self._app.title = "tslumen"

        db_sections = [
            klass(self.result, self.meta or {}, self.df, self._app)  # type: ignore
            for klass in self.SECTIONS
        ]
        self.sections = {section.__class__.__name__: section for section in db_sections}
        nav = []
        for sec in db_sections:
            subnav = []
            if sec.anchors:
                subnav = html.Ul(
                    [
                        html.Li(html.A(title, href=f"#{block_id}", className="mt-2 anchor"))
                        for block_id, title in sec.anchors
                    ],
                    className="sublist-unstyled",
                )
                subnav = [subnav]
            nav.append(
                html.Li(
                    [
                        html.A(
                            sec.title,
                            href=f"#{sec.section_id}",
                            className="mt-2 anchor",
                        )
                    ]
                    + subnav
                )
            )

        sidebar = html.Div(
            [
                html.Div(className="logo"),
                html.Br(),
                html.Ul(nav, className="list-unstyled"),
            ],
            className="sidebar",
        )
        content = html.Div(
            html.Div(
                [html.Section(sec.layout) for sec in db_sections],
                className="content-inner",
            ),
            className="content",
        )

        self._app.layout = html.Div([sidebar, content])

    @property
    def app(self) -> TslumenDash:
        return self._app

    @property
    def server(self) -> Any:
        return self.app.server

    def run_server(
        self,
        mode: Optional[str] = None,
        width: Any = "100%",
        height: Any = 650,
        inline_exceptions: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Serve the app using flask in a background thread. You should not run this on a
        production server, use gunicorn/waitress instead.

        Args:
            mode (Optional[str]): Display mode. One of: ``"external"``: The URL of the app will be
                displayed in the notebook output cell. Clicking this URL will open the app in the
                default web browser; ``"inline"``: The app will be displayed inline in the notebook
                output cell in an iframe; ``"jupyterlab"``: The app will be displayed in a dedicate
                tab in the JupyterLab interface. Requires JupyterLab and the `jupyterlab-dash`
                extension.
            width: Width of app when displayed using mode="inline"
            height: Height of app when displayed using mode="inline"
            inline_exceptions: If True, callback exceptions are displayed inline in the the
                notebook output cell. Defaults to True if mode=="inline", False otherwise.
            kwargs: Additional keyword arguments to pass to the superclass ``Dash.run_server``
                method.
        """
        return self.app.run_server(
            mode=mode,
            width=width,
            height=height,
            inline_exceptions=inline_exceptions,
            **kwargs,
        )
