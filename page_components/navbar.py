import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from app import app

def Navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("New dashboard", href="/new")),
            dbc.NavItem(dbc.NavLink("View dashboard", href="/report")),
        ],
        brand="Compliance: The Basics",
        brand_href="/home",
        sticky="top",
    )


def Navbar2():
    return html.Nav([
        html.Div([
            html.Div([
                html.Img(src=app.get_asset_url("logo-purple.png"), className="nav-brand-img"),
                dcc.Link("Compliance: The Basics", className="nav-brand")
            ], className="nav-brand-div"),

            html.Div([
                html.Ul([
                    dcc.Link('Full View   ', href='/dash-vanguard-report/full-view'),
                    dcc.Link('Full View   ', href='/dash-vanguard-report/full-view')
                ], className="links-list")
            ], className="links")

        ], className="row gs-header"),
    ])