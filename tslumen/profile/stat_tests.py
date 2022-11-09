"""Statistical tests."""
from typing import Dict, Any, Optional
from dataclasses import dataclass
import math
import warnings

import numpy as np
import pandas as pd
import scipy
import statsmodels.stats.api as sms
from statsmodels.tsa.tsatools import freq_to_period
from statsmodels.tsa.stattools import acf, adfuller, kpss

from tslumen.profile.base import ProfilingFunction, _DCDict
from tslumen.misc import repr_html


__all__ = [
    "TestResult",
    "levene_constant_variance",
    "ljungbox_autocorrelation",
    "jarque_bera_normality",
    "omnibus_normality",
    "adfuller_stationarity",
    "kpss_stationarity",
]


@repr_html
@dataclass
class TestResult(_DCDict):
    test: str
    p_value: float
    confidence_level: float
    null_hypothesis: str
    reject_null_hypothesis: bool
    details: Optional[Dict[str, Any]]


@ProfilingFunction
def levene_constant_variance(data: pd.Series, confidence_level: float = 0.05) -> TestResult:
    """Levene test for constant variances, tests the null hypothesis that all input samples are
    from populations with equal variances.

    Args:
        data (pd.Series): Time series.
        confidence_level (float): Confidence level for rejecting the null hypothesis.

    Returns:
        TestResult: test name, p-value, null hypothesis, reject?, confidence level and details.

    See Also:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html
    """
    ser_clean = data
    if np.isnan(data).any():
        ser_clean = data.fillna(method="bfill").fillna(method="ffill")
        warnings.warn("Found and removed N/A values.", UserWarning)

    try:
        freq = freq_to_period(data.index.inferred_freq)
        width = freq if freq > 1 else 10
        n_segs = len(data) // width
    except (ValueError, AttributeError):
        n_segs = 2
        width = len(data) // n_segs

    sample_groups = ser_clean.values[: n_segs * width].reshape(n_segs, width)
    t_statistic, p_value = scipy.stats.levene(*sample_groups)
    initial_hypothesis = f"Variance is constant between {n_segs} groups"
    outcome_specifics = {"t_statistic": float(t_statistic)}
    reject_h0 = bool(p_value < confidence_level)
    result = TestResult(
        test="Levene",
        p_value=float(p_value),
        null_hypothesis=initial_hypothesis,
        reject_null_hypothesis=reject_h0,
        details=outcome_specifics,
        confidence_level=confidence_level,
    )

    return result


@ProfilingFunction
def ljungbox_autocorrelation(
    data: pd.Series, n_lags: Optional[int] = None, confidence_level: float = 0.05
) -> TestResult:
    """Null hypothesis - no auto correlation amounts specified lags.

    Args:
        data (pd.Series): Time series.
        n_lags (int): Number of lags, if not supplied calculated as ``10*log(data.length)``.
        confidence_level (float): Confidence level for rejecting the null hypothesis.

    Returns:
        TestResult: test name, p-value, null hypothesis, reject?, confidence level and details.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
    """
    ser_clean = data
    if np.isnan(data).any():
        ser_clean = data.dropna()
        warnings.warn("Found and removed N/A values.", UserWarning)

    if not n_lags:
        n_lags = math.ceil(math.log(len(ser_clean), 10) * 10)
        # n_lags needs to be less than array"s len -> edge case, small arrays
        n_lags = min(n_lags, len(ser_clean) - 1)

    acf_result, confidence_interval, q_stat, p_value = acf(
        ser_clean, nlags=n_lags, fft=False, qstat=True, alpha=confidence_level
    )
    outcome_specifics = {
        "acf": acf_result.tolist(),
        "confidence_interval": confidence_interval.tolist(),
        "q_stat": q_stat.tolist(),
        "p_values": p_value.tolist(),
    }
    reject_h0 = bool(min(p_value) < confidence_level)
    result = TestResult(
        test="Ljung-Box",
        p_value=min(p_value),
        null_hypothesis=f"No autocorrelation among specified lag({n_lags})",
        reject_null_hypothesis=reject_h0,
        details=outcome_specifics,
        confidence_level=confidence_level,
    )

    return result


