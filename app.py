from pathlib import Path
import flask
import dash
# import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import visdcc

import index

PROJECT_ROOT = Path("./").resolve().absolute()
DOWNLOAD_DIR = PROJECT_ROOT / "download"

normal_layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    dcc.Store(id="report-query", storage_type="local"),

    # content will be rendered in this element
    html.Div(id='page-content')
])


if __name__ == '__main__':
    app: dash.Dash = dash.Dash(__name__)
    server = app.server

    # # Keep this out of source code repository - save in a file or a database
    # VALID_USERNAME_PASSWORD_PAIRS = {
    #     "comp": "92point8",
    # }
    # auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

    app.index_string = """ 
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>Compliance Dashboard Generator - DEVELOPMENT (Adam Turner)</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    """

    app.validation_layout = html.Div([
        html.Div(id='page-content'),
        # html.Div(id="page-store", style={"display": "none"}),
        html.Ul(id="nav-list"),
        html.Button(id='button'),
        html.Button(id="report-download"),
        dcc.Location(id='url', refresh=False),
        dcc.Store(id="report-query", storage_type="local"),
        # dcc.Store(id="page-store", storage_type="local"),
        dcc.Store(id="contents-compliance-report"),
        dcc.Store(id="contents-training-report"),
        dcc.Upload(id='upload-compliance-report'),
        dcc.Upload(id='upload-training-report'),
        dcc.Input(id="input-title"),
        dcc.Input(id="input-location"),
        dcc.Input(id="input-disclosures"),
        # dcc.Interval(id='interval-component'),
        # visdcc.Run_js(id='javascript'),
    ])

    app.layout = html.Div([
        # represents the URL bar, doesn't render anything
        dcc.Location(id='url', refresh=False),

        # html.Div(id="page-store", style={"display": "none"}),
        # dcc.Interval(id='interval-component', interval=2000),
        dcc.Store(id="report-query", storage_type="local"),
        # dcc.Store(id="page-store", storage_type="local", data="0"),
        dcc.Store(id="contents-compliance-report"),
        dcc.Store(id="contents-training-report"),
        # visdcc.Run_js(id='javascript'),

        # content will be rendered in this element
        html.Div(id='page-content')
    ])

    @server.route('/download/<path:path>')
    def serve_report(path):
        """Serve a file from the upload directory."""
        return flask.send_from_directory(DOWNLOAD_DIR, path, as_attachment=True)

    idx = index.DGIndex(app)
    idx.run_app(app)
    app.run_server(debug=True)
