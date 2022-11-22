"""Time Series features port over and adaptations of some of the functions originally in R's
TSFeatures package.

See Also:
    - TSFeatures: https://cran.r-project.org/package=tsfeatures
    - https://robjhyndman.com/papers/icdm2015.pdf
"""
from typing import Optional, Callable, Union, Tuple
from functools import partial
import warnings

import numpy as np
import pandas as pd
from scipy.signal import welch
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf, pacf, kpss, adfuller
from statsmodels.tsa.tsatools import freq_to_period

from . import _supsmu as _ss
from tslumen.profile.base import ProfilingFunction


__all__ = [
    "ft_stl",
    "ft_entropy",
    "ft_acf",
    "ft_pacf",
    "ft_tilewin",
    "ft_cross_pts",
    "ft_kpss",
    "ft_adfuller",
]


def _acf(
    fun: Callable,
    x: Union[pd.Series, np.ndarray],
    freq: int = -1,
    max_lags: Optional[int] = None,
) -> Union[pd.Series, np.ndarray]:
    max_lags = max_lags or len(x)
    nlags = min(int(10 * np.log10(len(x))), len(x) - 1)
    return fun(x, nlags=min(max(freq, nlags), max_lags))


def _spectral_entropy(ts: pd.Series, sampling_freq: float, nperseg: Optional[int]) -> float:
    nperseg = nperseg or len(ts)
    _, psd = welch(ts, fs=sampling_freq, nperseg=nperseg)
    psd_norm = np.divide(psd, psd.sum())
    spec_entropy: float = -np.multiply(psd_norm, np.log2(psd_norm)).sum()
    spec_entropy /= np.log2(psd_norm.size)
    return spec_entropy


@ProfilingFunction
def ft_stl(data: pd.Series, freq: Optional[int] = None) -> pd.Series:
    """Calculates features related to STL.

    Returns:
        pd.Series: Series with 4 values: trend, seasonality, acf1(error) and acf10(error).
    """
    if not freq:
        inferred = data.index.inferred_freq
        freq = freq_to_period(inferred) if inferred else -1

    if len(data) < 2 * freq:
        warnings.warn("Need 2 full periods of data", UserWarning)
        return pd.Series(
            {
                "trend": np.nan,
                "seasonality": np.nan,
                "acf1(error)": np.nan,
                "acf10(error)": np.nan,
            }
        )

    if freq > 1:
        seasonal = 13
        seasonal_jump = np.ceil(seasonal / 10).astype(int)
        seasonal_deg = 0
        trend = np.ceil(1.5 * freq / (1 - 1.5 / seasonal)).astype(int)
        trend += 1 if trend % 2 == 0 else 0
        trend = max(3, int(trend))
        trend_jump = np.ceil(trend / 10).astype(int)
        trend_deg = 1
        low_pass = freq + 1
        low_pass += 1 if low_pass % 2 == 0 else 0
        low_pass = max(3, int(low_pass))
        low_pass_jump = np.ceil(low_pass / 10).astype(int)
        low_pass_deg = trend_deg
        robust = False

        stl = STL(
            data.interpolate(limit_direction="both"),
            freq,
            seasonal=seasonal,
            trend=trend,
            low_pass=low_pass,
            seasonal_deg=seasonal_deg,
            trend_deg=trend_deg,
            low_pass_deg=low_pass_deg,
            robust=robust,
            seasonal_jump=seasonal_jump,
            trend_jump=trend_jump,
            low_pass_jump=low_pass_jump,
        ).fit()

        trend, season, resid = stl.trend, stl.seasonal, stl.resid
    else:
        trend = _ss.supsmu(data).supsmu
        resid = data - trend
        season = [np.nan] * len(data)

    var_resid = np.var(resid, ddof=1)
    var_deseason = np.var(resid + trend, ddof=1)
    var_detrend = np.var(resid + season, ddof=1)

    c_trend = max(0, 1 - var_resid / var_deseason)
    c_season = max(0, 1 - var_resid / var_detrend)

    nlags = min(int(10 * np.log10(len(resid))), len(resid) - 1)
    resid_acf = acf(resid, nlags=nlags, fft=True)[1:11]
    c_eacf1 = resid_acf[0]
    c_eacf10 = (resid_acf**2).sum()

    return pd.Series(
        {
            "trend": c_trend,
            "seasonality": c_season,
            "acf1(error)": c_eacf1,
            "acf10(error)": c_eacf10,
        }
    )


@ProfilingFunction
def ft_entropy(
    data: pd.Series,
    sampling_frequency: float = 1.0,
    n_per_segment: Optional[int] = None,
) -> pd.Series:
    """Calculates spectral entropy of the data and its acf function.

    See Also:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html
    """
    datac = data.fillna(method="bfill").fillna(method="ffill")
    entropy_id = _spectral_entropy(datac, sampling_frequency, n_per_segment)
    entropy_acf = _spectral_entropy(_acf(acf, datac)[1:], sampling_frequency, n_per_segment)

    return pd.Series(
        {
            "entropy": entropy_id,
            "entropy_acf": entropy_acf,
        }
    )


