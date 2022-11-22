import pytest
import mock
import re
from tests.unit.profile.base import *

from tslumen.profile.correlation import (
    acf, acf_1d, acf_2d, pacf, pacf_1d, pacf_2d, lag_corr, corr_pearson, corr_kendall,
    corr_spearman, granger_causality,
)

@pytest.mark.parametrize(
    "fn",
    (acf, acf_1d, acf_2d, pacf, pacf_1d, pacf_2d, lag_corr, corr_pearson, corr_kendall,
    corr_spearman, granger_causality)
)
def test_stat_tests_profiler(fn):
    check_profiler(fn)


@pytest.mark.parametrize(
    "fnmock, fn, diff, kwargs, call_with",
    [
        ('acf', acf, 0, {}, {}),
        ('acf', acf, 0, dict(lags=23,adjusted=True,fft=True,alpha=0.1,missing='x'), dict(nlags=23,adjusted=True,fft=True,alpha=0.1,missing='x')),
        ('acf', acf_1d, 1, {}, {}),
        ('acf', acf_1d, 1, dict(lags=23,adjusted=True,fft=True,alpha=0.1,missing='x'), dict(nlags=23,adjusted=True,fft=True,alpha=0.1,missing='x')),
        ('acf', acf_2d, 2, {}, {}),
        ('acf', acf_2d, 2, dict(lags=23,adjusted=True,fft=True,alpha=0.1,missing='x'), dict(nlags=23,adjusted=True,fft=True,alpha=0.1,missing='x')),
        ('pacf', pacf, 0, {}, {}),
        ('pacf', pacf, 0, dict(lags=12, method='x',alpha=0.1), dict(nlags=12, method='x',alpha=0.1)),
        ('pacf', pacf_1d, 1, {}, {}),
        ('pacf', pacf_1d, 1, dict(lags=12, method='x',alpha=0.1), dict(nlags=12, method='x',alpha=0.1)),
        ('pacf', pacf_2d, 2, {}, {}),
        ('pacf', pacf_2d, 2, dict(lags=12, method='x',alpha=0.1), dict(nlags=12, method='x',alpha=0.1)),
    ])
def test_acf(fnmock, fn, diff, kwargs, call_with):
    path = f'tslumen.profile.correlation.sms.{fnmock}'

    with mock.patch(path, autospec=True) as fun:
        fun.return_value = np.arange(40), np.array([np.arange(40), np.arange(40)]).T
        ser = mkser(120)
        serd = pd.Series(np.diff(ser.values, diff), index=ser.index[diff:])
        actual = fn(ser, **kwargs).result
        assert isinstance(actual, pd.DataFrame)
        assert actual.columns.tolist() == ['lag', 'correlation', 'low', 'up']
        assert actual.lag.tolist() == list(range(40))
        assert actual.correlation.tolist() == list(range(40))
        assert actual.low.tolist()[1:] == [0.0] * 39
        assert actual.up.tolist()[1:] == [0.0] * 39
        assert np.isnan(actual.low[0])
        assert np.isnan(actual.up[0])
        assert fun.call_count == 1
        assert fun.call_args[0][0].equals(serd)
        call_args = fun.call_args[1]
        for par, val in call_with.items():
            assert par in call_args
            assert call_args[par] == val


@pytest.mark.parametrize(
    "ser, lags",
    [
        (mkser(120, ff='Y'), None),
        (mkser(120, ff='Q'), None),
        (mkser(120, ff='M'), None),
        (mkser(120, ff='W'), None),
        (mkser(120, ff='D'), None),
        (mkser(120, ff='B'), None),
        (mkser(120, ff='H'), None),
        (mkser(120, ff='Y'), (1, 3, 5)),
        (mkser(120, ff='Q'), (1, 3, 5)),
        (mkser(120, ff='M'), (1, 3, 5)),
        (mkser(120, ff='W'), (1, 3, 5)),
        (mkser(120, ff='D'), (1, 3, 5)),
        (mkser(120, ff='B'), (1, 3, 5)),
        (mkser(120, ff='H'), (1, 3, 5)),
])
def test_lag_corr(ser, lags):
    df_lags, df_corr = lag_corr(ser, lags=lags).result
    assert isinstance(df_lags, pd.DataFrame)
    assert isinstance(df_corr, pd.Series)
    assert df_lags.columns[0] == 'original'
    for col in df_lags.columns[1:]:
        assert col.startswith('lag ')
        lag = int(re.sub('[^0-9]', '', col))
        assert df_lags[col].equals(ser.shift(lag))
    assert (df_corr.dropna() <= 1.0).all()
    assert (df_corr.dropna() >= -1.0).all()
    assert df_corr.index.tolist() == df_lags.columns.tolist()



