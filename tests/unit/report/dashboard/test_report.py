import pytest
import pandas as pd
import flask
import mock

from tslumen.report.dashboard.report import *
from tslumen.report.dashboard.base import *
from tslumen.report.base import Report
from tslumen.scheduling import Scheduler
from tslumen.profile.base import BundledProfiler, BundledResultDetails

from ..util import mkresult as _mkresult


def mkresult():
    _r, _d = _mkresult()
    _r.result.exec_details = pd.DataFrame(
        [['foo', 'frame', '', _r.start, _r.end, _r.end-_r.start, False, '', 1]],
        columns=['Profiler', 'Scope', 'Target', 'Start', 'End', 'Duration', 'Succeeded', 'Exceptions', '# Runs'])
    return _r, _d


def test_dashboard():
    assert issubclass(Dashboard, Report)

    pr, df = mkresult()
    profiler = mock.create_autospec(spec=BundledProfiler)
    profiler.profile.return_value = pr
    scheduler = mock.create_autospec(spec=Scheduler)

    with pytest.raises(AssertionError):
        Dashboard(pd.DataFrame({'a': range(10000)},
                               index=pd.date_range('1980-01-01', freq='D', periods=10000)))

    with pytest.raises(AssertionError):
        Dashboard(pd.DataFrame({str(i): range(100) for i in range(25)},
                               index=pd.date_range('1980-01-01', freq='D', periods=100)))

    with pytest.warns(UserWarning, match=r'performance degrades.*'):
        class DDashboard(Dashboard):
            SECTIONS = []

        d = DDashboard(pd.DataFrame({'a': range(4000)},
                                    index=pd.date_range('1980-01-01', freq='D', periods=4000)),
                       profiler=profiler, scheduler=scheduler)
        assert isinstance(d.app, TslumenDash)
        assert isinstance(d.server, flask.Flask)

    with mock.patch('tslumen.report.dashboard.report.TslumenDash', autospec=True) as jd:
        d = Dashboard(df, result=pr)
        d.run_server(mode='external', width='20%', height=10, inline_exceptions=False)
        jd.return_value.run_server.assert_called_with(mode='external', width='20%', height=10, inline_exceptions=False)
        for n, sect in d.sections.items():
            assert isinstance(sect.app, TslumenDash)
            assert isinstance(sect.blocks, dict)
            assert sect.body is not None
            assert isinstance(sect.callbacks, list)
            assert isinstance(sect.controls, list)
            assert isinstance(sect.section_id, str)
            assert isinstance(sect.callbacks, list)
            assert isinstance(sect.title, str)
