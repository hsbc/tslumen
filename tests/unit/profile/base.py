from datetime import datetime
from dataclasses import is_dataclass
import numpy as np
import pandas as pd
from tslumen.profile.base import ProfileResult, ProfilingFunction


def csv2df(csv, dtstart='1991-11-01', ff='D'):
    data = [[float(v) for v in r.split(',')] for r in csv.split('\n')]
    index = pd.date_range(dtstart, freq=ff, periods=len(data))
    return pd.DataFrame(data, index=index)


def mkts(size, dtstart='1911-11-01', ff='D'):
    return pd.DataFrame(
        np.random.random(size),
        index=pd.date_range(dtstart, freq=ff, periods=size[0])
    )


def mkser(sz, **kwargs):
    return mkts((sz, 1), **kwargs).iloc[:, 0]


def check_profiler(fn):
    assert isinstance(fn, ProfilingFunction)
    assert fn.is_pseries or fn.is_pframe, f"{fn} neither pseries nor pframe profiler"
    assert is_dataclass(fn.config), f"{fn} get_config not returning a 'dataclass'"


def eq(actual, expected):
    assert type(actual) == type(expected), f"Result type mismatch {type(actual)}, {type(expected)}"
    assert (actual != actual and expected != expected) or \
           (actual == expected), \
        f"Result differs: actual={actual} expected={expected}"


def almosteq(actual, expected, tol=0.01):
    assert type(actual) == type(expected), f"Result type mismatch {type(actual)}, {type(expected)}"
    assert (actual != actual and expected != expected) or \
           actual == expected or \
           abs(expected-actual)/abs(expected) < tol, \
        f"Result differs: actual={actual} expected={expected}"

def dfeq(actual, expected):
    assert type(actual) == type(expected), f"Result type mismatch {type(actual)}, {type(expected)}"
    assert actual.equals(expected), f"Result differs\n    actual={actual}\n  expected={expected}"

def check_profile_exec(fn, args, out, comparer):
    result = fn(*args)
    assert isinstance(result, ProfileResult), f"{type(result)} not ProfileResult"
    assert bool(result), f"result is {bool(result)} -> {str(result)}"
    assert result.exception is None, f"Expecting no exceptions, got {result.exception}"
    assert result.name == fn.__name__, f"Result name is {result.name}"
    assert result.scope in ['frame', 'series', 'both'], f"Invalid scope {result.scope}"
    assert isinstance(result.target, str), f"Target must be a string, got {type(result.target)}"
    assert isinstance(result.start, datetime), f"Start must be datetime, got {type(result.start)}"
    assert isinstance(result.end, datetime), f"Start must be datetime, got {type(result.end)}"
    assert result.start <= result.end, "Start time should be <= end"
    comparer(result.result, out)