@pytest.mark.parametrize(
    "fn, method",
    [(corr_pearson, 'pearson'),
     (corr_kendall, 'kendall'),
     (corr_spearman, 'spearman')]
)
def test_corr(fn, method):
    df = mkts((120, 5))
    df_expected = df.copy().corr(method=method)
    df_actual = fn(df.copy()).result
    assert isinstance(df_actual, pd.DataFrame)
    assert df_actual.equals(df_expected)


def test_granger():
    a1 = pd.Series([
        20.0, 20.497, 20.358, 21.006, 22.529, 22.295, 22.061, 23.64, 24.408, 23.938, 24.481, 24.017,
        23.551, 23.793, 21.88, 20.155, 19.593, 18.58, 18.894, 17.986, 16.574, 18.04, 17.814, 17.881,
        16.457, 15.912, 16.023, 14.872, 15.248, 14.647, 14.356, 13.754, 15.606, 15.593, 14.535,
        15.358, 14.137, 14.346, 12.386, 11.058, 11.255, 11.993, 12.164, 12.049, 11.748, 10.269,
        9.549, 9.089, 10.146, 10.489, 8.726, 9.05, 8.665, 7.988, 8.6, 9.631, 10.562, 9.723, 9.414,
        9.745, 10.721, 10.242, 10.056, 8.95, 7.753, 8.566, 9.922, 9.85, 10.854, 11.215, 10.57, 10.932
    ])  # random walk
    a2 = a1*3
    a3 = a1*1.37
    df_a = pd.DataFrame(dict(a1=a1, a2=a2, a3=a3))

    np.random.seed(30)
    b1 = pd.Series(np.random.randn(120) * 2 + 1)
    b2 = pd.Series(np.random.randn(120) * 3.37 - 2.13)
    b3 = pd.Series(np.random.randn(120) * 7.3 + 4)
    df_b = pd.DataFrame(dict(b1=b1, b2=b2, b3=b3))

    dfp, dfl, d = granger_causality(df_a).result
    assert d == 1
    assert dfp.shape == (3, 3)
    assert dfl.shape == (3, 3)
    assert dfp.columns.tolist()  == ['a1[x]', 'a2[x]', 'a3[x]']
    assert dfp.index.tolist() == ['a1[y]', 'a2[y]', 'a3[y]']
    assert dfl.columns.tolist() == dfp.columns.tolist()
    assert dfl.index.tolist() == dfp.index.tolist()
    assert set(dfp.dtypes) == {np.dtype('float')}
    assert set(dfl.dtypes) == {np.dtype('int')}
    assert np.isnan(np.diag(dfp)).all()
    assert (np.diag(dfl) == -1).all()

    dfp, dfl, d = granger_causality(df_b).result
    assert d == 0
    assert dfp.shape == (3, 3)
    assert dfl.shape == (3, 3)
    assert dfp.columns.tolist() == ['b1[x]', 'b2[x]', 'b3[x]']
    assert dfp.index.tolist() == ['b1[y]', 'b2[y]', 'b3[y]']
    assert dfl.columns.tolist() == dfp.columns.tolist()
    assert dfl.index.tolist() == dfp.index.tolist()
    assert set(dfp.dtypes) == {np.dtype('float')}
    assert set(dfl.dtypes) == {np.dtype('int')}
    assert np.isnan(np.diag(dfp)).all()
    assert (np.diag(dfl) == -1).all()

    with mock.patch('tslumen.profile.correlation.sms.grangercausalitytests', autospec=True) as fun:
        fun.return_value = {n: {0: {'x': (None, 0.1, 2), 'y': (9,9,9)}} for n in range(1, 4)}
        dfp, dfl, d = granger_causality(df_b, test='x', addconst=False, maxlag=3).result
        assert fun.call_count == 6
        args = pd.DataFrame([call[1] for call in fun.call_args_list]).drop_duplicates()
        assert args.shape == (1, 3)
        assert args.loc[0, 'addconst'] == False
        assert args.loc[0, 'maxlag'] == 3
