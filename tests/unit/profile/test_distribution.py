import pytest
from tests.unit.profile.base import *

from tslumen.profile.distribution import (
    binned, pd_quantiles, pd_percentiles
)

@pytest.mark.parametrize(
    "fn",
    (binned, pd_quantiles, pd_percentiles)
)
def test_stats_profiler(fn):
    check_profiler(fn)


def test_binned():
    np.random.seed(42)
    sin = mkts((120,)).iloc[:,0]
    sout = binned(sin, 8).result
    assert isinstance(sout, pd.Series)
    assert len(sout) == 8
    for start, end in zip(sout.index.tolist(), sout.index[1:].tolist() + [max(sin)+1]):
        assert ((sin >= start) & (sin < end)).sum() == sout.loc[start]

    sout = binned(sin).result
    assert len(sout) == 4

    sin[4:6] = np.nan
    sout = binned(sin).result
    assert len(sout) == 4


def _test_probplot(sin, fn, col, sum_theoretical, min_sample, max_sample):
    out = fn(sin).result
    assert isinstance(out, pd.DataFrame)
    assert out.columns.tolist() == [f'theoretical_{col}', f'sample_{col}', 'reference']
    assert round(out[f'theoretical_{col}'].sum(), 2) == sum_theoretical
    assert round(out[f'sample_{col}'].min(), 0) == min_sample
    assert round(out[f'sample_{col}'].max(), 0) == max_sample


def test_pdquantiles():
    np.random.seed(42)
    sin = mkts((120,)).iloc[:, 0]
    _test_probplot(sin, pd_quantiles, 'quantiles', 0, 0, 1)

    sin[4:6] = np.nan
    _test_probplot(sin, pd_quantiles, 'quantiles', 0, 0, 1)


def test_pdpercentiles():
    np.random.seed(42)
    sin = mkts((120,)).iloc[:, 0]
    _test_probplot(sin, pd_percentiles, 'percentiles', 60, 1, 1)

    sin[4:6] = np.nan
    _test_probplot(sin, pd_percentiles, 'percentiles', 59, 1, 1)