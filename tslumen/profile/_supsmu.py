"""Wrapper around SuperSmoother to deal with edge cases"""
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from statsmodels.api import OLS, add_constant
from supersmoother import SuperSmoother


__all__ = ["supsmu"]


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
    x = np.arange(len(data))
    ys = data.interpolate(limit_direction="both")
    y = ys.values
    if len(y) < 100:
        span = 0.3
        j = round(len(y) * span)
        j += 1 if j % 2 == 0 else 1
        jj = j // 2
        yhat = np.concatenate(
            [
                OLS(y[:j], add_constant(x[:j])).fit().predict()[:jj],
                ys.rolling(j, center=True).mean()[jj:-jj],
                OLS(y[-j:], add_constant(x[-j:])).fit().predict()[-jj:],
            ]
        )
    else:
        est = SuperSmoother(
            alpha=alpha,
            period=period,
            primary_spans=primary_spans,
            middle_span=middle_span,
            final_span=final_span,
        )
        est.fit(x, y, presorted=True)
        yhat = est.predict(x)
    return pd.DataFrame({"original": data.values, "supsmu": yhat}, index=data.index)
