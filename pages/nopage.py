import dash_html_components as html
from page_components.navbar import Navbar

# Type hints:
from dash import Dash


def noPage(app: Dash):
    return html.Div([
        # CC Header
        Navbar(app),
        html.P(["404 Page not found"])
    ], className="no-page")