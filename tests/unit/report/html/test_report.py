import mock
import pandas as pd
from io import StringIO

from tslumen.report.html import sections
from tslumen.scheduling import Scheduler
from tslumen.profile.base import BundledProfiler, BundledResult, BundledResultDetails
from tslumen.report.html.base import HtmlBlock
from tslumen.report.html.report import HtmlReport


def test_sections():
    assert HtmlReport.SECTIONS == [
        sections.SectionSummary,
        sections.SectionTimeSeries,
        sections.SectionTSFeatures,
        sections.SectionRelations,
    ]


def test_structure():
    r = HtmlReport(pd.DataFrame({'a': range(24)},
                                index=pd.date_range('2010-01-01', periods=24, freq='M')),
                   profiler=mock.create_autospec(spec=BundledProfiler),
                   scheduler=mock.create_autospec(spec=Scheduler))
    r.SECTIONS = []
    assert r.sections == []
    assert r.duration is None

    html = r.html
    assert html is not None
    assert r.duration is not None


def test_univariate():
    r = HtmlReport(pd.DataFrame({'a': range(24)},
                                index=pd.date_range('2010-01-01', periods=24, freq='M')),
                   profiler=mock.create_autospec(spec=BundledProfiler),
                   scheduler=mock.create_autospec(spec=Scheduler))
    smts = mock.create_autospec(spec=HtmlBlock)
    suts = mock.create_autospec(spec=HtmlBlock)
    r.SECTIONS = [smts, suts]
    r._multiple_series = [smts]
    r._sequential = [smts, suts]

    _ = r.html
    suts.assert_called_once()
    smts.assert_not_called()

    assert r.html is not None
    assert r.result is not None
    r.result = '123'
    assert r._html is None


def test_multivariate():
    r = HtmlReport(pd.DataFrame({'a': range(24), 'b': range(24)},
                                index=pd.date_range('2010-01-01', periods=24, freq='M')),
                   profiler=mock.create_autospec(spec=BundledProfiler),
                   scheduler=mock.create_autospec(spec=Scheduler))
    smts = mock.create_autospec(spec=HtmlBlock)
    suts = mock.create_autospec(spec=HtmlBlock)
    r.SECTIONS = [smts, suts]
    r._multiple_series = [smts]
    r._sequential = [smts, suts]

    _ = r.html
    suts.assert_called_once()
    smts.assert_called_once()

    assert r.html is not None
    assert r.result is not None
    r.result = '123'
    assert r._html is None


def test_save(tmpdir):
    pr = BundledResult()
    pr.result = BundledResultDetails()
    pr.result.series = {}
    r = HtmlReport(pd.DataFrame({'a': range(24), 'b': range(24)},
                                index=pd.date_range('2010-01-01', periods=24, freq='M')),
                   result=pr)
    r._html_page = 'foobar'
    assert isinstance(r.save(), str)
    assert r.save() == 'foobar'
    with StringIO() as x:
        r.save(x)
        x.seek(0)
        assert x.read() == 'foobar'
    assert x.closed

    file = tmpdir.join('out.html')
    r.save(file.strpath)
    assert file.read() == 'foobar'

