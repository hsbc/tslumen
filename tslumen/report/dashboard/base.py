"""Base classes for building the dashboard."""
from abc import abstractmethod, ABC
from typing import Optional, Tuple, Callable, List, Any, Dict, Type

import pandas as pd

from tslumen.jinja_utils import create_jinja_env
from tslumen.profile import BundledResult
from tslumen.report.dashboard._dash import (
    Component,
    Input,
    Output,
    State,
    JupyterDash,
    html,
    dbc,
)


__all__ = [
    "JINJA_FILE_SEARCHPATHS",
    "TslumenDash",
    "BaseDash",
    "DashBlock",
    "DashInput",
    "DashSection",
]


JINJA_FILE_SEARCHPATHS = [
    "./tslumen/templates/dashboard",
    "./templates/dashboard",
    "./dashboard",
    "~/.tslumen/templates/dashboard",
    "~/.tslumen/dashboard",
]


class TslumenDash(JupyterDash):  # type: ignore
    """Extends `JupyterDash` in order to put in the default configurations."""

    def __init__(
        self, name: Optional[str] = None, server_url: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(name=name or "tslumen", server_url=server_url, **kwargs)
        env = create_jinja_env(
            paths=None,
            search_paths=JINJA_FILE_SEARCHPATHS,
            pkg_path="templates/dashboard",
            check="index.html",
        )
        template = env.get_template("index.html")
        self.index_string = template.render()


class BaseDash(ABC):
    """Base class for dash objects."""

    def __init__(
        self,
        result: BundledResult,
        meta: dict,
        df: pd.DataFrame,
        app: Optional[TslumenDash] = None,
        name: Optional[str] = None,
        server_url: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        app = app or TslumenDash(name=name, server_url=server_url, **kwargs)

        self.result = result
        self.meta = meta
        self.df = df
        self._app = app

        for fn_callback, outputs, inputs, states in self.callbacks:
            setattr(
                self,
                fn_callback.__name__,
                app.callback(
                    [Output(*o) for o in outputs],
                    [Input(*i) for i in inputs],
                    [State(*s) for s in states],
                )(fn_callback),
            )

        self._init_post()

    def _init_post(self) -> None:
        pass

    @property
    def callbacks(self) -> List[Tuple[Callable, List, List, List]]:
        return []

    @property
    @abstractmethod
    def layout(self) -> Component:
        pass

    @property
    def app(self) -> TslumenDash:
        return self._app

    @property
    def server(self) -> Any:
        return self.app.server

    def run_server(
        self,
        mode: Optional[str] = None,
        width: Any = "100%",
        height: Any = 650,
        inline_exceptions: Any = None,
        **kwargs: Any
    ) -> Any:
        self.app.layout = self.layout
        return self.app.run_server(
            mode=mode, width=width, height=height, inline_exceptions=inline_exceptions, **kwargs
        )


class DashBlock(BaseDash):
    """Base class for dash independent blocks, then composed into sections and the dashboard."""

    @property
    def block_id(self) -> str:
        return self.__class__.__name__.lower()

    @property
    def title(self) -> Optional[str]:
        return None

    @property
    def controls(self) -> Any:
        return None

    @property
    def body(self) -> Any:
        return None

    @property
    def style(self) -> dict:
        return {"height": "100%"}

    @property
    def layout(self) -> Component:
        card_body = [html.A(className="anchor-pos", id=self.block_id)]
        if self.title is not None or self.controls is not None:
            row = []
            if self.title:
                row.append(dbc.Col(html.H4(self.title)))
            if self.controls is not None:
                row.append(dbc.Col(html.Div(self.controls, className="float-right")))
            card_body.append(dbc.Row(row))
        card_body.append(dbc.Row(dbc.Col(self.body)))

        return dbc.Card(dbc.CardBody(card_body), style=self.style)


class DashInput(DashBlock):
    """Base class for dash input blocks."""

    @property
    def layout(self) -> Component:
        card = super().layout
        card.className = "ts-selector"
        return card


class DashSection(BaseDash):
    """Base class for independent sections, then composed into the dashboard."""

    @property
    def _block_classes(self) -> List[Type[DashBlock]]:
        return []

    @property
    def section_id(self) -> str:
        return self.__class__.__name__.lower()

    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    def controls(self) -> List[str]:
        return []

    @property
    @abstractmethod
    def body(self) -> Any:
        pass

    @property
    def anchors(self) -> List[Tuple[str, str]]:
        return []

    @property
    def layout(self) -> Component:
        hrow = [dbc.Col(html.H1(self.title))]
        if self.controls:
            hrow.append(
                dbc.Col(
                    html.Div(
                        [self.blocks[c].layout for c in self.controls],
                        className="float-right",
                    )
                )
            )
        return html.Div(
            [
                html.A(className="anchor-pos", id=self.section_id),
                dbc.Row(hrow),
                self.body,
            ],
            className="mb-4",
        )

    def __init__(
        self,
        result: BundledResult,
        meta: dict,
        df: pd.DataFrame,
        app: Optional[TslumenDash] = None,
        name: Optional[str] = None,
        server_url: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        super().__init__(
            result=result, meta=meta, df=df, app=app, name=name, server_url=server_url, **kwargs
        )
        self.blocks: Dict[str, DashBlock] = {
            klass.__name__: klass(self.result, self.meta, self.df, self.app)
            for klass in self._block_classes
        }