def _ft_acf(
    name: str,
    fun: Callable,
    data: pd.Series,
    n_diff: Tuple[int, ...],
    n_size: Tuple[int, ...],
) -> pd.Series:
    freq = freq_to_period(data.index.inferred_freq) or 1
    ret = {}
    for n_diff_ in n_diff:
        datadiff = np.diff(data.values, n=n_diff_)
        max_lags = len(datadiff) // 2 - 1 if name == "pacf" else None
        ts = _acf(fun, datadiff, freq=freq, max_lags=max_lags)
        if n_diff_ == 0:
            ret[f"{name}(season)"] = ts[freq] if len(ts) > freq else np.nan
        for n_size_ in n_size:
            ts_acf = ts[1 : 1 + n_size_]
            val = (np.square(ts_acf) if n_size_ > 1 else ts_acf).sum()
            ret[f"{name}{n_size_}(d={n_diff_})"] = val
    return pd.Series(ret)


@ProfilingFunction
def ft_acf(
    data: pd.Series,
    n_diff: Tuple[int, ...] = (0, 1, 2),
    n_size: Tuple[int, ...] = (1, 10),
) -> pd.Series:
    """ACF-related features"""
    return _ft_acf(
        "acf",
        partial(acf, fft=True),
        data.fillna(method="bfill").fillna(method="ffill"),
        n_diff,
        n_size,
    )


@ProfilingFunction
def ft_pacf(
    data: pd.Series, n_diff: Tuple[int, ...] = (0, 1, 2), n_size: Tuple[int, ...] = (5,)
) -> pd.Series:
    """PACF-related features"""
    return _ft_acf(
        "pacf",
        partial(pacf, method="ywm"),
        data.fillna(method="bfill").fillna(method="ffill"),
        n_diff,
        n_size,
    )


@ProfilingFunction
def ft_tilewin(data: pd.Series) -> pd.Series:
    """Tile window features

    Args:
        data (pd.Series): Timeseries data.

    Returns:
        pd.Series: Series with 2 values: instability and lumpiness.
    """
    freq = freq_to_period(data.index.inferred_freq)
    width = freq if freq > 1 else 10
    nobs = len(data)

    if nobs < 2 * width:
        warnings.warn("Need 2 full periods of data", UserWarning)
        instability, lumpiness = np.nan, np.nan
    else:
        datac = data.fillna(method="bfill").fillna(method="ffill")
        ts_scaled = (datac - datac.mean()) / datac.std(ddof=1)
        nsegs = nobs // width
        ts_tiled = ts_scaled.iloc[: width * nsegs].to_numpy().reshape(nsegs, width)
        ts_mean = ts_tiled.mean(axis=1)
        ts_var = ts_tiled.var(axis=1, ddof=1)
        instability = np.var(ts_mean, ddof=1)
        lumpiness = np.var(ts_var, ddof=1)

    return pd.Series({"instability": instability, "lumpiness": lumpiness})


@ProfilingFunction
def ft_cross_pts(data: pd.Series) -> pd.Series:
    """Number of times a time series crosses the median.

    Args:
        data (pd.Series): Timeseries data.

    Returns:
        pd.Series: Series with 1 value: crossing_points.
    """
    datac = data.fillna(method="bfill").fillna(method="ffill")
    pts = (datac <= np.median(datac)).astype(int).diff().abs().sum()
    return pd.Series({"crossing_points": int(pts)})


@ProfilingFunction
def ft_kpss(data: pd.Series) -> pd.Series:
    """KPSS-related features

    Args:
        data (pd.Series): Timeseries data.

    Returns:
        pd.Series: Series with 2 values: kpss(c), kpss(ct).
    """
    nlags = int(4 * (len(data) / 100) ** 0.25)
    datac = data.fillna(method="bfill").fillna(method="ffill")
    c, *_ = kpss(datac, "c", nlags=nlags)
    ct, *_ = kpss(datac, "ct", nlags=nlags)

    return pd.Series(
        {
            "kpss(c)": c,
            "kpss(ct)": ct,
        }
    )


@ProfilingFunction
def ft_adfuller(data: pd.Series) -> pd.Series:
    """ADFuller-related features

    Args:
        data (pd.Series): Timeseries data.

    Returns:
        pd.Series: Series with 4 values: adfuller(c), adfuller(ct), adfuller(ctt) and
        adfuller(nc).
    """
    data_clean = data.fillna(method="bfill").fillna(method="ffill")
    _, c, *_ = adfuller(data_clean, regression="c")
    _, ct, *_ = adfuller(data_clean, regression="ct")
    _, ctt, *_ = adfuller(data_clean, regression="ctt")
    _, nc, *_ = adfuller(data_clean, regression="nc")

    return pd.Series(
        {
            "adfuller(c)": c,
            "adfuller(ct)": ct,
            "adfuller(ctt)": ctt,
            "adfuller(nc)": nc,
        }
    )
