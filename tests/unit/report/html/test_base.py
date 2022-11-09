import pytest
import mock
from tslumen.report.html.base import *
import jinja2


def test_make_iframe():
    # hardly comprehensive or robust...
    iframe = HtmlBlock()._make_iframe('XXX', '$$$', 'ZZZ')
    assert '<iframe' in iframe
    assert 'XXX' in iframe
    assert 'name="ZZZ"' in iframe
    assert 'id="$$$"' in iframe


def test_htmlblock():
    with mock.patch('tslumen.jinja_utils.create_jinja_env', autospec=True) as jinja:
        env = mock.create_autospec(spec=jinja2.Environment)
        env.get_template.side_effect = lambda path: jinja2.Template({
            '_block.html': 'full=[{{ obj }}]',
            '_iframe.html': 'ifid={{ifid}}|ifname={{ifname}}|srce={{srce}}',
        }.get(path, "id={{obj._id}}|title={{obj._title}}"))
        jinja.return_value = env

        hb = HtmlBlock()
        hb._id = 'AAA'
        hb._title = 'ZZZ'

        assert jinja.call_count == 0
        html = hb.html
        assert html == 'id=AAA|title=ZZZ'
        assert jinja.call_count == 1
        env.get_template.assert_called_with('HtmlBlock.html')

        html_c = hb.html_page
        assert html_c == 'full=[id=AAA|title=ZZZ]'
        assert jinja.call_count == 2
        env.get_template.assert_called_with('_block.html')

        html_i = hb._repr_html_()
        assert 'ifid=' in html_i
        assert 'ifname=' in html_i
        assert 'srce=full=[id=AAA|title=ZZZ]' in html_i
        assert jinja.call_count == 3
        env.get_template.assert_called_with('_iframe.html')
