from dash.dependencies import Input, Output, State
from dash import Dash

from components import dashboard_generator
from components import homepage
from components import nopage
from components import new_dashboard
from components import navbar


class DGIndex:
    def __init__(self, app: Dash):
        self.app = app
        self.dg = None

        self._setup_callbacks()

    def run_app(self, app: Dash):
        self.dg = dashboard_generator.DashbordGenerator(app)

    def _setup_callbacks(self):
        app = self.app
        new_dashboard.setup_callbacks(app)
        navbar.setup_callbacks(app)

        @app.callback(Output('page-content', 'children'), [Input('url', 'pathname')], [State('url', 'search')])
        def display_page(pathname, query):
            if pathname == '/report':
                return self.dg.get_dashboard(query)
            elif pathname == '/home':
                return homepage.Homepage(self.app)
            elif pathname == '/new':
                return new_dashboard.new_dashboard(self.app)
            else:
                return nopage.noPage(self.app)
