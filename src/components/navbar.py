from __future__ import annotations

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ClientsideFunction, Input, Output, State

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash import Dash


def Navbar(app: Dash, download: bool = False):
    return html.Nav([
        html.Div([
            dcc.Link([
                html.Img(src=app.get_asset_url("logo-black.png")),
                html.Span("Compliance: The Basics")
            ], href="/home", className="nav-brand"),
            html.Ul(generate_nav_links(download=download), className="nav-links", id="nav-list")
        ], className="nav-container")
    ], className="navigation bg-nav")


def generate_nav_links(query: str = "", download: bool = False):
    query = query if query is not None else ""
    links = []
    if download:
        links.append(html.A("Download Report", id="report-download-png"))
        # links.append(html.A("Download PDF", id="report-download"))
        links.append(html.Span("|"))
    links.append(dcc.Link("New dashboard", href="/new"))
    links.append(dcc.Link("View dashboard", href=f"/report{query}"))
    return links


def setup_callbacks(app: Dash):
    @app.callback(Output("nav-list", "children"),
                  [Input('url', 'href')],
                  [State("report-query", "data")],
                  prevent_initial_call=True)
    def update_nav_links(_, query_string):
        return generate_nav_links(query_string)

    # app.clientside_callback(
    #     ClientsideFunction(
    #         namespace="compliance",
    #         function_name="download_pdf"
    #     ),
    #     Output("report-download", "data-download"),
    #     [Input("report-download", "n_clicks")],
    #     prevent_initial_call=True
    # )

    app.clientside_callback(
        ClientsideFunction(
            namespace="compliance",
            function_name="download_png"
        ),
        Output("report-download-png", "data-download"),
        [Input("report-download-png", "n_clicks")],
        prevent_initial_call=True
    )
