import pytest
from tests.unit.profile.base import *

from tslumen.profile.summary import (
    n_series, length, dt_start, dt_end, freq, period, sz_total, df_scaled, zeros, missing, infinite, sample
)


@pytest.mark.parametrize(
    "fn", (
        n_series, length, dt_start, dt_end, freq, period, sz_total, df_scaled, zeros, missing, infinite, sample
    )
)
def test_summary_profilers(fn):
    return check_profiler(fn)



@pytest.mark.parametrize(
    "fn,args,out,comparer", [
    # n_series
    (n_series, (pd.DataFrame(),), 0, eq),
    (n_series, (csv2df('1\n2'),), 1, eq),
    (n_series, (csv2df('1,2,3\n2,3,4'),), 3, eq),

    # length
    (length, (pd.DataFrame(),), 0, eq),
    (length, (csv2df('1'),), 1, eq),
    (length, (csv2df('1,2,3\n2,3,4'),), 2, eq),

    # dt_start
    (dt_start, (csv2df('1', '1991-11-01'),), datetime(1991, 11, 1, 0, 0), eq),
    (dt_start, (csv2df('1\n2\n3', '2002-05-22 15:30', 'H'),), datetime(2002, 5, 22, 15, 30), eq),

    # dt_end
    (dt_end, (csv2df('1', '1991-11-01'),), datetime(1991, 11, 1, 0, 0), eq),
    (dt_end, (csv2df('1\n2\n3', '2002-05-22 15:30', 'H'),), datetime(2002, 5, 22, 17, 30), eq),

    # freq
    (freq, (mkts((120, 3), ff='Y'),), 'A-DEC', eq),
    (freq, (mkts((120, 3), ff='Q'),), 'Q-DEC', eq),
    (freq, (mkts((120, 3), ff='M'),), 'M', eq),
    (freq, (mkts((120, 3), ff='W'),), 'W-SUN', eq),
    (freq, (mkts((120, 3), ff='D'),), 'D', eq),
    (freq, (mkts((120, 3), ff='B'),), 'B', eq),
    (freq, (mkts((120, 3), ff='H'),), 'H', eq),

    # period
    (period, (mkts((120, 3), ff='Y'),), 1, eq),
    (period, (mkts((120, 3), ff='Q'),), 4, eq),
    (period, (mkts((120, 3), ff='M'),), 12, eq),
    (period, (mkts((120, 3), ff='W'),), 52, eq),
    (period, (mkts((120, 3), ff='D'),), 7, eq),
    (period, (mkts((120, 3), ff='B'),), 5, eq),
    (period, (mkts((120, 3), ff='H'),), 24, eq),
    (period, (mkts((120, 3), ff='S'),), None, eq),

    # sz_total
    (sz_total, (pd.DataFrame(),), 0, eq),
    (sz_total, (csv2df('1'),), 16, eq),
    (sz_total, (csv2df('1,2,3\n2,3,4'),), 64, eq),

    # df_scaled
    (df_scaled, (pd.DataFrame(),), pd.DataFrame(), dfeq),
    (df_scaled, (csv2df('1,2,3\n2,3,4'),), csv2df('0,0,0\n1,1,1'), dfeq),

    # zeros
    (zeros, (pd.Series([1, 1]),), 0, eq),
    (zeros, (pd.Series([0, 1, 2, 3]),), 1, eq),
    (zeros, (pd.Series([0, 1, 0, 3]),), 2, eq),

    # missing
    (missing, (pd.Series([1, 1]),), 0, eq),
    (missing, (pd.Series([0, 1, 2, np.nan]),), 1, eq),
    (missing, (pd.Series([np.nan, np.nan, np.nan]),), 3, eq),

    # infinite
    (infinite, (pd.Series([1, 1]),), 0, eq),
    (infinite, (pd.Series([0, 1, 2, np.inf]),), 1, eq),
    (infinite, (pd.Series([np.inf, np.inf, np.inf]),), 3, eq),

    # sample
    (sample, (pd.Series(list(range(100))), 6),
     pd.Series([0,1,2,97,98,99], index=[0,1,2,97,98,99]), dfeq),
    (sample, (pd.Series(list(range(100))), 5),
     pd.Series([0,1,98,99], index=[0,1,98,99]), dfeq),
])
def test_summary_exec(fn, args, out, comparer):
    return check_profile_exec(fn, args, out, comparer=comparer)
