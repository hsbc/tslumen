import pandas as pd

from tslumen.report.base import Report
from tslumen.scheduling import Scheduler
from tslumen.profile import summary
from tslumen.profile.base import BundledProfiler, ProfileResult
from tslumen.profile import DefaultProfiler


def test_report_meta():
    df = pd.DataFrame({'a': [1,2,3]}, index=pd.date_range('1990-01-01', '1990-01-03', freq='D'))
    r = Report(df.copy())
    assert r.df.equals(df)
    assert r.meta == {'frame': {}, 'series': {'a': ''}}

    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]},
                      index=pd.date_range('1990-01-01', '1990-01-03', freq='D'))
    r = Report(df.copy())
    assert r.df.equals(df)
    assert r.meta == {'frame': {}, 'series': {'a': '', 'b': ''}}

    r = Report(df.copy(),
               {'frame': {'A': 1, 'B': 2},
                'series': {'a': 'x', 'b': 'y', 'c': 'ERROR'},
                'ignore me': 'yes'})
    assert r.df.equals(df)
    assert r.meta == {'frame': {'A': '1', 'B': '2'},
                      'series': {'a': 'x', 'b': 'y'}}


def test_report_configs():
    df = pd.DataFrame({'a': [1,2,3]}, index=pd.date_range('1990-01-01', '1990-01-03', freq='D'))
    r = Report(df)
    assert isinstance(r.scheduler, Scheduler)
    assert isinstance(r.profiler, DefaultProfiler)
    assert r.scheduler.config == Scheduler().config
    assert r.profiler.config == DefaultProfiler().config

    r = Report(df,
               profiler_config={'test': 1},
               scheduler_config={'n_jobs': 82})
    assert isinstance(r.scheduler, Scheduler)
    assert isinstance(r.profiler, DefaultProfiler)
    assert r.scheduler.config['n_jobs'] == 82
    assert r.profiler.config['test'] == 1
    assert r.profiler.scheduler == r.scheduler

    r = Report(df,
               profiler=DefaultProfiler(),
               scheduler=Scheduler(),
               profiler_config={'test': 1},
               scheduler_config={'n_jobs': 82})
    assert r.scheduler.config == Scheduler().config
    assert r.profiler.config == DefaultProfiler().config


def test_report_result():
    class Seq:
        def run(self, fn, args, desc = ""):
            return [fn(*arg) for arg in args]

    class X(BundledProfiler):
        _profilers = [summary.n_series]

    class Y(BundledProfiler):
        _profilers = [summary.length]

    sc = Seq()
    r = Report(pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]},
                            index=pd.date_range('1990-01-01', '1990-01-03', freq='D')),
               profiler=X(scheduler=sc), scheduler=sc)
    assert isinstance(r.scheduler, Seq)
    assert isinstance(r.result, ProfileResult)
    assert r.result.result.frame['n_series'] == 2
    assert r.meta == {'frame': {}, 'series': {'a': '', 'b': ''}}
    r.df = pd.DataFrame({'a': [1,2,3]}, index=pd.date_range('1990-01-01', '1990-01-03', freq='D'))
    assert r.result.result.frame['n_series'] == 1
    assert r.meta == {'frame': {}, 'series': {'a': ''}}
    r.meta = {'frame': {'desc': 'hola!'}}
    assert r.meta == {'frame': {'desc': 'hola!'}, 'series': {'a': ''}}
    r.profiler = Y(scheduler=sc)
    assert r.result.result.frame['length'] == 3

    r.result = 'foobar'
    assert r.result == 'foobar'
