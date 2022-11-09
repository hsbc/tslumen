"""Dash dependencies"""
from typing import Optional

import pandas as pd

from tslumen.misc import import_error_class, import_error_module


try:
    from dash.development.base_component import Component
    from dash.dependencies import Input, Output, State
except ImportError:
    Component = import_error_class("dash")
    Input = import_error_class("dash")
    Output = import_error_class("dash")
    State = import_error_class("dash")

try:
    from dash import dcc, html
except ImportError:
    try:
        import dash_core_components as dcc
        import dash_html_components as html
    except ImportError:
        dcc = import_error_module("dash_core_components")
        html = import_error_module("dash_html_components")

try:
    from jupyter_dash import JupyterDash
except ImportError:
    JupyterDash = import_error_class("jupyter_dash")

try:
    import dash_bootstrap_components as dbc
except ImportError:
    dbc = import_error_module("dash_bootstrap_components")


def EmptyFigure(
    width: Optional[int] = None, height: Optional[int] = 650, text: str = "No data"
) -> dict:
    return {
        "layout": {
            "height": height,
            "width": width,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "annotations": [
                {
                    "text": text,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 28},
                }
            ],
        }
    }


def Plot(pid: str, height: int) -> Component:
    return dbc.Spinner(
        dcc.Graph(id=pid, config={"displaylogo": False}, figure=EmptyFigure(height=height))
    )


def StatsTable(df: pd.DataFrame, title: str = "", classes: str = "") -> Component:
    table = html.Table(
        html.Tbody(
            [
                html.Tr([html.Th(ix)] + [html.Td(v, className="text-right") for v in val])
                for ix, val in df.iterrows()
            ]
        ),
        className=f"table table-condensed stats {classes}",
    )
    head = [html.H4(title)] if title else []
    return html.Div(head + [table])


def SimpleTable(
    df: pd.DataFrame,
    title: str = "",
    classes: str = "",
    show_index: bool = True,
    show_columns: bool = True,
) -> Component:
    header = []
    if show_columns:
        header = [
            html.Thead(
                [
                    html.Tr(
                        ([html.Th(df.index.name or "")] if show_index else [])
                        + [html.Th(col) for col in df.columns]
                    )
                ],
                className="thead-dark",
            )
        ]
    body = [
        html.Tbody(
            [
                html.Tr(
                    ([html.Th(index)] if show_index else []) + [html.Td(value) for value in row]
                )
                for index, row in df.iterrows()
            ]
        )
    ]
    table = html.Table(header + body, className=f"table table-sm table-striped dataframe {classes}")
    head = [html.H4(title)] if title else []
    return html.Div(head + [table])


def PopoverButton(
    content: Component,
    icon: str,
    name: str,
    color: str = "dark",
    size: str = "sm",
    trigger: str = "click",
    placement: str = "bottom",
    div_class: str = "",
) -> Component:
    button = dbc.Button(
        html.I(className=icon),
        color=color,
        outline=True,
        size=size,
        id=f"button-{name}",
    )
    pop = dbc.Popover(
        dbc.PopoverBody(content),
        id=f"pop-{name}",
        target=f"button-{name}",
        trigger=trigger,
        placement=placement,
    )
    return html.Div([button, pop], className=div_class)
