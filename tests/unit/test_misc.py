import pytest
import mock
from inspect import isclass
import jinja2
from tslumen.misc import lazyproperty, repr_html, import_error_function, import_error_class, import_error_module


def test_lazyproperty():
    class Dummy:
        def __init__(self):
            self.val = 1

        @lazyproperty
        def a_prop(self):
            return self.val

    obj = Dummy()
    assert obj.val == 1
    assert obj.a_prop == 1
    obj.val = 23
    assert obj.a_prop == 1
    assert obj._a_prop == 1


def test_repr_html_ok():
    with mock.patch('tslumen.jinja_utils.create_jinja_env', autospec=True) as jinja:
        env = mock.create_autospec(spec=jinja2.Environment)
        env.get_template.return_value = jinja2.Template("name={{obj.name}}|oid={{oid}}")
        jinja.return_value = env

        @repr_html
        class Dummy:
            name = 'foo'

        assert getattr(Dummy, '_repr_html_')
        assert callable(Dummy._repr_html_)
        assert isinstance(Dummy()._repr_html_(), str)
        assert 'name=foo' in Dummy()._repr_html_()
        assert 'oid=' in Dummy()._repr_html_()


def test_repr_html_err_nf():
    with mock.patch('tslumen.jinja_utils.create_jinja_env', autospec=True) as jinja:
        env = mock.create_autospec(spec=jinja2.Environment)
        env.get_template.side_effect = lambda *args, **kwargs: (_ for _ in ()).throw(jinja2.TemplateNotFound(''))
        jinja.return_value = env

        @repr_html
        class Dummy: pass

        assert getattr(Dummy, '_repr_html_')
        with pytest.warns(UserWarning, match=r'could not find jinja template.*'):
            assert isinstance(Dummy()._repr_html_(), str)


def test_repr_html_err_t():
    with mock.patch('tslumen.jinja_utils.create_jinja_env', autospec=True) as jinja:
        env = mock.create_autospec(spec=jinja2.Environment)
        env.get_template.side_effect = lambda *args, **kwargs: jinja2.Template("{{ name ")
        jinja.return_value = env

        @repr_html
        class Dummy: pass

        assert getattr(Dummy, '_repr_html_')
        with pytest.warns(UserWarning, match=r'jinja template error.*'):
            assert isinstance(Dummy()._repr_html_(), str)


def test_repr_html_err_ex():
    with mock.patch('tslumen.jinja_utils.create_jinja_env', autospec=True) as jinja:
        env = mock.create_autospec(spec=jinja2.Environment)
        env.get_template.side_effect = lambda *args, **kwargs: (_ for _ in ()).throw(Exception())
        jinja.return_value = env

        @repr_html
        class Dummy: pass

        assert getattr(Dummy, '_repr_html_')
        with pytest.warns(UserWarning, match=r'Exception _repr_html_.*'):
            assert isinstance(Dummy()._repr_html_(), str)


def test_import_error_function():
    fn = import_error_function('foobar')
    assert callable(fn)
    with pytest.raises(ImportError):
        fn()
    with pytest.raises(ImportError):
        fn(1, 2)
    with pytest.raises(ImportError):
        fn(a=1, b=2)
    with pytest.raises(ImportError):
        fn(1, b=2)


def test_import_error_class():
    Kls = import_error_class('foobar')
    assert isclass(Kls)
    with pytest.raises(ImportError):
        Kls()
    with pytest.raises(ImportError):
        Kls(1, 2)
    with pytest.raises(ImportError):
        Kls(a=1, b=2)
    with pytest.raises(ImportError):
        Kls(1, b=2)


def test_import_error_module():
    lib = import_error_module('foobar')
    assert isclass(lib)
    with pytest.raises(ImportError):
        lib.foo()
    with pytest.raises(ImportError):
        lib.foo(1, 2)
    with pytest.raises(ImportError):
        lib.foo(1, b=2)
