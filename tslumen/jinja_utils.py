"""Jinja util functions"""
from math import ceil, log10, floor
from typing import List, Optional, Any, Tuple
from datetime import datetime
import re

import numpy as np
import pandas as pd
import jinja2


__all__ = [
    "format_date_freq",
    "format_number",
    "filter_numberformat",
    "filter_html",
    "filter_dateformat",
    "filter_autoformat",
    "filter_idhtml",
    "filter_islist",
    "create_jinja_env",
]


def format_date_freq(freq: Optional[str] = None) -> str:
    """
    Args:
        freq (Optional[str]): Time series frequency (follow's Panda's convention).

    Returns:
        str: Ideal datetime format string based on the frequency.
    """
    dt_fmt_default = "%Y-%m-%d %H:%M:%S"
    dt_fmt_dic = {
        "A": "%Y",
        "Q": "%Y-%m",
        "M": "%Y-%m",
        "W": "%Y-%m-%d (w%W)",
        "D": "%Y-%m-%d",
        "B": "%Y-%m-%d",
        "H": "%Y-%m-%d %H:%M",
    }
    freq = freq[0] if freq else ""
    fmt = dt_fmt_dic.get(freq, dt_fmt_default)
    return "{:" + fmt + "}"


def format_number(value: Any) -> Tuple[str, int]:
    """
    Args:
        value (Any): A number.

    Returns:
        str, int: Format string; Divisor -- value should be divided by this before formatting.

    """
    order = 0
    div = 1
    avalue = abs(round(value, 6))
    if avalue == 0 or (isinstance(value, int) and avalue < 1000):
        sig = 0
    elif avalue < 1:
        sig = ceil(log10(1 / avalue)) + 2
    else:
        sig = 2
    if avalue >= 1000:
        order = int(floor(log10(avalue) // 3))
        div = 10 ** (abs(order) * 3)
    suffixes = ["", "k", "m", "b", "t"]
    suffix = suffixes[min(order, len(suffixes) - 1)]
    fmt = "{:" + f",.{sig}f" + "}" + suffix
    return fmt, div


def filter_numberformat(value: Any) -> str:
    """Jinja filter to auto format numbers

    Args:
        value (Any): Number to format.

    Returns:
        str: Formatted number.
    """
    fmt, div = format_number(value)
    return fmt.format(value / div)


def filter_html(value: Any) -> str:
    """Jinja filter to try and get an HTML representation of an object while respecting the
    preferred precedence: ``obj.html``, ``obj._repr_html_``, ``str(obj)``.

    Args:
        value (Any): The object to represent as HTML.

    Returns:
        str: Object's HTML representation.

    """
    if value is None:
        return ""
    try:
        return str(getattr(value, "html"))
    except AttributeError:
        pass
    try:
        return str(getattr(value, "_repr_html_")())
    except AttributeError:
        pass
    return str(value)


def filter_dateformat(
    value: Any, fmt: str = "{:%Y-%m-%d %H:%M:%S}", freq: Optional[str] = None
) -> str:
    """Jinja filter to format a datetime. If a frequency is provided, uses it to obtain the best
    format, else defers to ``fmt``.

    Args:
        value (Any): Datetime to format.
        fmt (str): The datetime format to default to.
        freq (Optional[str]): The respective frequency.

    Returns:
        str: Formatted datetime.
    """
    if freq:
        fmt = format_date_freq(freq)
    return fmt.format(value)


def filter_autoformat(value: Any, **kwargs: Any) -> str:
    """Jinja filter to try and autoformat a given value based on its data type.

    Args:
        value (Any): Object to format.
        **kwargs (Any): Optional keyword arguments to pass along to the chosen formatter.

    Returns:
        str: Formatted object.
    """
    if value is None:
        return ""
    try:
        if isinstance(value, datetime):
            return filter_dateformat(value, **kwargs)
        elif isinstance(value, (int, float, np.int32, np.int64, np.float64)):
            return filter_numberformat(value)
        elif isinstance(value, pd.Series):
            return str(pd.DataFrame(value).T._repr_html_())
        else:
            return str(value._repr_html_())
    except Exception:
        pass
    return str(value)


def filter_idhtml(value: Any) -> str:
    """Sanitizes a string to be a valid HTML id attribute.

    Args:
        value (Any): Value to use as ID.

    Returns:
        str: Sanitized (HTML safe) ID.
    """
    return re.sub(r"\W", "-", str(value)).lower()


def filter_islist(value: Any) -> bool:
    """Checks if an object is list-like.

    Args:
        value (Any): Value to be checked.

    Returns:
        bool: Whether value is a list or a tuple.
    """
    return isinstance(value, (list, tuple))


def create_jinja_env(
    paths: Optional[List[str]],
    search_paths: Optional[List[str]],
    pkg_path: str,
    check: Optional[str] = None,
) -> jinja2.Environment:
    all_paths = paths or search_paths or []
    loaders: List[jinja2.BaseLoader] = [
        jinja2.FileSystemLoader(searchpath=path) for path in all_paths
    ]
    loaders.append(jinja2.PackageLoader("tslumen", pkg_path))
    env = jinja2.Environment(loader=jinja2.ChoiceLoader(loaders))
    if check:
        env.get_template(check)  # simple canary test just to see if templates can be reached

    env.filters["html"] = filter_html
    env.filters["dateformat"] = filter_dateformat
    env.filters["numberformat"] = filter_numberformat
    env.filters["autoformat"] = filter_autoformat
    env.filters["idhtml"] = filter_idhtml
    env.filters["islist"] = filter_islist

    return env
