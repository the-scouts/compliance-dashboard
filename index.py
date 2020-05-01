from dash.dependencies import Input, Output
from dash import Dash

from components import dashboard_generator
from components import homepage
from components import nopage
from components import new_dashboard


class DGIndex:
    def __init__(self, app: Dash):
        self.app = app
        self.dg = None

        self._setup_callbacks()

    def run_app(self, app: Dash):
        self.dg = dashboard_generator.DashbordGenerator(app)

        self.dg.set_info("County Team", "October 2019", "Central Yorkshire")
        self.dg.set_people(305, 389)

    def _setup_callbacks(self):
        new_dashboard.setup_callbacks(self.app)

        @self.app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
        def display_page(pathname):
            if pathname == '/report':
                return self.dg.get_dashboard()
            elif pathname == '/home':
                return homepage.Homepage(self.app)
            elif pathname == '/new':
                return new_dashboard.new_dashboard(self.app)
            else:
                return nopage.noPage(self.app)
