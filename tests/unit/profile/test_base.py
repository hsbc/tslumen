import pytest
from typing import Union
from dataclasses import is_dataclass
from datetime import datetime
import pandas as pd
from tslumen.profile.base import ProfileException, ProfileResult, ProfilingFunction, BundledProfiler, BundledResult, valid_timeseries


def test_validtimeseries():
    with pytest.raises(ValueError):
        valid_timeseries(1)
    with pytest.raises(ValueError):
        valid_timeseries(None)
    with pytest.raises(ValueError):
        valid_timeseries(pd.DataFrame())
    with pytest.raises(ValueError):
        valid_timeseries(pd.DataFrame({True: ['a', 'b', 'c']}))
    with pytest.raises(ValueError):
        valid_timeseries(pd.DataFrame({1: ['a', 'b', 'c']}))
    with pytest.raises(ValueError):
        valid_timeseries(pd.DataFrame({'a': ['a', 'b', 'c']}))
    with pytest.raises(ValueError):
        valid_timeseries(pd.DataFrame({'a': [1, 2, 3]}))
    with pytest.raises(ValueError):
        valid_timeseries(pd.DataFrame({'a': [1, 2, 3]}, index=[datetime.now()]*3))


def test_profileexception():
    assert issubclass(ProfileException, BaseException)
    with pytest.raises(ProfileException):
        raise ProfileException


def test_profileresult():
    pr = ProfileResult()
    assert pr.exception is None
    assert pr.success
    assert bool(pr)

    pr.start = datetime.now()
    pr.name = 'the name'
    pr.scope = 'the scope'
    pr.target = 'the target'
    pr.success = False
    pr.warnings = []
    pr.exception = ProfileException()
    pr.result = 'the result'
    pr.end = datetime.now()

    assert pr.name == 'the name'
    assert pr.scope == 'the scope'
    assert pr.target == 'the target'
    assert pr.result == 'the result'
    assert pr.success is False
    assert bool(pr) is False
    assert pr.warnings == []
    assert isinstance(pr.exception, ProfileException)
    assert isinstance(pr.start, datetime)
    assert isinstance(pr.end, datetime)
    assert pr.end >= pr.start

    assert pr['name'] == pr.name
    assert pr['scope'] == pr.scope
    assert pr['target'] == pr.target
    assert pr['result'] == pr.result
    assert pr['success'] == pr.success
    assert pr['exception'] == pr.exception
    assert pr['start'] == pr.start
    assert pr['end'] == pr.end

    pr.exception = None
    assert dict(pr) == {
        'name': pr.name,
        'scope': pr.scope,
        'target': pr.target,
        'result': pr.result,
        'success': pr.success,
        'warnings': pr.warnings,
        'exception': pr.exception,
        'start': pr.start,
        'end': pr.end,
    }

    for k, val in pr:
        assert isinstance(k, str)
        assert val == getattr(pr, k)

    assert len(pr.keys()) == len(pr.values())
    assert len(pr.items()) == len(pr.values())


def _test_profiler(fn, args,
                   r_is_pseries, r_is_pframe,
                   result):
    assert fn.is_pseries == r_is_pseries
    assert fn.is_pframe == r_is_pframe
    assert is_dataclass(fn.config)

    ret = fn(args)
    assert isinstance(ret, ProfileResult)
    assert bool(ret)
    assert ret.exception is None
    assert ret.end >= ret.start
    for k, val in result.items():
        assert ret[k] == val, f"Error checking {k}, expected {val} got {ret[k]}"


@ProfilingFunction
def fun_series(data: pd.Series) -> str:
    return data.name or "no name"


@ProfilingFunction
def fun_frame(data: pd.DataFrame) -> str:
    return f'frame{data.shape}'


@ProfilingFunction
def fun_either(data: Union[pd.Series, pd.DataFrame]) -> str:
    return f'i am a {data.__class__.__name__}'


def test_profiler_series():
    _test_profiler(fun_series, pd.Series(name='alpha', dtype=float),
                   True, False,
                   dict(name="fun_series",
                        scope="series",
                        target="alpha",
                        result="alpha",
                        success=True))


def test_profiler_frame():
    _test_profiler(fun_frame, pd.DataFrame(),
                   False, True,
                   dict(name="fun_frame",
                        scope="frame",
                        target="",
                        result="frame(0, 0)",
                        success=True))


