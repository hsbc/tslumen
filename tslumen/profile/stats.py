"""Descriptive statistics."""
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from tslumen.profile.base import ProfilingFunction


__all__ = [
    "mean",
    "var",
    "std",
    "median",
    "mad",
    "cov",
    "minimum",
    "maximum",
    "q25",
    "q50",
    "q75",
    "iqr",
    "kurtosis",
    "skew",
]


@ProfilingFunction
def mean(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Arithmetic mean of ``data``.
    """
    return float(np.mean(data))


@ProfilingFunction
def var(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Variance of ``data``.
    """
    return float(np.var(data))


@ProfilingFunction
def std(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Standard deviation of ``data``.
    """
    return float(np.std(data))


@ProfilingFunction
def median(data: pd.Series) -> Any:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Median of ``data``.
    """
    data_ = data.dropna()
    if len(data_) == 0:
        return np.nan
    return float(np.median(data_))


@ProfilingFunction
def mad(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Median absolute deviation of ``data``.
    """
    return float(stats.median_abs_deviation(data.dropna()))


@ProfilingFunction
def cov(data: pd.Series) -> Any:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Coefficient of variation of ``data``.

    See Also:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.variation.html
    """
    data_ = data.dropna()
    if len(data_) == 0:
        return np.nan
    return float(stats.variation(data_))


@ProfilingFunction
def minimum(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Minimum value in ``data``.
    """
    return float(np.min(data))


@ProfilingFunction
def maximum(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Maximum value in ``data``.
    """
    return float(np.max(data))


@ProfilingFunction
def q25(data: pd.Series) -> Any:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Quantile 0.25 of ``data``.
    """
    data_ = data.dropna()
    if len(data_) == 0:
        return np.nan
    return float(np.quantile(data_, q=0.25))


@ProfilingFunction
def q50(data: pd.Series) -> Any:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Quantile 0.5 of ``data``.
    """
    data_ = data.dropna()
    if len(data_) == 0:
        return np.nan
    return float(np.quantile(data_, q=0.5))


@ProfilingFunction
def q75(data: pd.Series) -> Any:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Quantile 0.75 of ``data``.
    """
    data_ = data.dropna()
    if len(data_) == 0:
        return np.nan
    return float(np.quantile(data_, q=0.75))


@ProfilingFunction
def iqr(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Interquartile range of ``data``.

    See Also:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.iqr.html
    """
    return float(stats.iqr(data.dropna()))


@ProfilingFunction
def kurtosis(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Kurtosis of ``data``.

    See Also:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kurtosis.html
    """
    return float(stats.kurtosis(data.dropna()))


@ProfilingFunction
def skew(data: pd.Series) -> float:
    """
    Args:
        data (pd.Series): Time series.

    Returns:
        float: Sample skewness of ``data``.

    See Also:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html
    """
    return float(stats.skew(data.dropna()))
