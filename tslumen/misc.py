"""Miscellaneous utils available to all modules."""
from typing import Any, Callable, Type
from functools import wraps

__all__ = [
    "JINJA_FILE_SEARCHPATHS",
    "lazyproperty",
    "repr_html",
    "import_error_function",
    "import_error_class",
    "import_error_module",
]


JINJA_FILE_SEARCHPATHS = [
    "./tslumen/templates/ipython",
    "./templates/ipython",
    "./ipython",
    "~/.tslumen/templates/ipython",
    "~/.tslumen/ipython",
]


def lazyproperty(func: Callable) -> property:
    """Decorator to create lazy-loading properties. Creates a class attribute with the same name
    prefixed with an underscore and sets it to ``None``. When accessing the property, if the
    underscored attribute is ``None``, executes the decorated function and stores the result.
    Returns the underscored attribute.

    Args:
        func (Callable): Function to decorate.

    Returns:
        property: Decorated ``fn`` turned into a property.
    """

    @wraps(func)
    def lazy_(self: Any, *args: Any, **kwargs: Any) -> Any:
        field = f"_{func.__name__}"
        if getattr(self, field, None) is None:
            setattr(self, field, func(self, *args, **kwargs))
        return getattr(self, field)

    return property(lazy_)


def repr_html(klass: type) -> type:
    """Decorator to inject a ``_repr_html_`` method in a given class. Will attempt to load the jinja
    template and render to html, else returns html. Passes ``self`` onto the jinja variable ``obj``
    on the template. Template should be under ``/ipython`` (see
    ``tslumen.misc.JINJA_FILE_SEARCHPATHS`` for the full list of search paths).
    """
    from jinja2 import TemplateNotFound, TemplateError
    from tslumen.jinja_utils import create_jinja_env
    import warnings

    def _repr_html(self: Any) -> str:
        try:
            env = create_jinja_env(
                paths=None,
                search_paths=JINJA_FILE_SEARCHPATHS,
                pkg_path="templates/ipython",
                check="_base.html",
            )
            template = env.get_template(f"{klass.__module__}.{klass.__name__}.html")
            rendered = template.render(obj=self, oid=hex(id(self)))
            return rendered
        except TemplateNotFound as e:
            warnings.warn(f"could not find jinja template: {e}", UserWarning)
        except TemplateError as e:
            warnings.warn(f"jinja template error: {e}", UserWarning)
        except Exception as e:
            warnings.warn(f"Exception _repr_html_: {e}", UserWarning)
        return str(self)

    setattr(klass, "_repr_html_", _repr_html)
    return klass


def import_error_function(module: str) -> Callable:
    """Proxy function to raise import error"""

    def fn_error(*args: Any, **kwargs: Any) -> None:
        """Proxy function to raise import error"""
        _, _ = args, kwargs
        raise ImportError(f"Missing import '{module}'.")

    return fn_error


def import_error_class(module: str) -> Type:
    """Proxy class to raise import error"""

    class ClassError:
        """Proxy class to raise import error"""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _, _ = args, kwargs
            raise ImportError(f"Missing import '{module}'.")

    return ClassError


def import_error_module(module: str) -> Type:
    """Proxy "module" to raise import error"""

    class _Meta(type):
        def __getattr__(cls: Any, key: Any) -> Any:
            return cls

    class ModuleError(metaclass=_Meta):
        """Proxy class to raise import error"""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _, _ = args, kwargs
            raise ImportError(f"Missing import '{module}'.")

    return ModuleError
