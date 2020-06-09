import random
import os
import logging
import flask

import dash
import dash_core_components as dcc
import dash_html_components as html

import src.cache as cache
import src.config as config
import src.index as index

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


if __name__ != '__main__':
    app.enable_dev_tools(debug=True, dev_tools_hot_reload=False)
    debug_pin = os.environ["WERKZEUG_DEBUG_PIN"] = "-".join("".join([str(random.randint(0, 9)) for _ in range(3)]) for _ in range(4))
    gunicorn_logger = logging.getLogger('gunicorn.error')
    server.logger.handlers = gunicorn_logger.handlers
    server.logger.setLevel(gunicorn_logger.level)
    server.logger.info("#############################################################")
    server.logger.info("Running server on gunicorn")
    server.logger.info(f"Debugger PIN: {debug_pin}")
else:
    server.logger.setLevel(logging.DEBUG)

redis_cache = cache.CacheInterface(app)
redis_cache.load_from_disk()

app_router = index.DGIndex(app, redis_cache)
app_router.init_app(app)


if __name__ == '__main__':
    app.run_server(debug=True)
    server.logger.info("Running server!")

# TODO look into this maybe? serving from assets/css, assets/js etc.
# # Serving local static files
# @app.server.route('/static/<path:path>')
# def static_file(path):
#     static_folder = os.path.join(os.getcwd(), 'static')
#     return send_from_directory(static_folder, path)
