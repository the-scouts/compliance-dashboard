from __future__ import annotations

import dash_core_components as dcc
import dash_html_components as html

from src.components.navbar import Navbar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash import Dash


def noPage(app: Dash):
    return html.Div([
        # CC Header
        Navbar(app),
        page_not_found()
    ], className="page")


def page_not_found():
    return html.Div([
        html.H3("The page you requested does't exist."),
        dcc.Link([
            html.H4("Return to the start page")
        ], href="/home")
    ], className="page-container vertical-center static-container")
