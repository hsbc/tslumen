import pytest
import importlib
import copy


def test_tslumendash():
    from tslumen.report.dashboard.base import TslumenDash, JupyterDash
    assert issubclass(TslumenDash, JupyterDash)


def patch_import(ex_names):
    import builtins
    _import = copy.copy(builtins.__import__)

    def _monkey(name, *args, **kwargs):
        if name in ex_names:
            raise ImportError
        return _import(name, *args, **kwargs)

    def wrapper(fn):
        def wraps(*args, **kwargs):
            builtins.__import__ = _monkey
            from tslumen.report.dashboard import _dash
            _dash = importlib.reload(_dash)
            try:
                return fn(_dash, *args, **kwargs)
            finally:
                builtins.__import__ = _import
                _dash = importlib.reload(_dash)
        return wraps
    return wrapper


@patch_import(['dash.development.base_component'])
def test_missing_dash1(_dash):
    with pytest.raises(ImportError):
        _dash.Component()


@patch_import(['dash.dependencies'])
def test_missing_dash(_dash):
    with pytest.raises(ImportError):
        _dash.Component()
    with pytest.raises(ImportError):
        _dash.Input()
    with pytest.raises(ImportError):
        _dash.Output()
    with pytest.raises(ImportError):
        _dash.State()


@patch_import(['dash_core_components', 'dash'])
def test_missing_dcc(_dash):
    with pytest.raises(ImportError):
        _dash.dcc.Graph()


@patch_import(['dash_html_components', 'dash'])
def test_missing_dcc(_dash):
    with pytest.raises(ImportError):
        _dash.html.H1('foobar')


@patch_import(['jupyter_dash'])
def test_missing_jupyterdash(_dash):
    with pytest.raises(ImportError):
        _dash.JupyterDash()


@patch_import(['dash_bootstrap_components'])
def test_missing_dbc(_dash):
    with pytest.raises(ImportError):
        _dash.dbc.Row()
