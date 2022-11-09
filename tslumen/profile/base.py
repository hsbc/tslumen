"""Base functionality for the profile package, including a dataclass for representing results and a
decorator for allowing profiling functions to be employed correctly, as well as automatically
capturing execution information."""
from typing import (
    Any,
    Optional,
    Union,
    Dict,
    List,
    Callable,
    Tuple,
    KeysView,
    ValuesView,
    ItemsView,
)
from dataclasses import dataclass, make_dataclass, field, asdict, is_dataclass
from functools import update_wrapper
from inspect import signature, Signature
from datetime import datetime
import warnings

from typing_inspect import is_union_type, get_args
import pandas as pd

from tslumen.scheduling import Scheduler
from tslumen.misc import repr_html

__all__ = [
    "TypeSeriesFrame",
    "ProfileException",
    "valid_timeseries",
    "ProfileResult",
    "ProfilingFunction",
    "BundledResult",
    "BundledResultDetails",
    "BundledProfiler",
]


TypeSeriesFrame = Union[pd.Series, pd.DataFrame]


class ProfileException(BaseException):
    pass


def valid_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Checks if the DataFrame meets the necessary criteria to be profiled: be a Pandas DataFrame,
    have values (must be numeric), have a DateTimeIndex, have a recognizable frequency/period.

    Args:
        df: Pandas DataFrame.

    Returns:
        pandas.DataFrame: A copy of the input containing only numeric series and a sorted index.
    """
    # check if valid time series
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Expecting 'df' to be a pandas.DataFrame")
    if not all([isinstance(c, str) for c in df.columns]):
        raise ValueError("All column names must be 'str'")
    df = df.select_dtypes("number").sort_index().copy()
    if df.shape[1] == 0 or len(df) == 0:
        raise ValueError("DataFrame cannot be empty")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Expecting DataFrame index to be a pandas.DateTimeIndex")
    if not df.index.inferred_freq:
        raise ValueError("Could not infer the DataFrame's frequency")
    return df


class _DCDict:
    def __iter__(self) -> Any:
        return iter(asdict(self).items())

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def keys(self) -> KeysView:
        return asdict(self).keys()

    def values(self) -> ValuesView:
        return asdict(self).values()

    def items(self) -> ItemsView:
        return asdict(self).items()


@repr_html
@dataclass(init=False)
class ProfileResult(_DCDict):
    """For recording the results of a profiling operation."""

    name: str
    scope: str
    target: str
    start: datetime
    end: datetime
    success: bool
    warnings: List[warnings.WarningMessage]
    exception: Optional[ProfileException]
    result: Optional[Any]

    def __init__(self) -> None:
        self.warnings = []
        self.exception = None
        self.success = True

    def __bool__(self) -> bool:
        return self.success


@repr_html
class ProfilingFunction:
    """Decorator for turning a function into a profiler. Inspects the function's signature and
    builds a dataclass representing its configurations (for integrating with ``Hydra``). Adds two
    attributes ``is_pseries`` and ``is_pframe`` to distinguish whether it targets Series or
    DataFrames. This is inferred based on the type annotation of the first parameter. Captures the
    start and end timestamps, the return value, as well as any warnings or exceptions raised during
    the execution.

    Args:
        fn (Callable): Profiler function to decorate.
    """

    is_pframe: bool = False
    is_pseries: bool = False
    config: Any
    fn: Callable
    sig: Signature
    _par_data: str

    def __init__(self, fn: Callable) -> None:
        update_wrapper(self, fn)
        p_configs = []
        self.sig = signature(fn)
        assert (
            len(self.sig.parameters) >= 1
        ), "Profiling function requires at least 1 argument, the timeseries"
        for i, (name, par) in enumerate(self.sig.parameters.items()):
            assert par.annotation, f"Parameter {name} must be annotated"
            if i == 0:
                self._par_data = par.name
                if is_union_type(par.annotation):
                    data_types = get_args(par.annotation)
                else:
                    data_types = [par.annotation]
                self.is_pseries = pd.Series in data_types
                self.is_pframe = pd.DataFrame in data_types
                assert (
                    self.is_pseries or self.is_pframe
                ), f"First argument '{name}' must be a Series or DataFrame"
            else:
                p_configs.append((name, par.annotation, field(default=par.default)))
        self.config = make_dataclass("Config", p_configs)
        self.fn = fn  # type: ignore

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        result = ProfileResult()
        result.start = datetime.now()
        result.name = self.fn.__name__
        result.warnings = []
        try:
            bargs = self.sig.bind(*args, **kwargs)
            data = bargs.arguments[self._par_data]
            result.scope = "frame" if isinstance(data, pd.DataFrame) else "series"
            result.target = str(getattr(data, "name", "") or "" if result.scope == "series" else "")
            with warnings.catch_warnings(record=True) as w:
                result.result = self.fn(*args, **kwargs)
                result.success = True
                result.warnings += w
        except Exception as e:
            result.result = None
            result.success = False
            result.exception = ProfileException(e)
        finally:
            result.end = datetime.now()
        return result


@repr_html
@dataclass(init=False)
class BundledResultDetails(_DCDict):
    frame: Dict[str, Any]
    series: Dict[str, Dict[str, Any]]
    exec_details: pd.DataFrame
    config: Dict[str, Dict[str, Any]]


@dataclass(init=False)
class BundledResult(ProfileResult):
    result: BundledResultDetails


@repr_html
class BundledProfiler:
    """Base class for creating bundled profilers.

    Contains functionality to manage configurations, orchestrate the execution of the profiling
    functions and collate the results. It's up for the subclasses to decide on which profiling
    functions to include, done so by assigning a list with said profiling functions to the
    class variable `_profilers`.
    """

    _profilers: List[ProfilingFunction]

    @classmethod
    def get_profilers(cls, target: str = "any") -> Dict[str, ProfilingFunction]:
        """
        Args:
            target: {'series', 'frame', 'any'}, default 'any'
                Filter by function target (single series, data frame, or any/no filter).

        Returns:
            dict: Bundled profilers, profiler name => profiler function.
        """
        valid = {
            "series": lambda p: p.is_pseries,
            "frame": lambda p: p.is_pframe,
            "any": lambda p: True,
        }
        assert target in valid, f"Invalid target '{target}', valid options: {valid.keys()}"
        clause: Callable = valid[target]
        return {p.fn.__name__: p for p in cls._profilers if clause(p)}

    @classmethod
    def get_config_defaults(cls, as_dict: bool = True) -> Dict[str, Any]:
        """
        Returns:
            dict: Bundled configurations (defaults), profiler name => configuration.
        """
        configs = {}
        for name, p in cls.get_profilers().items():
            cfg = p.config()
            configs[name] = asdict(cfg) if as_dict else cfg
        return configs

    def __init__(
        self,
        config: Optional[Dict[str, Dict[str, Any]]] = None,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        """
        Args:
            config (Optional[dict]): Profiler functions' configurations. Whatever options are
                provided here will override the defaults. Expects a 2-level dictionary with the
                first level indexed by the name of the profiling functions and the second level
                the function's parameters. Assumed configs (i.e. defaults + overrides) are stored
                in the class variable `config`.
            scheduler (Optional[Scheduler]): For executing the profiling functions. Instantiates
                the default one if not provided.
        """
        self.config = self.get_config_defaults()
        if config:
            for p, cfg in config.items():
                self.config[p] = asdict(cfg) if is_dataclass(cfg) else cfg
        self.scheduler = scheduler or Scheduler()

    def profile(self, df: pd.DataFrame) -> BundledResult:
        """Executes the profiling functions on the supplied DataFrame.

        Args:
            df (pd.DataFrame): TimeSeries data to be profiled.

        Returns:
            ProfileResult: Result of the profiling.
        """

        def _run(
            fn: ProfilingFunction, data: Union[pd.DataFrame, pd.Series], config: dict
        ) -> Tuple[str, Any, pd.Series]:
            pr_ = fn(data, **config)
            details_ = pd.Series(
                {
                    "Profiler": pr_.name,
                    "Scope": pr_.scope,
                    "Target": pr_.target,
                    "Start": pr_.start,
                    "End": pr_.end,
                    "Duration": pr_.end - pr_.start,
                    "Succeeded": pr_.success,
                    "Exceptions": pr_.exception,
                    "# Runs": 1,
                }
            )
            return pr_.name, pr_.result, details_

        df = valid_timeseries(df)

        result = BundledResult()
        result.start = datetime.now()
        result.name = self.__class__.__name__
        result.scope = "both"
        result.target = ""
        result.result = BundledResultDetails()
        result.result.config = self.config
        result.result.frame = {}
        result.result.series = {col: {} for col in df.columns}
        exec_stats = []
        plan = [
            (fn, df, self.config[name]) for name, fn in self.get_profilers(target="frame").items()
        ] + [
            (fn, df[column], self.config[name])
            for name, fn in self.get_profilers(target="series").items()
            for column in df.columns
        ]
        executed = self.scheduler.run(_run, plan, desc="Profiling")
        for name, res, stats in executed:
            if stats.Scope == "frame":
                result.result.frame[name] = res
            else:
                result.result.series[stats.Target][name] = res
            exec_stats.append(stats)
        result.result.exec_details = pd.DataFrame(exec_stats)
        result.end = datetime.now()
        return result
