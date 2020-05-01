import dash_html_components as html
import dash_core_components as dcc
from page_components.navbar import Navbar

# Type hints:
from dash import Dash


def noPage(app: Dash):
    return html.Div([
        # CC Header
        Navbar(app),
        page_not_found()
    ], className="no-page")


def page_not_found():
    return html.Div([
        html.H3("The page you requested does't exist."),
        dcc.Link([
            html.H4("Click here to go to the start page")
        ], href="/home")
    ], className="err-container")