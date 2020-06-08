import uuid

import flask

import dash
from dash.dependencies import Input, Output, State

from src import auth
from src.components import homepage, navbar, new_dashboard, nopage, render_dashboard


class DGIndex:
    def __init__(self, app: dash.Dash, cache):
        self.app = app
        self.cache = cache

        self.dg = None

        self._setup_callbacks()

    def init_app(self, app: dash.Dash):
        self.dg = render_dashboard.DashbordGenerator(app)

    def _setup_callbacks(self):
        app = self.app
        new_dashboard.setup_callbacks(app, self.cache)
        navbar.setup_callbacks(app)
        auth.setup_callbacks(app)
        self._routing_callback()

    def _routing_callback(self):
        app = self.app

        @app.callback([Output("page-content", "children"),
                       Output("old-url", "data"), ],
                      [Input("url", "pathname"),
                       Input("login-url", "pathname"),
                       Input("download-url", "pathname"), ],
                      [State("url", "search"),
                       State("login-url", "search"),
                       State("download-url", "search"), ])
        def route_logins(_u1, _u2, _u3, _q1, _q2, _q3):
            # Delete all input variables. We get the needed values through dash.callback_context
            del _u1, _u2, _u3, _q1, _q2, _q3
            ctx = dash.callback_context

            if not flask.session.get("s_id"):
                flask.session["s_id"] = uuid.uuid4().hex[:8]

            # Find the latest pathname to change
            pathname = ctx.triggered[0].get("value")

            # Set the URL search string
            # TODO check if we ever need the extra checking (the else & if not query checks)
            triggered_url = ctx.triggered[0].get("prop_id")
            if triggered_url:
                query = ctx.states.get(f"{triggered_url.split('.')[0]}.search")
            else:
                query = [q for q in ctx.states.values() if q][0]
            if not query:
                query = ""

            if pathname == "/login":
                return auth.login_layout(), dash.no_update
            else:
                return display_app_page(pathname, query), pathname

        @auth.validate_login_session
        def display_app_page(pathname, query):
            if pathname in [None, "/", "/home"]:
                return homepage.Homepage(app)
            elif pathname == "/report":
                return self.dg.get_dashboard(query)
            elif pathname == "/new":
                return new_dashboard.new_dashboard(app)
            else:
                return nopage.noPage(self.app)
