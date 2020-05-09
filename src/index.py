import dash
from dash.dependencies import Input, Output, State

from src.components import dashboard_generator
from src.components import homepage
from src.components import nopage
from src.components import new_dashboard
from src.components import navbar
from src import auth


class DGIndex:
    def __init__(self, app: dash.Dash):
        self.app = app
        self.dg = None

        self._setup_callbacks()

    def run_app(self, app: dash.Dash):
        self.dg = dashboard_generator.DashbordGenerator(app)

    def _setup_callbacks(self):
        app = self.app
        new_dashboard.setup_callbacks(app)
        navbar.setup_callbacks(app)
        auth.setup_auth_callbacks(app)
        self._routing_callback()

    def _routing_callback(self):
        app = self.app

        @app.callback([Output('page-content', 'children'),
                       Output('old-url', 'data'), ],
                      [Input('url', 'pathname'),
                       Input('login-url', 'pathname')],
                      [State('url', 'search')])
        def route_logins(_, __, query):
            del _, __
            # Find the latest pathname to change
            pathname = dash.callback_context.triggered[0].get("value")
            if pathname == '/login':
                return auth.login_layout(), dash.no_update
            else:
                return display_app_page(pathname, query), pathname

        @auth.validate_login_session
        def display_app_page(pathname, query):
            if pathname == '/report':
                return self.dg.get_dashboard(query)
            elif pathname in ['/', '/home'] or pathname is None:
                return homepage.Homepage(app)
            elif pathname == '/new':
                return new_dashboard.new_dashboard(app)
            else:
                return nopage.noPage(self.app)
