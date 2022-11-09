"""Package containing all the profiling functions, each operating at DataFrame or Series level,
organized based on the main aspect they focus on or common theme. Profiling functions can be
bundled as desired, the `BundledProfiler` class facilitates that."""
from tslumen.profile.base import BundledProfiler, ProfilingFunction, ProfileResult, BundledResult
from tslumen.profile import (
    summary,
    stats,
    stat_tests,
    distribution,
    correlation,
    components,
    smooth,
    features,
)

_modules = [
    summary,
    stats,
    stat_tests,
    distribution,
    correlation,
    components,
    smooth,
    features,
]
_all_profiling_functions = [
    getattr(mod, obj)
    for mod in _modules
    for obj in dir(mod)
    if isinstance(getattr(mod, obj), ProfilingFunction)
]


class DefaultProfiler(BundledProfiler):
    """Bundles all the profiling functions available in `tslumen.profile`, a convenient way to
    run a full analysis on any given timeseries dataset."""

    _profilers = _all_profiling_functions
