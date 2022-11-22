"""Module with the main class ``HtmlReport``."""
import io
from typing import Optional, List, Union
from datetime import datetime, timedelta

import pandas as pd

from tslumen.misc import lazyproperty
from tslumen.scheduling import Scheduler
from tslumen.profile.base import BundledProfiler, BundledResult
from tslumen.report.base import Report
from tslumen.report.html.base import HtmlBlock
from tslumen.report.html.sections import (
    SectionSummary,
    SectionTimeSeries,
    SectionTSFeatures,
    SectionRelations,
)

__all__ = ["HtmlReport"]


class HtmlReport(Report, HtmlBlock):
    """Renders the profiling results as an interactive, fully self-contained HTML report that
    can be downloaded and shared without the need for a running server or Python kernel.
    """

    SECTIONS = [
        SectionSummary,
        SectionTimeSeries,
        SectionTSFeatures,
        SectionRelations,
    ]
    _multiple_series = [SectionTSFeatures, SectionRelations]
    _sequential = [SectionTimeSeries]

    def __init__(
        self,
        df: pd.DataFrame,
        meta: Optional[dict] = None,
        result: Optional[BundledResult] = None,
        profiler: Optional[BundledProfiler] = None,
        profiler_config: Optional[dict] = None,
        scheduler: Optional[Scheduler] = None,
        scheduler_config: Optional[dict] = None,
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
        """
        assert df.shape[1] <= 20 and (
            result is None or len(result.result.series) <= 20
        ), "HtmlReport not suitable for sets with more than 20 time series."
        super().__init__(
            df=df,
            meta=meta,
            result=result,
            profiler=profiler,
            profiler_config=profiler_config,
            scheduler=scheduler,
            scheduler_config=scheduler_config,
        )
        self.sections: List[HtmlBlock] = []
        self.duration: Optional[timedelta] = None
        self._html = None

    def _taint(self) -> None:
        self._html = None
        self._result = None

    @lazyproperty
    def html(self) -> str:
        """Lazy loading property with the HTML representation of the report."""
        assert self.df.shape[1] <= 20 and (
            self._result is None or len(self._result.result.series) <= 20
        ), "HtmlReport not suitable for sets with more than 20 time series."
        start = datetime.now()
        meta = self.meta or {}

        # instantiate sections and build execution plan
        sequence: List[HtmlBlock] = []
        parallel: List[HtmlBlock] = []
        self.sections = []
        for klass in self.SECTIONS:
            if self.df.shape[1] <= 1 and klass in self._multiple_series:
                continue
            section = klass(self.result, meta, self.df, self.scheduler)
            self.sections.append(section)
            (sequence if klass in self._sequential else parallel).append(section)

        # execute sequential
        for section in sequence:
            _ = section.html
        # execute parallel
        _ = self.scheduler.run(
            lambda o: o.html,
            [(section,) for section in parallel],
            desc="Rendering remaining sections",
        )
        end = datetime.now()
        render_duration = end - start
        profile_duration = self.result.end - self.result.start
        self.duration = profile_duration + render_duration
        return str(super().html)

    def save(
        self,
        path_or_buffer: Optional[Union[str, io.TextIOBase]] = None,
        mode: str = "w",
        encoding: Optional[str] = None,
    ) -> Optional[str]:
        """Save rendered html to disk"""
        if path_or_buffer is None:
            return str(self.html_page)
        if isinstance(path_or_buffer, str):
            with open(path_or_buffer, mode=mode, encoding=encoding) as fp:
                fp.write(self.html_page)
        else:
            path_or_buffer.write(self.html_page)
        return None
