import dash
# import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import index

app: dash.Dash = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.UNITED]
)
# app.config.suppress_callback_exceptions=True
# server = app.server

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

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])

if __name__ == '__main__':
    index.run_app(app)
    app.run_server(debug=True)
