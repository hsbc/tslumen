from datetime import datetime
import pytest
import numpy as np
import pandas as pd
import jinja2
from tslumen.jinja_utils import *


def test_filter_html():
    class A:
        html = 'YES'
        def _repr_html_(self):
            return 'NO'
        def __str__(self):
            return 'NO NO NO'
    class B:
        def _repr_html_(self):
            return 'YES'
        def __str__(self):
            return 'NO'
    class C:
        def __str__(self):
            return 'YES'

    assert filter_html(A()) == 'YES'
    assert filter_html(B()) == 'YES'
    assert filter_html(C()) == 'YES'
    assert filter_html(None) == ''
    assert filter_html(1) == '1'
    assert filter_html(True) == 'True'
    assert filter_html('abc') == 'abc'


def test_filter_dateformat():
    dt = datetime(2015, 11, 5, 18, 42, 2, 3)
    assert filter_dateformat(dt) == '2015-11-05 18:42:02'
    assert filter_dateformat(dt, fmt='{:%y}') == '15'
    assert filter_dateformat(dt, freq='A') == '2015'
    assert filter_dateformat(dt, freq='Q') == '2015-11'
    assert filter_dateformat(dt, freq='M') == '2015-11'
    assert filter_dateformat(dt, freq='W') == '2015-11-05 (w44)'
    assert filter_dateformat(dt, freq='D') == '2015-11-05'
    assert filter_dateformat(dt, freq='B') == '2015-11-05'
    assert filter_dateformat(dt, freq='H') == '2015-11-05 18:42'
    assert filter_dateformat(dt, freq='NOT A FREQ') == '2015-11-05 18:42:02'


def test_format_number(number, expected):
    actual = filter_numberformat(number)
    assert actual == expected, f"Expected {expected} got {actual}"


def test_autoformat():
    dt = datetime(2015, 11, 5, 18, 42, 2, 3)
    s = pd.Series([1, 2, 3])
    df = pd.DataFrame({'a': s})
    assert filter_autoformat(None) == ''
    assert filter_autoformat(dt) == '2015-11-05 18:42:02'
    assert filter_autoformat(0) == "0"
    assert filter_autoformat(10) == "10"
    assert filter_autoformat(-12.3) == "-12.30"
    assert filter_autoformat(-2783428) == "-2.78m"
    assert filter_autoformat(dt, fmt="{%X}") == '2015-11-05 18:42:02.000003'
    assert filter_autoformat(s) == str(pd.DataFrame(s).T._repr_html_())
    assert filter_autoformat(df) == str(df._repr_html_())


@pytest.mark.parametrize(
    "value,expected", [
        (' jksdh jlk jk jk jk jk  ', '-jksdh-jlk-jk-jk-jk-jk--'),
        ('1232', '1232'),
        ('', ''),
        ('aA32%%1@#x', 'aa32--1--x')
    ])
def test_filter_idhtml(value, expected):
    actual = filter_idhtml(value)
    actuals = actual.replace('-', '')
    assert actual == expected, f"Expected {expected} got {actual}"
    assert not actuals or actuals.isalnum()
    assert not actuals or actuals.islower() or actuals.isnumeric()


def test_filter_islist():
    for lst in [[], list(), [1, 2, 3], tuple(), (1, 2, 3)]:
        assert filter_islist(lst)
    for n in [None, 1, 'a', 'asdfsad', 1.1, True, np.nan, np.array([1, 2, 3]),
              pd.DataFrame(), pd.DataFrame({'a': [1, 2]}), pd.Series([1, 2])]:
        assert filter_islist(n) is False


def test_format_date_freq():
    dt = datetime(2015, 11, 5, 18, 42, 2, 3)
    assert format_date_freq().format(dt) == '2015-11-05 18:42:02'
    assert format_date_freq('A').format(dt) == '2015'
    assert format_date_freq('Q').format(dt) == '2015-11'
    assert format_date_freq('M').format(dt) == '2015-11'
    assert format_date_freq('W').format(dt) == '2015-11-05 (w44)'
    assert format_date_freq('D').format(dt) == '2015-11-05'
    assert format_date_freq('B').format(dt) == '2015-11-05'
    assert format_date_freq('H').format(dt) == '2015-11-05 18:42'
    assert format_date_freq('NOT A FREQ').format(dt) == '2015-11-05 18:42:02'


@pytest.mark.parametrize(
    "number,expected", [
        (0, "0"),
        (10, "10"),
        (11, "11"),
        (230, "230"),
        (1000, "1.00k"),
        (1234, "1.23k"),
        (1239, "1.24k"),
        (353245, "353.25k"),
        (2783428, "2.78m"),
        (987489348, "987.49m"),
        (327827837878, "327.83b"),
        (375427835478345, "375.43t"),
        (-10, "-10"),
        (-11, "-11"),
        (-230, "-230"),
        (-1000, "-1.00k"),
        (-1234, "-1.23k"),
        (-1239, "-1.24k"),
        (-353245, "-353.25k"),
        (-2783428, "-2.78m"),
        (-987489348, "-987.49m"),
        (-327827837878, "-327.83b"),
        (-375427835478345, "-375.43t"),
        (0.10, "0.100"),
        (23.11, "23.11"),
        (123.230, "123.23"),
        (1000.23432, "1.00k"),
        (1231.1234, "1.23k"),
        (0.1239, "0.124"),
        (0.0353245, "0.0353"),
        (0.2783428, "0.278"),
        (0.987489348, "0.987"),
        (0.327827837878, "0.328"),
        (-0.375427835478345, "-0.375"),
    ]
)
def test_format_number(number, expected):
    fmt, div = format_number(number)
    actual = fmt.format(number / div)
    assert actual == expected, f"Expected {expected} got {actual}"


def test_create_jinja_env():
    env = create_jinja_env(None, None, '')
    assert isinstance(env, jinja2.Environment)
    assert "html" in env.filters
    assert "dateformat" in env.filters
    assert "numberformat" in env.filters
    assert "autoformat" in env.filters
    assert "idhtml" in env.filters
