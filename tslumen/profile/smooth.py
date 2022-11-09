"""Data smoothing functions."""
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.nonparametric import smoothers_lowess

from . import _supsmu as _ss
from tslumen.profile.base import ProfilingFunction

__all__ = [
    "lowess",
    "rolling_avg",
    "supsmu",
]


@ProfilingFunction
def lowess(
    data: pd.Series,
    fracs: Tuple[float, ...] = (0.05, 0.1, 0.15),
    it: int = 3,
    delta: float = 0.0,
    missing: str = "drop",
) -> pd.DataFrame:
    """Locally Weighted Scatterplot Smoothing

    Args:
        data (pd.Series): Time series.
        fracs (Tuple[float, ...]): Fraction of data to use when estimating each y-value.
        it (int): number of residual-based reweightings to perform.
        delta (float): Distance within which to use linear interpolation instead of weighted
            regression.
        missing (str): Approach to deal with missing values -- 'none', 'drop', or 'raise'.

    Returns:
        pd.DataFrame: DataFrame with original series (labelled 'original') and N smoothed series,
        as dictated by the parameter ``fracs``, each series labelled as `lowess <frac>%`.

    See Also:
        https://www.statsmodels.org/stable/statsmodels.nonparametric.smoothers_lowess.lowess.html
    """
    return pd.concat(
        [data.rename("original")]
        + [
            pd.Series(
                smoothers_lowess.lowess(
                    data,
                    np.arange(len(data)),
                    frac=f,
                    it=it,
                    delta=delta,
                    missing=missing,
                    is_sorted=True,
                )[:, 1],
                index=(data.dropna() if missing == "drop" else data).index,
                name=f"lowess {int(f*100):2d}%",
            )
            for f in fracs
        ],
        axis=1,
    )


@ProfilingFunction
def rolling_avg(
    data: pd.Series, wins: Optional[Tuple[int, ...]] = tuple(), max_win_frac: int = 10
) -> pd.DataFrame:
    """Rolling average.

    Args:
        data (pd.Series): Time series.
        wins (Tuple[int, ...]): Size of the rolling windows -- determined based on frequency if not
            provided.
        max_win_frac (int): Forces window size to be no bigger than ``data.length/max_win_frac``.

    Returns:
        pd.DataFrame: DataFrame with original series (labelled 'original') and N smoothed series,
        as dictated by the parameter ``wins``, each series labelled as `rolling <win><freq>`.
    """
    freq = data.index.inferred_freq
    freq = freq[0] if freq else ""
    if not wins:
        max_win = len(data) // max_win_frac
        wins_dic = {
            "A": (3, 4, 5),
            "Q": (2, 4, 8),
            "M": (3, 6, 12),
            "W": (4, 8, 12),
            "D": (7, 14, 30, 90),
            "B": (5, 10, 20, 60),
            "H": (12, 24, 7 * 24, 30 * 24),
        }
        wins = wins_dic.get(freq, (max_win // 4, max_win // 2, max_win)) or tuple()
        wins = tuple(w for w in wins if w <= max_win)
    datac = data.fillna(method="bfill").fillna(method="ffill")
    return pd.concat(
        [data.rename("original")]
        + [datac.rolling(w).mean().rename(f"rolling {w}{freq}") for w in wins],
        axis=1,
    )


@ProfilingFunction
def supsmu(
    data: pd.Series,
    alpha: Optional[float] = None,
    period: Optional[float] = None,
    primary_spans: Tuple[float, ...] = (0.05, 0.2, 0.5),
    middle_span: float = 0.2,
    final_span: float = 0.05,
) -> pd.DataFrame:
    """SuperSmoother for nonparametric smoothing of scatter plots.

    Args:
        data (pd.Series): Time series.
        alpha (float): Bass enhancement / smoothing level (0 < alpha < 10).
        period (float): Data periodicity.
        primary_spans (Tuple[float]): Primary span values used for the smooth (between 0 and 1).
        middle_span (float): Middle span value.
        final_span (float): Final span value.

    Returns:
        pd.DataFrame: DataFrame with original and smooth series, labelled 'original' and 'supsmu'
        respectively.

    See Also:
        http://doi.org/10.5281/zenodo.14475
    """
    return _ss.supsmu(
        data=data,
        alpha=alpha,
        period=period,
        primary_spans=primary_spans,
        middle_span=middle_span,
        final_span=final_span,
    )
