import pytest
from tests.unit.profile.base import *

from tslumen.profile.stat_tests import (
    TestResult as _TestResult,
    levene_constant_variance, ljungbox_autocorrelation, jarque_bera_normality, omnibus_normality,
    adfuller_stationarity, kpss_stationarity
)


@pytest.mark.parametrize(
    "fn",
    (levene_constant_variance, ljungbox_autocorrelation, jarque_bera_normality, omnibus_normality,
     adfuller_stationarity, kpss_stationarity)
)
def test_stat_tests_profiler(fn):
    check_profiler(fn)


# Levene constant variance
# -------------------------------------------------------------------------------------------------

# Very Low variation within each group and Very high variation between groups
# makes not only constant variance Hypothesis to Fail but also p_value under 0.001
s_lev01 = pd.Series([1, 1.2, 1.3, 1.4, 1.5, 1.6, 1, 1.2, 1.3, 1.4, 1.5, 1.6,
                     100000000000000000000.1, 100000000000000000000.2,
                     100000000000000000000.3, 100000000000000000000.4,
                     100000000000000000000.5, 100000000000000000000.6,
                     100000000000000000000.1, 100000000000000000000.2,
                     100000000000000000000.3, 100000000000000000000.4,
                     100000000000000000000.5, 100000000000000000000.6],
                    index=pd.date_range('2010-01-01', periods=24, freq='M'))
r_lev01 = _TestResult(test="Levene", p_value=0.001, reject_null_hypothesis=True,
                      confidence_level=0.05, null_hypothesis='', details=None)

