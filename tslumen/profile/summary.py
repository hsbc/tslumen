"""Summary indicators, both at frame and series levels."""
from typing import Any, Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.tsatools import freq_to_period

from tslumen.profile.base import ProfilingFunction, TypeSeriesFrame


__all__ = [
    "n_series",
    "length",
    "dt_start",
    "dt_end",
    "freq",
    "period",
    "sz_total",
    "df_scaled",
    "zeros",
    "missing",
    "infinite",
    "sample",
]


@ProfilingFunction
def n_series(data: pd.DataFrame) -> int:
    """
    Args:
        data (pd.DataFrame): Time series.

    Returns:
        int: Number of series in the DataFrame.
    """
    return int(data.shape[1])


@ProfilingFunction
def length(data: pd.DataFrame) -> int:
    """
    Args:
        data (pd.DataFrame): Time series.

    Returns:
        int: Length of the time series.
    """
    return int(data.shape[0])


@ProfilingFunction
def dt_start(data: pd.DataFrame) -> Any:
    """
    Args:
        data (pd.DataFrame): Time series.

    Returns:
        datetime: Start datetime.
    """
    return data.index.min().to_pydatetime()


@ProfilingFunction
def dt_end(data: pd.DataFrame) -> Any:
    """
    Args:
        data (pd.DataFrame): Time series.

    Returns:
        datetime: End datetime.
    """
    return data.index.max().to_pydatetime()


@ProfilingFunction
def freq(data: TypeSeriesFrame) -> Optional[str]:
    """
    Args:
        data (Union[pd.Series, pd.DataFrame]): Time series.

    Returns:
        int: Data's inferred frequency.
    """
    return str(data.index.sort_values().inferred_freq)


@ProfilingFunction
def period(data: TypeSeriesFrame) -> Optional[int]:
    """
    Args:
        data (Union[pd.Series, pd.DataFrame]): Time series.

    Returns:
        int: Data's periodicity.
    """
    inferred_freq = data.index.sort_values().inferred_freq
    try:
        return int(freq_to_period(inferred_freq))
    except ValueError:
        return None


@ProfilingFunction
def sz_total(data: pd.DataFrame, memory_deep: bool = True) -> int:
    """
    Args:
        data (pd.DataFrame): TimeSeries data.
        memory_deep (bool): deeper interrogation to obtain system-level memory consumption.

    Returns:
        int: Memory usage in bytes.
    """
    return int(data.memory_usage(deep=memory_deep).sum())


@ProfilingFunction
def df_scaled(data: TypeSeriesFrame) -> TypeSeriesFrame:
    """Data scaled to be between 0 and 1.

    Args:
        data (Union[pd.Series, pd.DataFrame]): Time series.

    Returns:
        Union[pd.Series, pd.DataFrame]: Scaled data.
    """
    return (data - data.min()) / (data.max() - data.min())


@ProfilingFunction
def zeros(data: pd.Series) -> int:
    """Count number of zeros.

    Args:
        data (pd.Series): Time series.

    Returns:
        int: Number of ``0`` in ``data``.
    """
    return int((data == 0).sum())


@ProfilingFunction
def missing(data: pd.Series) -> Any:
    """Count number of missing values.

    Args:
        data (pd.Series): Time series.

    Returns:
        int: Number of ``np.nan`` in ``data``.
    """
    return int(data.isna().sum())


@ProfilingFunction
def infinite(data: pd.Series) -> int:
    """Count number of infinite values.

    Args:
        data (pd.Series): Time series.

    Returns:
        int: Number of ``np.inf`` in ``data``.
    """
    return int((data == np.inf).sum())


@ProfilingFunction
def sample(data: pd.Series, sample_size: int = 10) -> pd.Series:
    """Sample N records from the data.

    Args:
        data (pd.Series): Time series.
        sample_size (int): Size of the sample.

    Returns:
        pd.Series: First and last ``sample_size/2`` records in ``data``.
    """
    size = len(data)
    sample_size = sample_size // 2
    return data.iloc[np.r_[:sample_size, size - sample_size : size]].copy()
