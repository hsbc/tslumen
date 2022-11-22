import pytest
from tests.unit.profile.base import *

from tslumen.profile.features import (
    ft_stl, ft_entropy, ft_acf, ft_pacf, ft_tilewin, ft_cross_pts, ft_kpss, ft_adfuller
)


@pytest.mark.parametrize(
    "fn",
    (ft_stl, ft_entropy, ft_acf, ft_pacf, ft_tilewin, ft_cross_pts, ft_kpss, ft_adfuller)
)
def test_stat_tests_profiler(fn):
    check_profiler(fn)


def poke(ser, per=0.05):
    s = ser.copy()
    for _ in range(int(per * len(ser))):
        s.iloc[np.random.randint(len(ser))] = np.nan
    return s


@pytest.mark.parametrize(
    "ser",
    [
        mkser(20, ff='M'),
        mkser(120, ff='Y'),
        mkser(120, ff='Q'),
        mkser(120, ff='M'),
        mkser(120, ff='W'),
        mkser(120, ff='D'),
        mkser(120, ff='B'),
        mkser(120, ff='H'),
        poke(mkser(120, ff='Y')),
        poke(mkser(120, ff='Q')),
        poke(mkser(120, ff='M')),
        poke(mkser(120, ff='W')),
        poke(mkser(120, ff='D')),
        poke(mkser(120, ff='B')),
        poke(mkser(120, ff='H')),
    ]
)
def test_tsfeatures(ser):
    fts = [
        fn(ser)
        for fn in (ft_stl, ft_entropy, ft_acf, ft_pacf, ft_tilewin, ft_cross_pts, ft_kpss, ft_adfuller)
    ]
    for f in fts:
        assert bool(f)
    df = pd.concat([f.result for f in fts])
    assert df.shape == (26,)
    assert df.index.tolist() == [
        'trend', 'seasonality', 'acf1(error)', 'acf10(error)', 'entropy', 'entropy_acf',
        'acf(season)', 'acf1(d=0)', 'acf10(d=0)', 'acf1(d=1)', 'acf10(d=1)', 'acf1(d=2)',
        'acf10(d=2)', 'pacf(season)', 'pacf5(d=0)', 'pacf5(d=1)', 'pacf5(d=2)', 'instability',
        'lumpiness', 'crossing_points', 'kpss(c)', 'kpss(ct)', 'adfuller(c)', 'adfuller(ct)',
        'adfuller(ctt)', 'adfuller(nc)'
    ]
