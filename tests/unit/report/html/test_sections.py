import mock
import pandas as pd
from tslumen.report.html.sections import (
    SectionSummary, SectionTSFeatures, SectionRelations, SectionTimeSeries,
    SubTimeSeries, TabTSStatistics, TabTSDistribution, TabTSFeatures, TabTSAutoCorrelation,
    TabTSLagPlots, TabTSComponents, TabTSSeasonality, TabTSSmoothing,
    _FTS_MAIN, _FTS_STAT, _FTS_ACF, _PROFILERS_TSFEATURES
)

from ..util import mkresult as _mkresult


def mkresult():
    _r, _d = _mkresult()
    for s in _r.result.series:
        del _r.result.series[s]['kpss_stationarity']
        del _r.result.series[s]['rolling_avg']
    return _r, _d


def mkresult_e():
    _r, _d = mkresult()
    for s in _r.result.series:
        _r.result.series[s]['stl'] = None
        _r.result.series[s]['seasonal_split'] = None
    _r.result.frame['granger_causality'] = None
    return _r, _d


@mock.patch('tslumen.report.html.sections.TS')
@mock.patch('tslumen.report.html.sections.TSStack')
@mock.patch('tslumen.report.html.sections.Distribution')
@mock.patch('tslumen.report.html.sections.BoxPlot')
@mock.patch('tslumen.report.html.sections.LagCorrelation')
@mock.patch('tslumen.report.html.sections.LagMatrix')
@mock.patch('tslumen.report.html.sections.Radar')
@mock.patch('tslumen.report.html.sections.Heatmap')
@mock.patch('tslumen.report.html.sections.ScatterMatrix')
@mock.patch('tslumen.report.html.sections.GrangerMatrix')
@mock.patch('tslumen.report.html.sections.GrangerGraph')
def _test_block(*args, kls=None, sid=None, stitle=None, mappings=None, plots=None, scope='section', fnres=mkresult):
    figs = {arg._mock_name: arg for arg in args}
    result, df = fnres()
    if scope == 'section':
        data = df
        section = kls(
            result=result,
            meta={},
            df=data
        )
        content = result.result.frame
        assert section._id == sid, f"_id expecting {sid} got {section._id}"
        assert section._title == stitle, f"_title expecting {stitle} got {section._title}"
    else:
        data = df.iloc[:, 0]
        section = kls(
            result=result.result.series[data.name],
            name=data.name,
            ser=data,
        )
        content = result.result.series[data.name]
    for k, val in mappings.items():
        if callable(val):
            expected = val(content )
        elif val is None:
            expected = content[k]
        else:
            expected = content[val]
        actual = getattr(section, k)
        compare = (lambda x, y: x.equals(y))\
            if isinstance(expected, pd.DataFrame)\
            else (lambda x, y: x == y)
        assert compare(actual, expected), f"Attribute {k}, expecting {expected} got {actual}"
    for plot, counts in plots.items():
        actual = figs[plot].call_count
        assert actual == counts, f"Plot {plot} expecting count {counts} got {actual}"
    return result, df, section


def test_summary():
    result, df, section = _test_block(
        kls=SectionSummary,
        sid="summary",
        stitle="Summary",
        mappings = dict(
            n_series=None,
            length=None,
            dt_start=None,
            dt_end=None,
            freq=None,
            period=None,
            sz_total=None,
            sz_rec=lambda x: x["sz_total"]/x["n_series"],
        ),
        plots=dict(TS=2)
    )
    assert section.exec_start == result.start
    assert section.exec_end == result.end
    assert section.package == "tslumen"
    assert section.config == {}
    assert section.config_dict.strip() == '{}'
    assert section.config_yaml.strip() == '{}'
    assert section.issues.equals(pd.DataFrame(columns=['Profiler', 'Scope', 'Target', 'Exceptions']))
    assert section.exec_duration == result.end - result.start
    assert section.meta_frame == {}
    assert section.meta_series == {}


def test_tsfeatures():
    result, df, section = _test_block(
        kls=SectionTSFeatures,
        sid="tsfeatures",
        stitle="Features",
        mappings = {},
        plots=dict(
            Radar=1,
            Heatmap=1,
        )
    )
    assert isinstance(section.df_fts, pd.DataFrame)
    assert section.df_fts.index.tolist() == _FTS_MAIN


def test_relations():
    _test_block(
        kls=SectionRelations,
        sid="relations",
        stitle="Relations",
        mappings = {
            'correlation': lambda x: 'Pearson',
            'df_corr': 'corr_pearson',
            'dfp': lambda x: x['granger_causality'][0],
            'dfl': lambda x: x['granger_causality'][1],
            'granger_diff': lambda x: x['granger_causality'][2],
            'granger_critical': lambda x: 0.05,
        },
        plots=dict(
            ScatterMatrix=1,
            GrangerMatrix=1,
            GrangerGraph=1,
        )
    )
    _test_block(
        kls=SectionRelations,
        sid="relations",
        stitle="Relations",
        mappings={},
        plots=dict(
            GrangerMatrix=0,
            GrangerGraph=0,
        ),
        fnres=mkresult_e
    )


