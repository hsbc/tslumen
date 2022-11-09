"""Module with the sections that go into ``HtmlReport``."""
from typing import Dict, Any, Optional
from pprint import pformat

import pandas as pd
import yaml

import tslumen
from tslumen.misc import lazyproperty
from tslumen.scheduling import Scheduler
from tslumen.profile import BundledResult
from tslumen import jinja_utils as ju
from tslumen.report.html.base import HtmlBlock
from tslumen.plot.static import (
    TS,
    TSStack,
    Distribution,
    BoxPlot,
    LagCorrelation,
    LagMatrix,
    Radar,
    Heatmap,
    ScatterMatrix,
    GrangerMatrix,
    GrangerGraph,
)


__all__ = [
    "SectionSummary",
    "TabTSStatistics",
    "TabTSDistribution",
    "TabTSFeatures",
    "TabTSAutoCorrelation",
    "TabTSLagPlots",
    "TabTSComponents",
    "TabTSSeasonality",
    "TabTSSmoothing",
    "SubTimeSeries",
    "SectionTimeSeries",
    "SectionTSFeatures",
    "SectionRelations",
]


_PROFILERS_TSFEATURES = [
    "ft_stl",
    "ft_entropy",
    "ft_acf",
    "ft_pacf",
    "ft_tilewin",
    "ft_kpss",
    "ft_adfuller",
]
_FTS_MAIN = [
    "trend",
    "seasonality",
    "entropy",
    "entropy_acf",
    "instability",
    "lumpiness",
]
_FTS_STAT = [
    "kpss(c)",
    "kpss(ct)",
    "adfuller(c)",
    "adfuller(ct)",
    "adfuller(ctt)",
    "adfuller(nc)",
]
_FTS_ACF = [
    "acf1(d=0)",
    "acf1(d=1)",
    "acf1(d=2)",
    "acf10(d=0)",
    "acf10(d=1)",
    "acf10(d=2)",
    "pacf5(d=0)",
    "pacf5(d=1)",
    "pacf5(d=2)",
    "acf1(error)",
    "acf10(error)",
    "acf(season)",
    "pacf(season)",
]


class SectionSummary(HtmlBlock):
    """Class holding the contents of the "Summary" section"""

    _id = "summary"
    _title = "Summary"

    def __init__(
        self,
        result: BundledResult,
        meta: dict,
        df: pd.DataFrame,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        _ = (df, scheduler)
        frame = result.result.frame

        # Tab: Overview
        self.n_series = frame.get("n_series", "")
        self.length = frame.get("length", -1)
        self.dt_start = frame.get("dt_start", "")
        self.dt_end = frame.get("dt_end", "")
        self.freq = frame.get("freq", -1)
        self.period = frame.get("period", "")
        self.sz_total = frame.get("sz_total", -1)
        self.sz_rec = frame.get("sz_total", 0) / frame.get("n_series", 1)

        df_scaled = frame.get("df_scaled", None)
        self.plot = TS(df, figsize=(5.8, 2.8), yaxis=False, legend=True)
        self.plot_scaled = (
            None
            if df_scaled is None
            else TS(df_scaled, figsize=(5.8, 2.8), yaxis=False, legend=True)
        )

        # Tab: Metadata
        self.meta_frame = meta.get("frame", {})
        self.meta_series = meta.get("series", {})

        # Tab: Execution stats
        self.exec_start = result.start
        self.exec_end = result.end
        self.exec_duration = result.end - result.start
        self.package = "tslumen"
        self.version = tslumen.__version__
        self.config = result.result.config
        self.config_dict = pformat(result.result.config)
        self.config_yaml = yaml.dump(result.result.config)

        # Tab: Issues
        self.issues = (
            result.result.exec_details.query("~ Succeeded")[
                ["Profiler", "Scope", "Target", "Exceptions"]
            ]
            .sort_values(["Profiler", "Target"])
            .reset_index(drop=True)
        )


class TabTSStatistics(HtmlBlock):
    """Time Series tab: Statistics"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        stats = pd.Series(
            {
                name: result[fun]
                for name, fun in {
                    "Mean": "mean",
                    "Variance": "var",
                    "Standard deviation": "std",
                    "Median": "median",
                    "Median absolute deviation": "mad",
                    "Coefficient of variation": "cov",
                    "Minimum": "minimum",
                    "25%": "q25",
                    "50%": "q50",
                    "75%": "q75",
                    "Maximum": "maximum",
                    "Interquartile range": "iqr",
                    "Kurtosis": "kurtosis",
                    "Skewness": "skew",
                }.items()
            },
            name="Value",
        )
        self.stats = pd.DataFrame(stats)

        series_tests = {}
        for tname in [
            "levene_constant_variance",
            "ljungbox_autocorrelation",
            "jarque_bera_normality",
            "omnibus_normality",
            "adfuller_stationarity",
            "kpss_stationarity",
        ]:
            tr = result.get(tname, None)
            if not tr:
                continue
            series_tests[tr.test] = {
                "Null Hypothesis": tr.null_hypothesis,
                "Reject": "Yes" if tr.reject_null_hypothesis else "No",
                "pvalue": f"{tr.p_value:.3f}",
                "Confidence": f"{tr.confidence_level:.2f}",
            }
        self.tests = pd.DataFrame(series_tests).T.rename_axis(index="Test")


class TabTSDistribution(HtmlBlock):
    """Time Series tab: Distribution"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        self.plot_dist = Distribution(
            series=result["binned"],
            df_percentiles=result["pd_percentiles"],
            df_quantiles=result["pd_quantiles"],
            figsize=(6.8, 5),
        )


