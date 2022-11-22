"""Auto/correlation functions, including Spearman, ACF, PACF, etc."""
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa import stattools as sms

from tslumen.profile.base import ProfilingFunction


__all__ = [
    "acf",
    "acf_1d",
    "acf_2d",
    "pacf",
    "pacf_1d",
    "pacf_2d",
    "lag_corr",
    "corr_pearson",
    "corr_kendall",
    "corr_spearman",
    "granger_causality",
]


def _stattools_make_df(corr: np.ndarray, conf: np.ndarray) -> pd.DataFrame:
    df_corr = pd.DataFrame(
        {
            "lag": np.arange(len(corr)),
            "correlation": corr,
            "low": conf[:, 0] - corr,
            "up": conf[:, 1] - corr,
        }
    )
    df_corr.loc[0, ["low", "up"]] = np.nan
    return df_corr


def _acf(
    data: pd.Series,
    diff: int = 0,
    lags: int = 40,
    adjusted: bool = False,
    fft: bool = False,
    alpha: float = 0.05,
    missing: str = "none",
) -> pd.DataFrame:
    data_clean = data.fillna(method="bfill").fillna(method="ffill")
    lags = min(lags, len(data_clean) // 2, len(data_clean))
    data_clean = pd.Series(np.diff(data_clean.values, diff), index=data_clean.index[diff:])
    corr, conf = sms.acf(
        data_clean,
        nlags=lags,
        adjusted=adjusted,
        qstat=False,
        fft=fft,
        alpha=alpha,
        missing=missing,
    )
    return _stattools_make_df(corr, conf)


def _pacf(
    data: pd.Series,
    diff: int = 0,
    lags: int = 40,
    method: str = "ywadjusted",
    alpha: float = 0.05,
) -> pd.DataFrame:
    data_clean = data.fillna(method="bfill").fillna(method="ffill")
    lags = min(lags, np.floor(len(data_clean) / 2) - 2, len(data_clean))
    data_clean = pd.Series(np.diff(data_clean.values, diff), index=data_clean.index[diff:])
    corr, conf = sms.pacf(data_clean, nlags=lags, method=method, alpha=alpha)
    return _stattools_make_df(corr, conf)


@ProfilingFunction
def acf(
    data: pd.Series,
    lags: int = 40,
    adjusted: bool = False,
    fft: bool = False,
    alpha: float = 0.05,
    missing: str = "none",
) -> pd.DataFrame:
    """Calculates the autocorrelation function on level data.

    Returns:
        pd.DataFrame: DataFrame with 4 columns: lag, correlation, low and up.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
    """
    return _acf(data, 0, lags=lags, adjusted=adjusted, fft=fft, alpha=alpha, missing=missing)


@ProfilingFunction
def acf_1d(
    data: pd.Series,
    lags: int = 40,
    adjusted: bool = False,
    fft: bool = False,
    alpha: float = 0.05,
    missing: str = "none",
) -> pd.DataFrame:
    """Calculates the autocorrelation function on 1-differenced data.

    Returns:
        pd.DataFrame: DataFrame with 4 columns: lag, correlation, low and up.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
    """
    return _acf(data, 1, lags=lags, adjusted=adjusted, fft=fft, alpha=alpha, missing=missing)


@ProfilingFunction
def acf_2d(
    data: pd.Series,
    lags: int = 40,
    adjusted: bool = False,
    fft: bool = False,
    alpha: float = 0.05,
    missing: str = "none",
) -> pd.DataFrame:
    """Calculates the autocorrelation function on 2-differenced data.

    Returns:
        pd.DataFrame: DataFrame with 4 columns: lag, correlation, low and up.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html
    """
    return _acf(data, 2, lags=lags, adjusted=adjusted, fft=fft, alpha=alpha, missing=missing)


@ProfilingFunction
def pacf(
    data: pd.Series, lags: int = 40, method: str = "ywadjusted", alpha: float = 0.05
) -> pd.DataFrame:
    """Calculates the partial autocorrelation function on level data.

    Returns:
        pd.DataFrame: DataFrame with 4 columns: lag, correlation, low and up.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.pacf.html
    """
    return _pacf(data, 0, lags=lags, method=method, alpha=alpha)


@ProfilingFunction
def pacf_1d(
    data: pd.Series, lags: int = 40, method: str = "ywadjusted", alpha: float = 0.05
) -> pd.DataFrame:
    """Calculates the partial autocorrelation function on 1-differenced data.

    Returns:
        pd.DataFrame: DataFrame with 4 columns: lag, correlation, low and up.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.pacf.html
    """
    return _pacf(data, 1, lags=lags, method=method, alpha=alpha)


@ProfilingFunction
def pacf_2d(
    data: pd.Series, lags: int = 40, method: str = "ywadjusted", alpha: float = 0.05
) -> pd.DataFrame:
    """Calculates the partial autocorrelation function on 1-differenced data.

    Returns:
        pd.DataFrame: DataFrame with 4 columns: lag, correlation, low and up.

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.pacf.html
    """
    return _pacf(data, 2, lags=lags, method=method, alpha=alpha)


@ProfilingFunction
def lag_corr(
    data: pd.Series, lags: Optional[Tuple[int, ...]] = tuple()
) -> Tuple[pd.DataFrame, pd.Series]:
    """Creates a DataFrame with the level data plus shifts as per the ``lags`` parameter.

    Args:
        data (pd.Series): Timeseries data.
        lags (Optional[Tuple[int, ...]]): Lags to shift the data on. If not supplied attempts to
            find appropriate defaults based on the frequency.

    Returns:
        pd.DataFrame, pd.DataFrame: DataFrame with shifted data, DataFrame with correlation between
        lagged and level
    """
    freq = data.index.inferred_freq
    freq = freq[0] if freq else ""
    if not lags:
        max_lag = len(data)
        lags_dic = {
            "A": (1, 2, 3, 4, 5, 6, 10, 15),
            "Q": (1, 2, 3, 4, 5, 6, 8, 16),
            "M": (1, 2, 3, 4, 6, 9, 12, 24),
            "W": (1, 2, 3, 4, 12, 24, 36, 48),
            "D": (1, 2, 3, 4, 5, 6, 7, 14, 30, 90, 180, 365),
            "B": (1, 2, 3, 4, 5, 10, 20, 40, 60, 120, 180, 240),
            "H": tuple(range(1, 25)),
        }
        lags = lags_dic.get(freq, (1, 2, 3)) or tuple()
        lags = tuple(lag for lag in lags if lag <= max_lag)
    df_lags = pd.concat(
        [data.rename("original")] + [data.shift(lag).rename(f"lag {lag}{freq}") for lag in lags],
        axis=1,
    )
    return df_lags, df_lags.corr()["original"]


@ProfilingFunction
def corr_pearson(data: pd.DataFrame) -> pd.DataFrame:
    """
    Args:
        data (pd.DataFrame): Timeseries dataframe.

    Returns:
        pd.DataFrame: Pearson correlation.
    """
    return data.corr(method="pearson")


@ProfilingFunction
def corr_kendall(data: pd.DataFrame) -> pd.DataFrame:
    """
    Args:
        data (pd.DataFrame): Timeseries dataframe.

    Returns:
        pd.DataFrame: Kendall correlation.
    """
    return data.corr(method="kendall")


@ProfilingFunction
def corr_spearman(data: pd.DataFrame) -> pd.DataFrame:
    """
    Args:
        data (pd.DataFrame): Timeseries dataframe.

    Returns:
        pd.DataFrame: Spearman correlation.
    """
    return data.corr(method="spearman")


@ProfilingFunction
def granger_causality(
    data: pd.DataFrame,
    test: str = "ssr_chi2test",
    addconst: bool = True,
    maxlag: int = 5,
    max_diff: int = 3,
    adf_confidence: float = 0.1,
) -> Tuple[pd.DataFrame, pd.DataFrame, int]:
    """Attempts to make the data stationary by applying differencing if needed (up to ``max_diff``)
    -- determined based on ADFuller test on ``adf_confidence`` with autolag calculation based on
    AIC; for each series pair, runs granger causality test and gets the smallest p-value and
    corresponding lag; builds a matrix with the result.

    Args:
        data (pd.DataFrame): Timeseries dataframe.
        test (str): Test name to use with Granger Causality.
        addconst (bool): Include a constant in the model.
        maxlag (int): Compute Granger Causality up til maxlag.
        max_diff (int): Diff at most max_diff times to attain stationarity.
        adf_confidence (float): Confidence level for the ADFuller test on stationarity.

    Returns:
        pd.DataFrame, pd.DataFrame, int: p-values matrix, lags matrix, number of differencing

    See Also:
        https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.grangercausalitytests.html
    """
    # only stationary
    df_ = data.fillna(method="bfill").fillna(method="ffill")
    stationary = []
    for d in range(max_diff + 1):
        stationary = [sms.adfuller(df_[c], autolag="AIC")[1] < adf_confidence for c in df_.columns]
        if all(stationary):
            break
        df_ = df_.diff().dropna()
    df_ = df_.iloc[:, [i for i, st in enumerate(stationary) if st]]

    dfp = pd.DataFrame(
        np.zeros((df_.shape[1], df_.shape[1])), columns=df_.columns, index=df_.columns
    )
    dfl = pd.DataFrame(
        np.zeros((df_.shape[1], df_.shape[1])), columns=df_.columns, index=df_.columns
    )
    for c in dfp.columns:
        for r in dfp.index:
            if c == r:
                min_p_value = np.nan
                min_lag = -1
            else:
                test_result = sms.grangercausalitytests(
                    df_[[r, c]], addconst=addconst, maxlag=maxlag, verbose=False
                )
                p_values = sorted(
                    [test_result[lag][0][test] for lag in range(1, maxlag + 1)],
                    key=lambda v: float(v[1]),
                )
                _, min_p_value, min_lag = p_values[0]
            dfp.loc[r, c] = min_p_value
            dfl.loc[r, c] = min_lag
    dfp.columns = [f"{c}[x]" for c in dfp.columns]
    dfp.index = [f"{c}[y]" for c in dfp.index]
    dfl.columns = [f"{c}[x]" for c in dfl.columns]
    dfl.index = [f"{c}[y]" for c in dfl.index]
    dfl = dfl.astype(int)
    return dfp, dfl, d