@mock.patch('tslumen.report.html.sections.SubTimeSeries')
def test_timeseries(sts):
    class Seq:
        def run(self, fn, args, desc = ""):
            return [fn(*arg) for arg in args]

    result, df = mkresult()
    section = SectionTimeSeries(
        result,
        {},
        df,
        scheduler=Seq()
    )
    _ = section.html
    assert sts.call_count == df.shape[1]


@mock.patch('tslumen.report.html.sections.TabTSStatistics')
@mock.patch('tslumen.report.html.sections.TabTSDistribution')
@mock.patch('tslumen.report.html.sections.TabTSFeatures')
@mock.patch('tslumen.report.html.sections.TabTSComponents')
@mock.patch('tslumen.report.html.sections.TabTSAutoCorrelation')
@mock.patch('tslumen.report.html.sections.TabTSLagPlots')
@mock.patch('tslumen.report.html.sections.TabTSSeasonality')
@mock.patch('tslumen.report.html.sections.TabTSSmoothing')
def test_subtimeseries(*args):
    _test_block(
        kls=SubTimeSeries,
        sid=None,
        stitle=None,
        mappings={
            'name': lambda x: x['df_scaled'].name,
            'mean': None,
            'std': None,
            'minimum': None,
            'maximum': None,
            'zeros': None,
            'missing': None,
            'infinite': None,
        },
        plots=dict(
            TS=1,
        ),
        scope='sub'
    )
    for arg in args:
        arg.assert_called_once()


def test_tabstatistics():
    result, df, section = _test_block(
        kls=TabTSStatistics,
        sid=None,
        stitle=None,
        mappings={},
        plots=dict(),
        scope='tab'
    )
    result = result.result.series['Sales']
    for loc, key in {
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
        "Skewness": "skew"
    }.items():
        actual, expected = section.stats.loc[loc, 'Value'], result[key]
        assert actual == expected, f'Expecting result[{key}]={expected}, got stats[{loc}]={actual}'

    assert isinstance(section.tests, pd.DataFrame)
    assert section.tests.columns.tolist() == ["Null Hypothesis", "Reject", "pvalue", "Confidence"]
    assert section.tests.index.name == "Test"
    for test in ["levene_constant_variance", "ljungbox_autocorrelation", "jarque_bera_normality",
                 "omnibus_normality", "adfuller_stationarity"]:
        tr = result[test]
        assert tr.test in section.tests.index
        s = section.tests.loc[tr.test]
        assert s["Null Hypothesis"] == tr.null_hypothesis
        assert s["Reject"] == "Yes" if tr.reject_null_hypothesis else "No"
        assert float(s["pvalue"]) == round(tr.p_value, 3)
        assert float(s["Confidence"]) == round(tr.confidence_level, 2)


def test_tabdistribution():
    _test_block(
        kls=TabTSDistribution,
        sid=None,
        stitle=None,
        mappings={},
        plots=dict(Distribution=1),
        scope='tab'
    )


def test_tabtsfeatures():
    _test_block(
        kls=TabTSFeatures,
        sid=None,
        stitle=None,
        mappings={
            'df_fts_main': lambda x: pd.DataFrame(pd.concat([x[ft] for ft in _PROFILERS_TSFEATURES])[_FTS_MAIN], columns=['Main']),
            'df_fts_stat': lambda x: pd.DataFrame(pd.concat([x[ft] for ft in _PROFILERS_TSFEATURES])[_FTS_STAT], columns=['Stationarity']),
            'df_fts_acf': lambda x: pd.DataFrame(pd.concat([x[ft] for ft in _PROFILERS_TSFEATURES])[_FTS_ACF], columns=['ACF/PACF']),
        },
        plots=dict(Radar=3),
        scope='tab'
    )


def test_tabacf():
    _test_block(
        kls=TabTSAutoCorrelation,
        sid=None,
        stitle=None,
        mappings={},
        plots=dict(LagCorrelation=6),
        scope='tab'
    )


def test_tablagplots():
    _test_block(
        kls=TabTSLagPlots,
        sid=None,
        stitle=None,
        mappings={},
        plots=dict(LagMatrix=1),
        scope='tab'
    )


def test_tabcomponents():
    _test_block(
        kls=TabTSComponents,
        sid=None,
        stitle=None,
        mappings={
            'seasonality': lambda x: True,
        },
        plots=dict(TSStack=1),
        scope='tab'
    )
    _test_block(
        kls=TabTSComponents,
        sid=None,
        stitle=None,
        mappings={
            'seasonality': lambda x: False,
        },
        plots=dict(TSStack=0),
        scope='tab',
        fnres=mkresult_e,
    )


def test_tabseasonality():
    _test_block(
        kls=TabTSSeasonality,
        sid=None,
        stitle=None,
        mappings={
            'seasonality': lambda x: True,
        },
        plots=dict(TS=1, BoxPlot=2),
        scope='tab'
    )
    _test_block(
        kls=TabTSSeasonality,
        sid=None,
        stitle=None,
        mappings={
            'seasonality': lambda x: False,
        },
        plots=dict(TS=0, BoxPlot=0),
        scope='tab',
        fnres=mkresult_e,
    )


def test_tabsmoothing():
    _test_block(
        kls=TabTSSmoothing,
        sid=None,
        stitle=None,
        mappings={},
        plots=dict(TS=2),
        scope='tab'
    )
