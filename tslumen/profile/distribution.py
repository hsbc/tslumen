"""Distribution functions."""
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import iqr
from statsmodels.api import ProbPlot

from tslumen.profile.base import ProfilingFunction


__all__ = [
    "binned",
    "pd_quantiles",
    "pd_percentiles",
]


@ProfilingFunction
def binned(data: pd.Series, nbins: Optional[int] = None) -> pd.Series:
    """Bins the data in ``nbins`` bins.

    Args:
        data (pd.Series): Timeseries to bin.
        nbins (Optional[int]): Number of bins, if not provided uses the Freedman-Diaconis rule to
            calculate the number of bins: bw=2×IQR×n^{−1/3}; n_bins=(max−min)/bw

    Returns:
        pd.Series: Series with the counts, indexed by bins.
    """
    data = data.copy().dropna()
    if not nbins:
        # Freedman-Diaconis rule: bin-width is set to bw=2×IQR×n^{−1/3}; n_bins=(max−min)/bw
        bw = 2 * iqr(data) * len(data) ** (-1 / 3)
        nbins = round((max(data) - min(data)) / bw)
    counts, bins = np.histogram(data.values, nbins)
    return pd.Series(counts, index=bins[:-1])


@ProfilingFunction
def pd_quantiles(data: pd.Series) -> pd.DataFrame:
    """Calculates quantiles -- supporting data for a QQ-plot.

    Args:
        data (pd.Series): Timeseries data.

    Returns:
        pd.DataFrame: DataFrame with 3 columns, theoretical_quantiles, sample_quantiles and
        reference
    """
    probp = ProbPlot(data.dropna())
    x = probp.theoretical_quantiles
    y = probp.sample_quantiles
    m, b = y.std(), y.mean()
    ref_line = x * m + b
    return pd.DataFrame({"theoretical_quantiles": x, "sample_quantiles": y, "reference": ref_line})


@ProfilingFunction
def pd_percentiles(data: pd.Series) -> pd.DataFrame:
    """Calculates percentiles -- supporting data for a PP-plot.

    Args:
        data (pd.Series): Timeseries to data.

    Returns:
        pd.DataFrame: DataFrame with 3 columns, theoretical_percentiles, sample_percentiles and
        reference
    """
    probp = ProbPlot(data.dropna())
    x = probp.theoretical_percentiles
    y = probp.sample_percentiles
    m, b = y.std(), y.mean()
    ref_line = x * m + b
    return pd.DataFrame(
        {"theoretical_percentiles": x, "sample_percentiles": y, "reference": ref_line}
    )
