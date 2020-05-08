import flask
import dash
from uuid import uuid4

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
# import visdcc

import src.index as index

app: dash.Dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

server.secret_key = uuid4().bytes

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
    dcc.Location(id='login-url', refresh=False),
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
    html.Div(id='login-alert'),
    html.Button(id='login-button'),
    dcc.Input(id='login-username'),
    dcc.Input(id='login-password'),
])

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='login-url', refresh=False),
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

# @server.route('/download/<path:path>')
# def serve_report(path):
#     """Serve a file from the upload directory."""
#     return flask.send_from_directory(DOWNLOAD_DIR, path, as_attachment=True)

idx = index.DGIndex(app)
idx.run_app(app)

if __name__ == '__main__':
    print("Running server")
    app.run_server(debug=True)