def test_profiler_either():
    _test_profiler(fun_either, pd.Series(dtype=float),
                   True, True,
                   dict(name="fun_either",
                        scope="series",
                        target="",
                        result="i am a Series",
                        success=True))
    _test_profiler(fun_either, pd.DataFrame(),
                   True, True,
                   dict(name="fun_either",
                        scope="frame",
                        target="",
                        result="i am a DataFrame",
                        success=True))


def test_profiler_bad_fun():
    with pytest.raises(AssertionError):
        @ProfilingFunction
        def no_fun(data: int) -> str:
            return 'error'


def test_profiler_raises():
    ret = fun_frame(1)
    assert not ret.success
    assert not bool(ret)
    assert ret.exception is not None
    assert isinstance(ret.exception, ProfileException)


def test_bundledprofiler():
    class DummyA(BundledProfiler):
        _profilers = []

    class DummyB(BundledProfiler):
        _profilers = [fun_series]

    class DummyC(BundledProfiler):
        _profilers = [fun_frame]

    class DummyD(BundledProfiler):
        _profilers = [fun_series, fun_frame, fun_either]

    assert DummyA.get_profilers() == {}
    assert DummyA.get_config_defaults() == {}
    assert DummyA.get_profilers(target='frame') == {}
    assert DummyA.get_profilers(target='series') == {}

    assert list(DummyB.get_profilers()) == ['fun_series']
    assert list(DummyB.get_config_defaults()) == ['fun_series']
    assert list(DummyB.get_profilers(target='frame')) == []
    assert list(DummyB.get_profilers(target='series')) == ['fun_series']
    assert all([is_dataclass(c) for c in DummyB.get_config_defaults(False).values()])
    assert all([c.is_pframe for c in DummyB.get_profilers(target='frame').values()])
    assert all([c.is_pseries for c in DummyB.get_profilers(target='series').values()])

    assert list(DummyC.get_profilers()) == ['fun_frame']
    assert list(DummyC.get_config_defaults()) == ['fun_frame']
    assert list(DummyC.get_profilers(target='frame')) == ['fun_frame']
    assert list(DummyC.get_profilers(target='series')) == []
    assert all([isinstance(c, dict) for c in DummyC.get_config_defaults().values()])
    assert all([c.is_pframe for c in DummyC.get_profilers(target='frame').values()])
    assert all([c.is_pseries for c in DummyC.get_profilers(target='series').values()])

    assert list(DummyD.get_profilers()) == ['fun_series', 'fun_frame', 'fun_either']
    assert list(DummyD.get_config_defaults()) == ['fun_series', 'fun_frame', 'fun_either']
    assert list(DummyD.get_profilers(target='frame')) == ['fun_frame', 'fun_either']
    assert list(DummyD.get_profilers(target='series')) == ['fun_series', 'fun_either']
    assert all([is_dataclass(c) for c in DummyD.get_config_defaults(False).values()])
    assert all([c.is_pframe for c in DummyD.get_profilers(target='frame').values()])
    assert all([c.is_pseries for c in DummyD.get_profilers(target='series').values()])

    a1 = DummyA(config={'a': {'x': 1}})
    a2 = DummyA(scheduler=1)
    assert a1.config == {'a': {'x': 1}}
    assert a2.config == {}
    assert a2.scheduler == 1

    class XScheduler:
        def run(self, fn, args, desc):
            return [fn(*arg) for arg in args]

    d = DummyD(scheduler=XScheduler())
    ret = d.profile(pd.DataFrame({'a': [1,2,3], 'b': [4, 5, 6]},
                                 index=pd.date_range('1990-01-01', '1990-01-03', freq='D')))
    assert is_dataclass(ret)
    assert isinstance(ret, BundledResult)
    assert ret.success
    assert list(ret.result.frame.keys()) == ['fun_frame', 'fun_either']
    assert list(ret.result.series.keys()) == ['a', 'b']
    assert ret.result.config == {'fun_frame': {}, 'fun_series': {}, 'fun_either': {}}
    assert isinstance(ret.result.exec_details, pd.DataFrame)
    assert len(ret.result.exec_details.query('~ Succeeded')) == 0
    assert len(ret.result.exec_details) == 6
