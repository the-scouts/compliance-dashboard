import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

# Type hints@
from dash import Dash


def Navbar(app: Dash):
    return dbc.NavbarSimple(
        [
            dbc.NavItem(dbc.NavLink("New dashboard", href="/new")),
            dbc.NavItem(dbc.NavLink("View dashboard", href="/report")),
        ],
        brand="Compliance: The Basics",
        brand_href="/home",
        sticky="top",
    )


def Navbar2(app: Dash):
    return dbc.Nav([
        html.Div([
            dcc.Link([
                html.Div([
                    html.Img(src=app.get_asset_url("logo-purple.png"), className="nav-brand-img"),
                    html.Span("Compliance: The Basics", className="nav-brand-text")
                ], className="nav-brand-div"),
            ], href="/home", className="nav-brand-link"),


            html.Div([
                html.Ul([
                    dcc.Link("New dashboard", href="/new"),
                    dcc.Link("View dashboard", href="/report")
                ], className="links-list")
            ], className="links")

        ], className="row gs-header"),
    ])
