import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State

# Type hints@
from dash import Dash


def Navbar(app: Dash, download: bool = False):
    return html.Nav([
        html.Div([
            dcc.Link([
                html.Img(src=app.get_asset_url("logo-black.png")),
                html.Span("Compliance: The Basics")
            ], href="/home", className="nav-brand"),
            html.Ul(generate_nav_links(download=download), className="nav-links", id="nav-list")
        ], className="nav-container")
    ], className="navigation bg-nav")


def generate_nav_links(query: str = "", download: bool = False):
    query = query if query is not None else ""
    links = []
    if download:
        links.append(html.Button("Download Report", id="report-download"))
    links.append(dcc.Link("New dashboard", href="/new"))
    links.append(dcc.Link("View dashboard", href=f"/report{query}"))
    return links


def setup_callbacks(app: Dash):
    @app.callback(Output("nav-list", "children"),
                  [Input('url', 'href')],
                  [State("report-query", "data")],
                  prevent_initial_call=True)
    def update_nav_links(_, query_string):
        return generate_nav_links(query_string)

    # @app.callback([Output('javascript', 'run'),],
    #               [Input("report-download", "n_clicks")])
    # def setup_dowload(x):
    #     if x:
    #         return """
    #         var pageHTML = document.documentElement.outerHTML;
    #         var tempEl = document.getElementById("page-store");
    #         tempEl.dataset.store = encodeURI(pageHTML);
    #         """,
    #     return dash.no_update

    # @app.callback([Output("page-store", "data-store1"),
    #                Output("page-store", "data-store"),],
    #               [Input("interval-component", "n_intervals"),],
    #               [State("page-store", "data-store1"),
    #                State("page-store", "data-store"),],
    #               prevent_initial_call=True)
    # def stuff(_, data, data2):
    #     if data:
    #         print(_, data, data2)
    #     return ["dash.no_update", ""]


