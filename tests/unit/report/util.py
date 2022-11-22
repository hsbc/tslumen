import datetime
import copy
import numpy as np
import pandas as pd
from tslumen.profile.base import BundledResult, BundledResultDetails
from tslumen.profile.stat_tests import TestResult as StatTestResult


def mkts(series, length, dtstart='1911-11-01', ff='D'):
    return pd.DataFrame(
        {c: np.random.random(length) for c in series},
        index=pd.date_range(dtstart, freq=ff, periods=length)
    )


def mkacf():
    return pd.DataFrame({
            'lag': range(41),
            'correlation': np.random.random(41),
            'low': np.random.random(41),
            'up': np.random.random(41),
        })


def mkresult():
    cols = ['Sales', 'AdBudget', 'GDP']
    df = mkts(cols, 100, '1981-03-01', 'QS-DEC')
    result = BundledResult()
    result.result = BundledResultDetails()
    result.start = datetime.datetime(2021, 1, 1, 10, 30, 25)
    result.end = datetime.datetime(2021, 1, 1, 10, 31, 12)
    result.success: False
    result.exception = None
    result.name = 'BundledProfiler'
    result.scope = "both"
    result.target = ""
    result.result.exec_details = pd.DataFrame(
        columns=['Profiler', 'Scope', 'Target', 'Start', 'End', 'Duration', 'Succeeded', 'Exceptions', '# Runs'])
    result.result.config = {}
    result.result.frame = {
        'df_scaled': mkts(cols, 100, '1981-03-01', 'QS-DEC'),
        'dt_start': datetime.datetime(1981, 3, 1, 0, 0),
        'dt_end': datetime.datetime(2005, 12, 1, 0, 0),
        'freq': 'QS-DEC',
        'length': 100,
        'n_series': 3,
        'period': 4,
        'sz_total': 3200,
        'corr_kendall': pd.DataFrame(np.random.random((3,3)), index=cols, columns=cols),
        'corr_pearson': pd.DataFrame(np.random.random((3,3)), index=cols, columns=cols),
        'corr_spearman': pd.DataFrame(np.random.random((3,3)), index=cols, columns=cols),
        'granger_causality': (
            pd.DataFrame(np.random.random((3, 3)), index=cols, columns=cols),
            pd.DataFrame(np.random.random((3, 3)), index=cols, columns=cols),
            0)
    }
    result.result.series = {
        col: {
            'df_scaled': result.result.frame['df_scaled'][col],
            'freq': 'QS-DEC',
            'infinite': 0,
            'maximum': 1115.5,
            'mean': 948.737,
            'minimum': 735.1,
            'missing': 0,
            'period': 4,
            'sample': df[col].iloc[-10:],
            'std': 97.7596917497186,
            'zeros': 0,
            'cov': 0.10304193021851009,
            'iqr': 147.60000000000014,
            'kurtosis': -0.9043746422029222,
            'mad': 62.499999999999886,
            'median': 960.6500000000001,
            'q25': 871.0999999999999,
            'q50': 960.6500000000001,
            'q75': 1018.7,
            'skew': -0.3563224680501467,
            'var': 9556.957330999998,
            'adfuller_stationarity': StatTestResult(test='Augmented Dickey-Fuller', p_value=0.016627676807431355, confidence_level=0.05, null_hypothesis='Data has unit root', reject_null_hypothesis=True, details={'test_statistic': -3.2627546696298033, 'n_lags': 9, 'n_obs': 90, 'critical_values': {'1%': -3.505190196159122, '5%': -2.894232085048011, '10%': -2.5842101234567902}}),
            'jarque_bera_normality': StatTestResult(test='Jarque Bera', p_value=0.06316579843262377, confidence_level=0.05, null_hypothesis='Data is normally distributed', reject_null_hypothesis=False, details={'jarque_bera_test_statistic': 5.523984576704396, 'skew': -0.3563224680501467, 'kurtosis': 2.095625357797078}),
            'kpss_stationarity': StatTestResult(test='Kwiatkowski-Phillips-Schmidt-Shin', p_value=0.1, confidence_level=0.05, null_hypothesis='Data is level stationary', reject_null_hypothesis=False, details={'test_statistic': 0.3055440753326099, 'n_lags': 19, 'critical_values': {'10%': 0.347, '5%': 0.463, '2.5%': 0.574, '1%': 0.739}}),
            'levene_constant_variance': StatTestResult(test='Levene', p_value=0.9999999003188672, confidence_level=0.05, null_hypothesis='Variance is constant between 25 groups', reject_null_hypothesis=False, details={'t_statistic': 0.11547067866812606}),
            'ljungbox_autocorrelation': StatTestResult(test='Ljung-Box', p_value=5.0262219619456626e-95, confidence_level=0.05, null_hypothesis='No autocorrelation among specified lag(20)', reject_null_hypothesis=True, details={'acf': [1.0, 0.002461067314144716, -0.6990913096062669, -0.026673142009657477, 0.7728196412766846, -0.023771943264104527, -0.6577847019101651, -0.06307749652440088, 0.706228271061431, -0.04020875744244758, -0.6569155394819666, -0.04214139078382368, 0.6803447323793437, -0.050754857866383826, -0.6375658875126979, -0.005513000584307002, 0.6278598895169643, -0.06791842835004913, -0.5809051988138463, -0.014830059421764746, 0.6222820232658419], 'confidence_interval': [[1.0, 1.0], [-0.19353533113986068, 0.19845746576815013], [-0.8950888951779188, -0.5030937240346149], [-0.30228822491256957, 0.2489419408932546], [0.4971054150552452, 1.048533867498124], [-0.3729203005019381, 0.325376413973729], [-1.006995228578006, -0.3085741752423244], [-0.4570197446364463, 0.33086475158764456], [0.3118982309764343, 1.1005583111464277], [-0.4804534341565394, 0.4000359192716443], [-1.0973012664288528, -0.2165298125350803], [-0.5186855121706895, 0.43440273060304213], [0.20365747607995294, 1.1570319886787344], [-0.5633878463766271, 0.46187813064385946], [-1.1503918786040819, -0.12473989642131411], [-0.5479342475000197, 0.5369082463314057], [0.08543649014315913, 1.1702832888907695], [-0.6375760652720562, 0.501739208571958], [-1.1508738204091709, -0.010936577218521704], [-0.6071055869337723, 0.5774454680902428], [0.029992231372303335, 1.2145718151593805]], 'q_stat': [0.0006240393304289411, 50.86830080977383, 50.94311376181101, 114.40094729325723, 114.46162175560279, 161.412082218197, 161.84846350627674, 217.1455872305535, 217.32680470951692, 266.23444765764367, 266.43797740523235, 320.08869717498766, 320.3907174863644, 368.6023530838355, 368.6060002648886, 416.47411951269095, 417.04100760518867, 459.0166011428879, 459.0442961151968, 508.4167479663751], 'p_values': [0.9800702947852259, 8.996815766778383e-12, 5.030525745224091e-11, 8.376767315464388e-24, 4.667834587304637e-23, 2.9740966666156055e-32, 1.309571556589117e-31, 1.5434798523792796e-42, 7.635107175309984e-42, 2.0787272885786537e-51, 1.0005218518125141e-50, 2.8140919037590143e-61, 1.2866753434118743e-60, 5.1185275430986927e-70, 2.6764363624166534e-69, 1.276572254588111e-78, 5.04598702671192e-78, 4.1880938554057004e-86, 2.120838819069483e-85, 5.0262219619456626e-95]}),
            'omnibus_normality': StatTestResult(test='Omnibus', p_value=0.003124031197569999, confidence_level=0.05, null_hypothesis='Data is normally distributed', reject_null_hypothesis=True, details={'k2': 11.537262121273017}),
            'binned': pd.DataFrame([[11,12,11,22,28,16]], index=[735,798,861,925,988,1052]),
            'pd_percentiles': pd.DataFrame({
                'theoretical_percentiles': np.random.random(100),
                'sample_percentiles': [1.0] * 100,
                'reference': [1]*100,
            }),
            'pd_quantiles': pd.DataFrame({
                'theoretical_quantiles': np.random.random(100),
                'sample_quantiles':  np.random.random(100),
                'reference':  np.random.random(100),
            }),
            'acf': mkacf(),
            'acf_1d': mkacf(),
            'acf_2d': mkacf(),
            'pacf': mkacf(),
            'pacf_1d': mkacf(),
            'pacf_2d': mkacf(),
            'lag_corr': (
                mkts(['original', 'lag 1Q', 'lag 2Q', 'lag 3Q'], 100, '1981-03-01', 'QS-DEC'),
                pd.Series(np.random.random(4), index=['original', 'lag 1Q', 'lag 2Q', 'lag 3Q'], name='original')
            ),
            'seasonal_split': pd.DataFrame(np.random.random((4,6)),
                                           index=['03', '06', '09', '12'],
                                           columns=['1981', '1982', '1983', '1984', '1985', '1986']),
            'stl': mkts(['trend', 'seasonality', 'residual'], 100, '1981-03-01', 'QS-DEC'),
            'lowess': mkts(['original', 'lowess  5%', 'lowess 10%', 'lowess 15%'], 100, '1981-03-01', 'QS-DEC'),
            'rolling_avg': mkts(['original', 'rolling 2Q', 'rolling 4Q', 'rolling 8Q'], 100, '1981-03-01', 'QS-DEC'),
            'supsmu': mkts(['trend', 'original', 'supsmu'], 100, '1981-03-01', 'QS-DEC'),
            'ft_acf': pd.Series(np.random.random(7), index=['acf(season)', 'acf1(d=0)', 'acf10(d=0)', 'acf1(d=1)', 'acf10(d=1)', 'acf1(d=2)', 'acf10(d=2)']),
            'ft_adfuller': pd.Series(np.random.random(4), index=['adfuller(c)', 'adfuller(ct)', 'adfuller(ctt)', 'adfuller(nc)']),
            'ft_cross_pts': pd.Series(np.random.random(1), index=['crossing_points']),
            'ft_entropy': pd.Series(np.random.random(2), index=['entropy', 'entropy_acf']),
            'ft_kpss': pd.Series(np.random.random(2), index=['kpss(c)', 'kpss(ct)']),
            'ft_pacf': pd.Series(np.random.random(4), index=['pacf(season)', 'pacf5(d=0)', 'pacf5(d=1)', 'pacf5(d=2)']),
            'ft_stl': pd.Series(np.random.random(4), index=['trend', 'seasonality', 'acf1(error)', 'acf10(error)']),
            'ft_tilewin': pd.Series(np.random.random(2), index=['instability', 'lumpiness']),
        }
        for col in cols
    }
    return result, df

