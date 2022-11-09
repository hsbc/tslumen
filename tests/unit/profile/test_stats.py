import pytest
from tests.unit.profile.base import *

from tslumen.profile.stats import (
    mean, var, std, median, mad, cov, minimum, maximum, q25, q50, q75, iqr, kurtosis, skew
)

@pytest.mark.parametrize(
    "fn",
    (mean, var, std, median, mad, cov, minimum, maximum, q25, q50, q75, iqr, kurtosis, skew)
)
def test_stats_profiler(fn):
    check_profiler(fn)


s1 = pd.Series(dtype=float)
s2 = pd.Series([1, 2, 3])
s3 = pd.Series([2.2,1.1,3.3,4.5,0,np.nan])

@pytest.mark.parametrize("fn,args,out", [
    # mean
    (mean, (s1,), float(np.nan)),
    (mean, (s2,), 2.0),
    (mean, (s3,), 2.22),

    # var
    (var, (s1,), float(np.nan)),
    (var, (s2,), 0.67),
    (var, (s3,), 2.51),

    # std
    (std, (s1,), float(np.nan)),
    (std, (s2,), 0.82),
    (std, (s3,), 1.58),

    # median
    (median, (s1,), float(np.nan)),
    (median, (s2,), 2.0),
    (median, (s3,), 2.2),

    # mad
    (mad, (s1,), float(np.nan)),
    (mad, (s2,), 1.0),
    (mad, (s3,), 1.1),

    # cov
    (cov, (s1,), float(np.nan)),
    (cov, (s2,), 0.41),
    (cov, (s3,), 0.71),

    # minimum
    (minimum, (s1,), float(np.nan)),
    (minimum, (s2,), 1.0),
    (minimum, (s3,), 0.0),

    # maximum
    (maximum, (s1,), float(np.nan)),
    (maximum, (s2,), 3.0),
    (maximum, (s3,), 4.5),

    # q25
    (q25, (s1,), float(np.nan)),
    (q25, (s2,), 1.5),
    (q25, (s3,), 1.1),

    # q50
    (q50, (s1,), float(np.nan)),
    (q50, (s2,), 2.0),
    (q50, (s3,), 2.22),

    # q75
    (q75, (s1,), float(np.nan)),
    (q75, (s2,), 2.5),
    (q75, (s3,), 3.3),

    # iqr
    (iqr, (s1,), float(np.nan)),
    (iqr, (s2,), 1.0),
    (iqr, (s3,), 2.2),

    # kurtosis
    (kurtosis, (s1,), float(np.nan)),
    (kurtosis, (s2,), -1.5),
    (kurtosis, (s3,), -1.28),

    # skew
    (skew, (s1,), float(np.nan)),
    (skew, (s2,), 0.0),
    (skew, (s3,), 0.0385),
])
def test_stats_exec(fn, args, out):
    return check_profile_exec(fn, args, out, almosteq)