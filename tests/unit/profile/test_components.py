import pytest
from tests.unit.profile.base import *

from tslumen.profile.components import stl, seasonal_split


@pytest.mark.parametrize(
    "fn",
    (stl, seasonal_split)
)
def test_stats_profiler(fn):
    check_profiler(fn)


def eq_stl(actual, expected):
    assert isinstance(actual, pd.DataFrame)
    assert actual.shape == expected['shape']
    if actual.shape[1] > 0:
        assert actual.columns.tolist() == ['trend', 'seasonality', 'residual']

def eq_seasonal_split(actual, expected):
    assert isinstance(actual, pd.DataFrame)
    assert actual.shape == expected['shape']
    if actual.shape[1] > 0:
        assert actual.index.dtype == np.dtype('O')
        assert list(actual.select_dtypes('number').columns) == list(actual.columns)


@pytest.mark.parametrize(
    "fn,args,out,comparer", [
        # stl
        (stl, (mkser(120, ff='Y'),), {'shape': (0, 0)}, eq_stl),
        (stl, (mkser(120, ff='Q'),), {'shape': (120, 3)}, eq_stl),
        (stl, (mkser(120, ff='M'),), {'shape': (120, 3)}, eq_stl),
        (stl, (mkser(120, ff='W'),), {'shape': (120, 3)}, eq_stl),
        (stl, (mkser(120, ff='D'),), {'shape': (120, 3)}, eq_stl),
        (stl, (mkser(120, ff='B'),), {'shape': (120, 3)}, eq_stl),
        (stl, (mkser(120, ff='H'),), {'shape': (120, 3)}, eq_stl),

        # seasonal_split
        (seasonal_split, (mkser(120, ff='Y'),), {'shape': (0, 0)}, eq_seasonal_split),
        (seasonal_split, (mkser(120, ff='Q'),), {'shape': (4, 31)}, eq_seasonal_split),
        (seasonal_split, (mkser(120, ff='M'),), {'shape': (12, 11)}, eq_seasonal_split),
        (seasonal_split, (mkser(120, ff='W'),), {'shape': (52, 4)}, eq_seasonal_split),
        (seasonal_split, (mkser(120, ff='D'),), {'shape': (31, 4)}, eq_seasonal_split),
        (seasonal_split, (mkser(120, ff='B'),), {'shape': (5, 25)}, eq_seasonal_split),
        (seasonal_split, (mkser(120, ff='H'),), {'shape': (24, 5)}, eq_seasonal_split),
])
def test_components(fn, args, out, comparer):
    return check_profile_exec(fn, args, out, comparer=comparer)