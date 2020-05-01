import datetime

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from page_components.navbar import Navbar

import dash


def setup_callbacks(app: dash.Dash):
    create_upload_callback(app, "compliance-report")
    create_upload_callback(app, "training-report")


def create_upload_callback(app: dash.Dash, upload_id: str):
    @app.callback(Output(f'output-upload-{upload_id}', 'children'),
                  [Input(f'upload-{upload_id}', 'contents')],
                  [State(f'upload-{upload_id}', 'filename'),
                   State(f'upload-{upload_id}', 'last_modified')])
    def update_output(contents, name, date):
        if contents is not None:
            children = parse_contents(contents, name, date)
            return children


def parse_contents(contents, filename, date):
    return html.Div([
        html.H5(filename),

        html.H6(datetime.datetime.fromtimestamp(date)),

        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        # html.Img(src=contents),
        html.Hr(),
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


def new_dashboard(app: dash.Dash):
    return html.Div([
        Navbar(app),
        _new_dashboard(),
    ], className="new-dashboard-page")


def _new_dashboard():
    return html.Div([
        _upload_component("compliance-report"),
        _upload_component("training-report"),
        dcc.Input(
            id="input-title",
            type="text",
            placeholder="County Team",
        ),
        dcc.Input(
            id="input-disclosures",
            type="number",
            placeholder=98.50,
            min=0, max=100, step=0.01,
        )
    ], className="new-dashboard-container")


def _upload_component(upload_id: str):
    return html.Div([
        dcc.Upload(
            html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            id=f'upload-{upload_id}',
            className="new-upload"
        ),
        html.Div(id=f'output-upload-{upload_id}'),
    ])
