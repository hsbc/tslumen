import pytest
import mock
from tests.unit.profile.base import *

from tslumen.profile.smooth import (
    lowess, rolling_avg, supsmu
)


@pytest.mark.parametrize(
    "fn",
    (lowess, rolling_avg, supsmu)
)
def test_stats_profiler(fn):
    check_profiler(fn)


def test_lowess():
    path = 'tslumen.profile.smooth.smoothers_lowess.lowess'
    side_effect = lambda data, *args, **kwargs: np.array([[0] * len(data), [kwargs['frac']] * len(data)]).T

    with mock.patch(path, side_effect=side_effect, autospec=True) as smoother:
        ser = pd.Series([-2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3])
        p = lowess(ser).result
        assert isinstance(p, pd.DataFrame)
        assert smoother.call_count == 3
        assert p.columns.tolist() == ['original', 'lowess  5%', 'lowess 10%', 'lowess 15%']
        assert p.iloc[:, 0].equals(ser)
        assert p['lowess  5%'].tolist() == [0.05]*len(ser)
        assert p['lowess 10%'].tolist() == [0.10]*len(ser)
        assert p['lowess 15%'].tolist() == [0.15]*len(ser)

    with mock.patch(path, side_effect=side_effect, autospec=True) as smoother:
        ser = pd.Series([-2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3])
        p = lowess(ser, fracs = (0.7, 0.95), it = 1, delta = 0.1, missing = 'keep').result
        assert isinstance(p, pd.DataFrame)
        assert smoother.call_count == 2
        for call in smoother.call_args_list:
            assert call[1]['frac'] in [0.7, 0.95]
            assert call[1]['it'] == 1
            assert call[1]['delta'] == 0.1
            assert call[1]['missing'] == 'keep'
        assert p.columns.tolist() == ['original', 'lowess 70%', 'lowess 95%']
        assert p.iloc[:, 0].equals(ser)
        assert p['lowess 70%'].tolist() == [0.70]*len(ser)
        assert p['lowess 95%'].tolist() == [0.95]*len(ser)


def eq_ravg(actual, expected):
    assert isinstance(actual, pd.DataFrame)
    assert actual.shape == expected['shape']
    if actual.shape[1] > 0:
        assert actual.columns[0] == 'original'
        assert actual.columns[1:].tolist() == [f'rolling {l}{expected["freq"]}' for l in expected["w"]]
        for l in expected["w"]:
            assert round(actual[f'rolling {l}{expected["freq"]}'], 2).equals(round(actual['original'].rolling(l).mean(), 2))


@pytest.mark.parametrize(
    "args,out,comparer", [
        # stl
        ((mkser(  80, ff='Y'),), {'shape': (  80, 4), 'freq': 'A', "w": [3, 4, 5]}, eq_ravg),
        ((mkser( 100, ff='Q'),), {'shape': ( 100, 4), 'freq': 'Q', "w": [2, 4, 8]}, eq_ravg),
        ((mkser( 120, ff='M'),), {'shape': ( 120, 4), 'freq': 'M', "w": [3, 6, 12]}, eq_ravg),
        ((mkser( 420, ff='W'),), {'shape': ( 420, 4), 'freq': 'W', "w": [4, 8, 12]}, eq_ravg),
        ((mkser(1220, ff='D'),), {'shape': (1220, 5), 'freq': 'D', "w": [7, 14, 30, 90]}, eq_ravg),
        ((mkser(1220, ff='B'),), {'shape': (1220, 5), 'freq': 'B', "w": [5, 10, 20, 60]}, eq_ravg),
        ((mkser(8220, ff='H'),), {'shape': (8220, 5), 'freq': 'H', "w": [12, 24, 168, 720]}, eq_ravg),
])
def test_rolling_avg(args, out, comparer):
    return check_profile_exec(rolling_avg, args, out, comparer=comparer)


def test_supsmu():
    path_ss = 'tslumen.profile._supsmu.SuperSmoother'
    path_ols = 'tslumen.profile._supsmu.OLS'

    with mock.patch(path_ss, autospec=True) as smoother:
        with mock.patch(path_ols, autospec=True) as ols:
            ser = pd.Series([42] * 28)
            smoother.return_value.predict.return_value = (ser * -1).values
            ols.return_value.fit.return_value.predict.return_value = (ser * 0).values
            p = supsmu(ser).result
            assert isinstance(p, pd.DataFrame)
            assert smoother.call_count == 0
            assert ols.call_count == 2
            assert p.columns.tolist() == ['original', 'supsmu']
            assert p['original'].equals(ser)
            assert (p['supsmu'][:4].values == 0).all()
            assert (p['supsmu'][-4:].values == 0).all()
            assert (p['supsmu'][4:-4].values == 42).all()

    with mock.patch(path_ss, autospec=True) as smoother:
        ser = pd.Series([-2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3] * 8)
        smoother.return_value.predict.return_value = (ser * -1).values
        p = supsmu(ser).result
        assert isinstance(p, pd.DataFrame)
        assert smoother.call_count == 1
        assert p.columns.tolist() == ['original', 'supsmu']
        assert p['original'].equals(ser)
        assert p['supsmu'].equals(-1*ser)

    with mock.patch(path_ss, autospec=True) as smoother:
        ser = pd.Series([-2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3, -2, 3] * 8)
        smoother.return_value.predict.return_value = (ser * -1).values
        p = supsmu(ser, alpha=0.1, period=2.2, primary_spans=(0.1, 0.8), middle_span=0.12, final_span=0.15).result
        assert isinstance(p, pd.DataFrame)
        assert smoother.call_count == 1
        assert smoother.call_args_list[0][1]['alpha'] == 0.1
        assert smoother.call_args_list[0][1]['period'] == 2.2
        assert smoother.call_args_list[0][1]['primary_spans'] == (0.1, 0.8)
        assert smoother.call_args_list[0][1]['middle_span'] == 0.12
        assert smoother.call_args_list[0][1]['final_span'] == 0.15
        assert p.columns.tolist() == ['original', 'supsmu']
        assert p['original'].equals(ser)
        assert p['supsmu'].equals(-1*ser)
