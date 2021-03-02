from __future__ import annotations

import dash_core_components as dcc
import dash_html_components as html

from src.components import navbar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash import Dash

body = html.Div([
    html.H3("Compliance: The Basics"),
    html.H4("Compliance dashboard generator"),
    html.Br(),
    html.Span(dcc.Link("Create a new report", href="/new"), id="entry-point"),
    html.Br(),
    html.Em([
        "If you have any questions, please ",
        html.A("contact the developer", href="https://forms.gle/5iiLrRdMh1skJfeL9", target="_blank"),
        ", Adam Turner"])
], className="page-container static-container vertical-center home")


def Homepage(app: Dash) -> html.Div:
    return html.Div([
        navbar.Navbar(app),
        body
    ], className="page")
