import dash
# import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import flask

import index

normal_layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])

validation_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Upload(id='upload-compliance-report'),
    html.Div(id='output-upload-compliance-report'),
    dcc.Upload(id='upload-training-report'),
    html.Div(id='output-upload-training-report'),
])


def serve_content():
    if flask.has_request_context():
        return normal_layout
    else:
        return validation_layout


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

    app.layout = serve_content()
    idx = index.DGIndex(app)
    idx.run_app(app)
    app.run_server(debug=True)