# Low variation within each group and NO variation between them
# makes constant variance Hypothesis to be True and p-value = 1.0
s_lev02 = pd.Series([1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3,
                     1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
                    index=pd.date_range('2010-01-01', periods=24, freq='M'))
r_lev02 = _TestResult(test="Levene", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)

s_lev03 = pd.Series([np.nan, 2, 3, 1, 2, np.nan, 1, 2, 3, 1, 2, 3,
                     1, 2, 3, 1, 2, 3, 1, 2, 3, 1, np.nan, np.nan],
                    index=pd.date_range('2010-01-01', periods=24, freq='SM'))
r_lev03 = _TestResult(test="Levene", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)

ts_levene = [
    (levene_constant_variance, (ser,), res)
    for ser, res in zip([s_lev01, s_lev02, s_lev03],
                        [r_lev01, r_lev02, r_lev03])
]


# Ljung-Box AutoCorrelation
# -------------------------------------------------------------------------------------------------
s_ljb01 = pd.Series([-1, -3, -1, 6, -2, 1, 2, 6, 0, 3, 2, 6])
s_ljb02 = pd.Series([0, -1.4428, -0.6344, -2.3231, 0.2858, -4.1757, 1.1735, -2.9105, 2.3725, -3.8455, 2.4451])
s_ljb03 = pd.Series([16272.01, np.nan, 16776.43, 16790.19, 17581.43, 17663.54])
s_ljb04 = pd.Series([1, 2])
s_ljb05 = pd.Series([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

r_ljb01 = _TestResult(test="Ljung-Box", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_ljb02 = _TestResult(test="Ljung-Box", p_value=1, reject_null_hypothesis=True,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_ljb03 = _TestResult(test="Ljung-Box", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_ljb04 = _TestResult(test="Ljung-Box", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_ljb05 = _TestResult(test="Ljung-Box", p_value=np.nan, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
ts_ljb_ac = [
    (ljungbox_autocorrelation, (ser,), res)
    for ser, res in zip([s_ljb01, s_ljb02, s_ljb03, s_ljb04, s_ljb05],
                        [r_ljb01, r_ljb02, r_ljb03, r_ljb04, r_ljb05])
]


# Jarque Bera Normality
# -------------------------------------------------------------------------------------------------
s_jbn01 = pd.Series([-1.7498, 0.3427, 1.1530, -0.2524, 0.9813, 0.5142, 0.2212, -1.0700, -0.1895, 0.2550, -0.4580,
                     0.4352, -0.5836, 0.8168, 0.6727])
s_jbn02 = pd.Series([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096, 8192, 16384, 32768, 65536])
s_jbn03 = pd.Series([16272.01, np.nan, 16776.43, 16790.19, 17581.43, 17663.54])
s_jbn04 = pd.Series([1, 2])

r_jbn01 = _TestResult(test="Jarque Bera", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_jbn02 = _TestResult(test="Jarque Bera", p_value=1, reject_null_hypothesis=True,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_jbn03 = _TestResult(test="Jarque Bera", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_jbn04 = _TestResult(test="Jarque Bera", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
ts_jbn = [
    (jarque_bera_normality, (ser,), res)
    for ser, res in zip([s_jbn01, s_jbn02, s_jbn03, s_jbn04],
                        [r_jbn01, r_jbn02, r_jbn03, r_jbn04])
]


# Omnibus Normality
# -------------------------------------------------------------------------------------------------
s_omn01 = pd.Series([-1.7498, 0.3427, 1.1530, -0.2524, 0.9813, 0.5142, 0.2212, -1.0700, -0.1895,
                     0.2550, -0.4580, 0.4352, -0.5836, 0.8168, 0.6727,
                     -1.7498, 0.3427, 1.1530, -0.2524, 0.9813, 0.5142, 0.2212, -1.0700, -0.1895,
                     0.2550, -0.4580, 0.4352, -0.5836, 0.8168, 0.6727])
s_omn02 = pd.Series([2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096, 8192, 16384, 32768, 65536])
s_omn03 = pd.Series([16272.01, np.nan, 16776.43, 16790.19, 17581.43, 17663.54])
s_omn04 = pd.Series([1, 2])

r_omn01 = _TestResult(test="Omnibus", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_omn02 = _TestResult(test="Omnibus", p_value=1, reject_null_hypothesis=True,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_omn03 = _TestResult(test="Omnibus", p_value=np.nan, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_omn04 = _TestResult(test="Omnibus", p_value=np.nan, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
ts_omn = [
    (omnibus_normality, (ser,), res)
    for ser, res in zip([s_omn01, s_omn02, s_omn03, s_omn04],
                        [r_omn01, r_omn02, r_omn03, r_omn04])
]


# Augmented Dickey-Fuller Stationarity
# -------------------------------------------------------------------------------------------------
s_adf01 = pd.Series([20.0, 20.497, 20.358, 21.006, 22.529, 22.295, 22.061,
                     23.64, 24.408, 23.938, 24.481, 24.017, 23.551, 23.793,
                     21.88, 20.155, 19.593, 18.58, 18.894, 17.986, 16.574,
                     18.04, 17.814, 17.881, 16.457, 15.912, 16.023, 14.872,
                     15.248, 14.647, 14.356, 13.754, 15.606, 15.593, 14.535,
                     15.358, 14.137, 14.346, 12.386, 11.058, 11.255, 11.993,
                     12.164, 12.049, 11.748, 10.269, 9.549, 9.089, 10.146,
                     10.489, 8.726, 9.05, 8.665, 7.988, 8.6, 9.631, 10.562,
                     9.723, 9.414, 9.745, 10.721, 10.242, 10.056, 8.95, 7.753,
                     8.566, 9.922, 9.85, 10.854, 11.215, 10.57, 10.932])  # random walk
s_adf02 = pd.Series([3.353, 0.654, -0.438, 1.659, -4.422, 0.471, 1.542, -2.957, 2.288,
                     0.677, -0.831, 1.266, 4.541, 0.364, 0.496, -0.919, -1.7, 1.661,
                     -1.712, 0.143, -0.955, 0.958, 0.667, 2.075, -1.02, -0.54, -1.958,
                     -0.889, 0.755, 1.514, -1.844, 1.739, 2.711, 0.827, 3.754, -1.548])  # normal
s_adf03 = pd.Series([16272.01, np.nan, 16776.43, 16790.19, 17581.43, 17663.54, 234.234, 18920.33])
s_adf04 = pd.Series([1, 2])
s_adf05 = pd.Series([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
r_adf01 = _TestResult(test="Augmented Dickey-Fuller", p_value=0.8, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_adf02 = _TestResult(test="Augmented Dickey-Fuller", p_value=0.5, reject_null_hypothesis=True,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_adf03 = _TestResult(test="Augmented Dickey-Fuller", p_value=1, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_adf04 = _TestResult(test="Augmented Dickey-Fuller", p_value=np.nan, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
r_adf05 = _TestResult(test="Augmented Dickey-Fuller", p_value=np.nan, reject_null_hypothesis=False,
                      confidence_level=0.05, null_hypothesis='', details=None)
ts_adf = [
    (adfuller_stationarity, (ser,), res)
    for ser, res in zip([s_adf01, s_adf02, s_adf03, s_adf04, s_adf05],
                        [r_adf01, r_adf02, r_adf03, r_adf04, r_adf05])
]


# Kwiatkowski-Phillips-Schmidt-Shin Stationarity
# -------------------------------------------------------------------------------------------------
s_kpss01 = pd.Series([20.0, 20.497, 20.358, 21.006, 22.529, 22.295, 22.061,
                      23.64, 24.408, 23.938, 24.481, 24.017, 23.551, 23.793,
                      21.88, 20.155, 19.593, 18.58, 18.894, 17.986, 16.574,
                      18.04, 17.814, 17.881, 16.457, 15.912, 16.023, 14.872,
                      15.248, 14.647, 14.356, 13.754, 15.606, 15.593, 14.535,
                      15.358, 14.137, 14.346, 12.386, 11.058, 11.255, 11.993,
                      12.164, 12.049, 11.748, 10.269, 9.549, 9.089, 10.146,
                      10.489, 8.726, 9.05, 8.665, 7.988, 8.6, 9.631, 10.562,
                      9.723, 9.414, 9.745, 10.721, 10.242, 10.056, 8.95, 7.753,
                      8.566, 9.922, 9.85, 10.854, 11.215, 10.57, 10.932])  # random walk
s_kpss02 = pd.Series([3.353, 0.654, -0.438, 1.659, -4.422, 0.471, 1.542, -2.957, 2.288,
                      0.677, -0.831, 1.266, 4.541, 0.364, 0.496, -0.919, -1.7, 1.661,
                      -1.712, 0.143, -0.955, 0.958, 0.667, 2.075, -1.02, -0.54, -1.958,
                      -0.889, 0.755, 1.514, -1.844, 1.739, 2.711, 0.827, 3.754, -1.548])  # normal
s_kpss03 = pd.Series([16272.01, np.nan, 16776.43, 16790.19, 17581.43, 17663.54, 234.234, 18920.33])
s_kpss04 = pd.Series([1, 2])
s_kpss05 = pd.Series([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
r_kpss01 = _TestResult(test="Kwiatkowski-Phillips-Schmidt-Shin", p_value=0.8, reject_null_hypothesis=True,
                       confidence_level=0.05, null_hypothesis='', details=None)
r_kpss02 = _TestResult(test="Kwiatkowski-Phillips-Schmidt-Shin", p_value=0.5, reject_null_hypothesis=False,
                       confidence_level=0.05, null_hypothesis='', details=None)
r_kpss03 = _TestResult(test="Kwiatkowski-Phillips-Schmidt-Shin", p_value=1, reject_null_hypothesis=False,
                       confidence_level=0.05, null_hypothesis='', details=None)
r_kpss04 = _TestResult(test="Kwiatkowski-Phillips-Schmidt-Shin", p_value=np.nan, reject_null_hypothesis=False,
                       confidence_level=0.05, null_hypothesis='', details=None)
r_kpss05 = _TestResult(test="Kwiatkowski-Phillips-Schmidt-Shin", p_value=np.nan, reject_null_hypothesis=False,
                       confidence_level=0.05, null_hypothesis='', details=None)
ts_kpss = [
    (kpss_stationarity, (ser,), res)
    for ser, res in zip([s_kpss01, s_kpss02, s_kpss03, s_kpss04, s_kpss05],
                        [r_kpss01, r_kpss02, r_kpss03, r_kpss04, r_kpss05])
]


@pytest.mark.parametrize(
    "fn,args,out",
    [
        *ts_levene,
        *ts_ljb_ac,
        *ts_jbn,
        *ts_omn,
        *ts_adf,
        *ts_kpss
    ]
)
def test_stat_tests_exec(fn, args, out):
    def _cmp_statt(actual, expected):
        assert actual.test == expected.test, "Test name differs"
        assert actual.reject_null_hypothesis == expected.reject_null_hypothesis, "Reject null differs"
        assert (actual.p_value != actual.p_value and expected.p_value != expected.p_value) or \
               (actual.p_value <= expected.p_value), "Larger p-value than expected"

    return check_profile_exec(fn, args, out, comparer=_cmp_statt)
