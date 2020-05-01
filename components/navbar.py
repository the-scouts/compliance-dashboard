import dash_html_components as html
import dash_core_components as dcc

# Type hints@
from dash import Dash


def Navbar(app: Dash):
    return html.Nav([
        html.Div([
            dcc.Link([
                html.Img(src=app.get_asset_url("logo-black.png")),
                html.Span("Compliance: The Basics")
            ], href="/home", className="nav-brand"),
            html.Ul([
                dcc.Link("New dashboard", href="/new"),
                dcc.Link("View dashboard", href="/report")
            ], className="nav-links")
        ], className="nav-container")
    ], className="navigation bg-nav")
