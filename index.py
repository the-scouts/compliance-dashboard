from dash.dependencies import Input, Output
from dash import Dash

from pages.dashboard_generator import DashbordGenerator
from pages.homepage import Homepage
from pages.nopage import noPage


def run_app(app: Dash):
    dg = DashbordGenerator(app)
    dg.set_info("County Team", "October 2019", "Central Yorkshire")
    dg.set_people(305, 389)

    @app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/report':
            return dg.get_dashboard()
        elif pathname == '/home':
            return Homepage(app)
        else:
            return noPage(app)
