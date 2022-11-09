import mock
from pkg_resources import DistributionNotFound
from importlib import reload


def test_version():
    import tslumen
    assert isinstance(tslumen.__version__, str)


def test_no_version():
    import tslumen
    with mock.patch('pkg_resources.get_distribution', autospec=True) as ver:
        ver.side_effect = lambda *args, **kwargs: (_ for _ in ()).throw(DistributionNotFound())
        tslumen = reload(tslumen)
        assert tslumen.__version__ == ""


def test_showversions(capsys):
    import tslumen
    tslumen.show_versions()
    captured = capsys.readouterr().out
    for l in tslumen.CORE_DEPENDENCIES:
        assert l in captured


def test_showversions_missing(capsys):
    import tslumen
    tslumen.CORE_DEPENDENCIES = ['foobar']
    tslumen.show_versions()
    captured = capsys.readouterr().out
    assert 'foobar' in captured
    assert 'not installed' in captured


def test_showversions_nover(capsys):
    import tslumen
    tslumen.CORE_DEPENDENCIES = ['tslumen.profile']
    tslumen.show_versions()
    captured = capsys.readouterr().out
    assert 'tslumen.profile' in captured
    assert 'cannot determine version' in captured