class TabTSFeatures(HtmlBlock):
    """Time Series tab: Features"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        df_fts = pd.concat([result[ft] for ft in _PROFILERS_TSFEATURES])
        self.df_fts_main = pd.DataFrame(df_fts[_FTS_MAIN].rename("Main"))
        self.df_fts_stat = pd.DataFrame(df_fts[_FTS_STAT].rename("Stationarity"))
        self.df_fts_acf = pd.DataFrame(df_fts[_FTS_ACF].rename("ACF/PACF"))
        self.plot_fts_main = Radar(self.df_fts_main)
        self.plot_fts_stat = Radar(self.df_fts_stat)
        self.plot_fts_acf = Radar(
            self.df_fts_acf.loc[
                [
                    "acf1(d=0)",
                    "acf1(d=1)",
                    "acf1(d=2)",
                    "acf1(error)",
                    "acf10(error)",
                    "acf(season)",
                ]
            ]
        )


class TabTSAutoCorrelation(HtmlBlock):
    """Time Series tab: Auto Correlation"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        self.plot_acf = LagCorrelation(df=result["acf"], title="ACF")
        self.plot_acf_1d = LagCorrelation(df=result["acf_1d"], title="ACF (1-diff)")
        self.plot_acf_2d = LagCorrelation(df=result["acf_2d"], title="ACF (2-diff)")
        self.plot_pacf = LagCorrelation(df=result["pacf"], title="PACF")
        self.plot_pacf_1d = LagCorrelation(df=result["pacf_1d"], title="PACF (1-diff)")
        self.plot_pacf_2d = LagCorrelation(df=result["pacf_2d"], title="PACF (2-diff)")


class TabTSLagPlots(HtmlBlock):
    """Time Series tab: Lag Plots"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        self.plot_lag = LagMatrix(
            original=result["lag_corr"][0].original,
            lags=result["lag_corr"][0].iloc[:, 1:],
            corr=result["lag_corr"][1],
        )


class TabTSComponents(HtmlBlock):
    """Time Series tab: Components"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        df = result["stl"]
        if df is None or df.empty:
            self.seasonality = False
            self.plot_stl = None
        else:
            self.seasonality = True
            self.plot_stl = TSStack(df=df, figsize=(6.8, 6))


class TabTSSeasonality(HtmlBlock):
    """Time Series tab: Seasonality"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        df = result["seasonal_split"]
        if df is None or df.empty:
            self.seasonality = False
            self.plot_seasonality = None
            self.plot_seas_box1 = None
            self.plot_seas_box2 = None
        else:
            self.seasonality = True
            self.plot_seasonality = TS(df=df, figsize=(6.8, 3), legend=False, colors="PuBu")
            dfb1 = (
                df.dropna(axis=1, how="all")
                .iloc[:, -10:]
                .fillna(method="bfill")
                .fillna(method="ffill")
            )
            dfb2 = df.T.dropna(how="all").fillna(method="bfill").fillna(method="ffill")
            self.plot_seas_box1 = BoxPlot(df=dfb1, figsize=(6.8, 2))
            self.plot_seas_box2 = BoxPlot(df=dfb2, figsize=(6.8, 2))


class TabTSSmoothing(HtmlBlock):
    """Time Series tab: Smoothing"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        _ = (name, ser)
        for var in ["rolling_avg", "supsmu", "lowess"]:
            df = result.get(var, None)
            if df is None:
                plot = None
            else:
                plot = TS(
                    df=df,
                    figsize=(6.8, 2),
                    line_width=[3],
                    colors=["#cecce0"] + TS.PALETTE[1:],
                )
            setattr(self, f"plot_{var}", plot)


