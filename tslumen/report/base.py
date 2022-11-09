"""Base functionality for creating profiling Reports."""
from typing import Optional

import pandas as pd

from tslumen.scheduling import Scheduler
from tslumen.profile.base import BundledProfiler, BundledResult, valid_timeseries
from tslumen.profile import DefaultProfiler


__all__ = ["Report"]


class Report:
    """Base class for creating profiling Reports."""

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
        self._df = valid_timeseries(df)
        self._meta = meta or {}
        self.scheduler = scheduler or Scheduler(config=scheduler_config)
        self._profiler = profiler or DefaultProfiler(
            config=profiler_config or {}, scheduler=self.scheduler
        )
        self._result: Optional[BundledResult] = result

    def _taint(self) -> None:
        self._result = None

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @df.setter
    def df(self, value: pd.DataFrame) -> None:
        self._df = value
        self._taint()

    @property
    def meta(self) -> Optional[dict]:
        meta_frame = {key: str(value) for key, value in self._meta.get("frame", {}).items()}
        meta_series_ = self._meta.get("series", {})
        meta_series = {series: str(meta_series_.get(series, "")) for series in self._df.columns}
        return dict(frame=meta_frame, series=meta_series)

    @meta.setter
    def meta(self, value: Optional[dict]) -> None:
        self._meta = value or {}

    @property
    def profiler(self) -> BundledProfiler:
        return self._profiler

    @profiler.setter
    def profiler(self, value: BundledProfiler) -> None:
        self._profiler = value
        self._taint()

    @property
    def result(self) -> BundledResult:
        if not self._result:
            self._result = self.profiler.profile(self.df)
        return self._result

    @result.setter
    def result(self, value: BundledResult) -> None:
        self._taint()
        self._result = value
