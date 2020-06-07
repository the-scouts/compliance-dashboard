import pkg_resources

import logging
import flask
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html

import src.config as config
import src.index as index
print("\n".join(f"{d.project_name} ({d.version})" for d in pkg_resources.working_set))

app: dash.Dash = dash.Dash(
    __name__,
    external_scripts=["https://unpkg.com/html2canvas@1.0.0-rc.5/dist/html2canvas.min.js"],
    assets_folder=config.ASSETS_DIR
)
server = app.server

server.secret_key = config.secret_key

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
    html.Ul(id="nav-list"),
    html.Button(id='button'),
    # html.A(id="report-download"),
    html.A(id="report-download-png"),
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='login-url', refresh=False),
    dcc.Location(id='download-url', refresh=False),
    dcc.Store(id="report-query", storage_type="local"),
    dcc.Store(id="old-url"),
    dcc.Upload(id='upload-compliance-report'),
    dcc.Upload(id='upload-training-report'),
    dcc.Input(id="input-title"),
    dcc.Input(id="input-location"),
    dcc.Input(id="input-disclosures"),
    html.Div(id='login-alert'),
    html.Button(id='login-button'),
    dcc.Input(id='login-username'),
    dcc.Input(id='login-password'),
])

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),
    dcc.Location(id='login-url', refresh=False),
    dcc.Location(id='download-url', refresh=True),

    # memory / localStorage / sessionStorage
    dcc.Store(id="old-url"),
    dcc.Store(id="report-query", storage_type="local"),
    # dcc.Store(id="page-store", storage_type="local", data="0"),

    # content will be rendered in this element
    html.Div(id='page-content'),
])


@server.route('/download/<path:path>')
def serve_report(path):
    """Serve a file from the upload directory."""
    return flask.send_from_directory(config.DOWNLOAD_DIR, path, as_attachment=True)


print(f"{id(config.global_path_cache_dict)} app.py")
app_router = index.DGIndex(app)
app_router.init_app(app)
app.enable_dev_tools(debug=True)
# from flask_caching import Cache
# cache = Cache()
# cache.init_app(app.server, config={
#     'CACHE_TYPE': 'simple',
#     # 'CACHE_DIR': config.DATA_ROOT / "cache"
# })

if __name__ == '__main__':
    app.run_server(debug=True)
    server.logger.info("Running server!")
else:
    app.enable_dev_tools(debug=True)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    server.logger.handlers = gunicorn_logger.handlers
    server.logger.setLevel(gunicorn_logger.level)
    server.logger.info("Running server on gunicorn")

# TODO look into this maybe? serving from assets/css, assets/js etc.
# # Serving local static files
# @app.server.route('/static/<path:path>')
# def static_file(path):
#     static_folder = os.path.join(os.getcwd(), 'static')
#     return send_from_directory(static_folder, path)