@ProfilingFunction
def jarque_bera_normality(data: pd.Series, confidence_level: float = 0.05) -> TestResult:
    """The Jarque-Bera test statistic tests the null hypothesis that the data is normally
    distributed against an alternative that the data follow some other distribution.

    Args:
        data (pd.Series): Time series.
        confidence_level (float): Confidence level for rejecting the null hypothesis.

    Returns:
        TestResult: test name, p-value, null hypothesis, reject?, confidence level and details.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.stats.stattools.jarque_bera.html
    """
    ser_clean = data
    if np.isnan(data).any():
        ser_clean = data.dropna()
        warnings.warn("Found and removed N/A values.", UserWarning)

    jarque_bera_test_statistic, p_value, skew, kurtosis = sms.jarque_bera(ser_clean)
    outcome_specifics = {
        "jarque_bera_test_statistic": float(jarque_bera_test_statistic),
        "skew": float(skew),
        "kurtosis": float(kurtosis),
    }
    reject_h0 = bool(p_value < confidence_level)
    result = TestResult(
        test="Jarque Bera",
        p_value=p_value,
        confidence_level=confidence_level,
        null_hypothesis="Data is normally distributed",
        reject_null_hypothesis=reject_h0,
        details=outcome_specifics,
    )

    return result


@ProfilingFunction
def omnibus_normality(data: pd.Series, confidence_level: float = 0.05) -> TestResult:
    """Omnibus test for normality, null hypothesis: data is normally distributed.

    Args:
        data (pd.Series): Time series.
        confidence_level (float): Confidence level for rejecting the null hypothesis.

    Returns:
        TestResult: test name, p-value, null hypothesis, reject?, confidence level and details.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.stats.stattools.omni_normtest.html
    """
    ser_clean = data
    if np.isnan(data).any():
        ser_clean = data.dropna()
        warnings.warn("Found and removed N/A values.", UserWarning)

    k_2, p_value = sms.omni_normtest(ser_clean)
    outcome_specifics = {"k2": float(k_2)}
    reject_h0 = bool(p_value < confidence_level)
    result = TestResult(
        test="Omnibus",
        p_value=float(p_value),
        confidence_level=confidence_level,
        null_hypothesis="Data is normally distributed",
        reject_null_hypothesis=reject_h0,
        details=outcome_specifics,
    )

    return result


@ProfilingFunction
def adfuller_stationarity(data: pd.Series, confidence_level: float = 0.05) -> TestResult:
    """Augmented Dickey-Fuller unit root test, can be used to test for a unit root in a univariate
    process in the presence of serial correlation.

    Args:
        data (pd.Series): Time series.
        confidence_level (float): Confidence level for rejecting the null hypothesis.

    Returns:
        TestResult: test name, p-value, null hypothesis, reject?, confidence level and details.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html
    """
    ser_clean = data
    if np.isnan(data).any():
        ser_clean = data.dropna()
        warnings.warn("Found and removed N/A values.", UserWarning)

    if len(ser_clean) < 6:
        warnings.warn("Sample size is too short", UserWarning)
        test_statistic, p_value, n_lags, n_obs, crit = np.nan, np.nan, None, None, None
    else:
        test_statistic, p_value, n_lags, n_obs, crit, *_ = adfuller(ser_clean, autolag="AIC")

    outcome_specifics = {
        "test_statistic": test_statistic,
        "n_lags": n_lags,
        "n_obs": n_obs,
        "critical_values": crit,
    }
    reject_h0 = bool(p_value < confidence_level)
    result = TestResult(
        test="Augmented Dickey-Fuller",
        p_value=float(p_value),
        confidence_level=confidence_level,
        null_hypothesis="Data has unit root",
        reject_null_hypothesis=reject_h0,
        details=outcome_specifics,
    )

    return result


@ProfilingFunction
def kpss_stationarity(data: pd.Series, confidence_level: float = 0.05) -> TestResult:
    """Kwiatkowski-Phillips-Schmidt-Shin test for the null hypothesis that the data is level or
    trend stationary.

    Args:
        data (pd.Series): Time series.
        confidence_level (float): Confidence level for rejecting the null hypothesis.

    Returns:
        TestResult: test name, p-value, null hypothesis, reject?, confidence level and details.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.kpss.html
    """
    ser_clean = data
    if np.isnan(data).any():
        ser_clean = data.dropna()
        warnings.warn("Found and removed N/A values.", UserWarning)

    try:
        test_statistic, p_value, n_lags, crit, *_ = kpss(ser_clean, nlags="auto")
    except (ValueError, OverflowError) as e:
        test_statistic, p_value, n_lags, crit = np.nan, np.nan, None, None
        warnings.warn(str(e), UserWarning)

    outcome_specifics = {
        "test_statistic": test_statistic,
        "n_lags": n_lags,
        "critical_values": crit,
    }
    reject_h0 = bool(p_value < confidence_level)
    result = TestResult(
        test="Kwiatkowski-Phillips-Schmidt-Shin",
        p_value=float(p_value),
        confidence_level=confidence_level,
        null_hypothesis="Data is level stationary",
        reject_null_hypothesis=reject_h0,
        details=outcome_specifics,
    )

    return result
