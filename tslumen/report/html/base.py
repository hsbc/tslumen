"""Base classes for building the HTML report."""
from typing import Optional, Any
import uuid
import html
from jinja2 import Template

from tslumen import jinja_utils as ju
from tslumen.misc import lazyproperty


__all__ = ["JINJA_FILE_SEARCHPATHS", "HtmlBlock"]


JINJA_FILE_SEARCHPATHS = [
    "./tslumen/templates/html",
    "./templates/html",
    "./html",
    "~/.tslumen/templates/html",
    "~/.tslumen/html",
]


class HtmlBlock:
    """Basic HTML building block."""

    _id: str
    _title: str

    def _get_template(self, path: str) -> Template:
        env = ju.create_jinja_env(
            paths=None,
            search_paths=JINJA_FILE_SEARCHPATHS,
            pkg_path="templates/html",
            check="_base.html",
        )
        return env.get_template(path)

    def _make_iframe(
        self, src: str, ifid: Optional[str] = None, ifname: Optional[str] = None
    ) -> str:
        srce = html.escape(src)
        ifid = ifid or uuid.uuid4().hex
        ifname = ifname or ifid
        template = self._get_template("_iframe.html")
        return template.render(ifid=ifid, ifname=ifname, srce=srce)

    def _render(self, path: str, obj: Any) -> str:
        template = self._get_template(path)
        return template.render(obj=obj)

    @lazyproperty
    def html(self) -> str:
        """
        Returns:
            str: Class representation as a HTML block, as rendered by Jinja.
        """
        return self._render(path=f"{self.__class__.__name__}.html", obj=self)

    @lazyproperty
    def html_page(self) -> str:
        """
        Returns:
            str: Class representation as a full HTML page.
        """
        return self._render(path="_block.html", obj=self.html)

    def _repr_html_(self) -> str:
        """
        Returns:
            str: Class representation as a complete HTML document, embedded in an iframe.
        """
        return str(self._make_iframe(self.html_page))
