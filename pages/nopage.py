import dash_html_components as html
from page_components.navbar import Navbar

noPage = html.Div([
    # CC Header
    Navbar(),
    html.P(["404 Page not found"])
], className="no-page")