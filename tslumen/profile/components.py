"""Functions for decomposing the time series in trend/seasonality/residual."""
from typing import Optional

import pandas as pd
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.tsatools import freq_to_period

from tslumen.profile.base import ProfilingFunction


__all__ = ["stl", "seasonal_split"]


@ProfilingFunction
def stl(
    data: pd.Series,
    period: Optional[int] = None,
    seasonal: int = 7,
    trend: Optional[int] = None,
    low_pass: Optional[int] = None,
    seasonal_deg: Optional[int] = 0,
    trend_deg: Optional[int] = 0,
    low_pass_deg: Optional[int] = 0,
    robust: bool = False,
    seasonal_jump: int = 1,
    trend_jump: int = 1,
    low_pass_jump: int = 1,
) -> pd.DataFrame:
    """Season-Trend decomposition using LOESS.

    Returns:
        pd.DataFrame: DataFrame with 3 columns: trend, seasonality and residual.

    See Also:
        statsmodels STL:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html
    """
    period_ = period or freq_to_period(data.index.inferred_freq)
    if period_ < 2:
        return pd.DataFrame()
    res = STL(
        data.fillna(method="bfill").fillna(method="ffill"),
        period=period,
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
    return pd.DataFrame({"trend": res.trend, "seasonality": res.seasonal, "residual": res.resid})


@ProfilingFunction
def seasonal_split(data: pd.Series) -> pd.DataFrame:
    """
    Splits the data by season:
        * Quarterly - Years by Quarters
        * Monthly - Years by Months
        * Weekly - Years by Weeks
        * Daily - Year+Months by Days
        * Business daily - Week by Day of the Week
        * Hourly - Year+Month+Day by Hours

    Args:
        data (pd.Series): Time series split.

    Returns:
        pd.DataFrame: Seasonally split data.

    """
    freq_by = {
        "Q": ("%Y", "%m"),
        "M": ("%Y", "%m"),
        "W": ("%G", "W%V"),
        "D": ("%Y-%m", "%d"),
        "B": ("%G-%V", "%w-%a"),
        "H": ("%Y-%m-%d", "%H"),
    }
    freq = data.index.inferred_freq
    freq = freq[0] if freq else ""
    if freq in freq_by:
        fmt_season, fmt_freq = freq_by[freq]

        return (
            pd.DataFrame(
                {
                    "season": data.index.strftime(fmt_season),
                    "freq": data.index.strftime(fmt_freq),
                    "value": data.values,
                }
            )
            .set_index(["season", "freq"])
            .unstack(0)
            .droplevel(0, axis=1)
        )
    return pd.DataFrame()
