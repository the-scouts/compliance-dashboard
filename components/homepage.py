import dash_core_components as dcc
import dash_html_components as html

from page_components.navbar import Navbar

# Type hints:
from dash import Dash


body = html.Div([
    html.H3("Compliance: The Basics"),
    html.H4("Compliance dashboard generator"),
    html.Br(),
    html.Span([
        "Please click ",
        dcc.Link("here", href="/new"),
        " to start a new report."
    ]),
    html.Br(),
    html.Span("If you have any questions, please contact the developer, Adam Turner")
], className="home")


def Homepage(app: Dash):
    return html.Div([
        Navbar(app),
        body
    ], className="home-page")


# app.layout = Homepage()
'''
@app.callback(
    Output(component_id='my-div',component_property='children'),
    [Input(component_id='my-dropdown',component_property='children')]
)
def update_text_output(button_selction):
    return "what the fuck is going on"
'''