class SubTimeSeries(HtmlBlock):
    """Class holding the content for each time series in the "Time Series" section"""

    def __init__(self, name: str, result: Dict[str, Any], ser: pd.Series) -> None:
        # Summary
        self.name = name
        self.mean = result["mean"]
        self.std = result["std"]
        self.minimum = result["minimum"]
        self.maximum = result["maximum"]
        self.zeros = result["zeros"]
        self.missing = result["missing"]
        self.infinite = result["infinite"]

        fmt_num, div_num = ju.format_number(result["sample"].mean())
        fmt_date = ju.format_date_freq(result["freq"])
        self.sample = pd.DataFrame(
            [[fmt_num.format(val / div_num) for val in result["sample"].T]],
            columns=[fmt_date.format(dt) for dt in result["sample"].index],
        )
        self.sample.insert(self.sample.shape[1] // 2, "...", "...")

        self.plot_ts = TS(pd.DataFrame(ser), figsize=(5, 2.3), legend=False)

        # Tabs
        self.tabs = {
            "Stats": TabTSStatistics(name, result, ser),
            "Distribution": TabTSDistribution(name, result, ser),
            "Features": TabTSFeatures(name, result, ser),
            "Components": TabTSComponents(name, result, ser),
            "Correlation": TabTSAutoCorrelation(name, result, ser),
            "Lags": TabTSLagPlots(name, result, ser),
            "Seasonal": TabTSSeasonality(name, result, ser),
            "Smoothing": TabTSSmoothing(name, result, ser),
        }


class SectionTimeSeries(HtmlBlock):
    """Class representing the Time Series section"""

    _id = "timeseries"
    _title = "Time Series"

    def __init__(
        self,
        result: BundledResult,
        meta: dict,
        df: pd.DataFrame,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        _ = meta
        self._series = result.result.series
        self._scheduler = scheduler or Scheduler()
        self._df = df
        self.series: Dict[str, SubTimeSeries] = {}

    @staticmethod
    def _run(name: str, series_result: Dict[str, Any], ser: pd.Series) -> SubTimeSeries:
        obj = SubTimeSeries(name, series_result, ser)
        _ = obj.html
        return obj

    @lazyproperty
    def html(self) -> str:
        objs = self._scheduler.run(
            self._run,
            [(name, series_result, self._df[name]) for name, series_result in self._series.items()],
            desc="Rendering TimeSeries section",
        )
        self.series = {obj.name: obj for obj in objs}
        return str(super().html)


class SectionTSFeatures(HtmlBlock):
    """Class holding the contents of the "Features" section"""

    _id = "tsfeatures"
    _title = "Features"

    def __init__(
        self,
        result: BundledResult,
        meta: dict,
        df: pd.DataFrame,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        _ = (meta, df, scheduler)
        series = result.result.series

        self.df_fts = pd.concat(
            [
                pd.concat([ser[ft] for ft in _PROFILERS_TSFEATURES]).rename(name)
                for name, ser in series.items()
            ],
            axis=1,
        )
        self.df_fts = self.df_fts.loc[_FTS_MAIN]
        self.plot_radar = Radar(self.df_fts, figsize=(4, 4), linewidth=1.5, alpha=0, legend=True)
        self.plot_heat = Heatmap(self.df_fts.T)


class SectionRelations(HtmlBlock):
    """Class holding the contents of the "Correlations" section"""

    _id = "relations"
    _title = "Relations"

    def __init__(
        self,
        result: BundledResult,
        meta: dict,
        df: pd.DataFrame,
        scheduler: Optional[Scheduler] = None,
    ) -> None:
        _ = (meta, scheduler)
        frame = result.result.frame

        self.correlation = "Pearson"
        self.df_corr = frame["corr_pearson"]
        self.plot_scatter = ScatterMatrix(df=df, df_corr=self.df_corr)

        if frame["granger_causality"] is not None:
            self.dfp, self.dfl, self.granger_diff = frame["granger_causality"]
        else:
            self.dfp, self.dfl, self.granger_diff = None, None, -1
        self.granger_critical = 0.05
        if self.dfp is None:
            self.plot_granger_m = None
            self.plot_granger_g = None
        else:
            self.plot_granger_m = GrangerMatrix(
                dfp=self.dfp, dfl=self.dfl, critical=self.granger_critical
            )
            self.plot_granger_g = GrangerGraph(dfp=self.dfp, critical=self.granger_critical)
