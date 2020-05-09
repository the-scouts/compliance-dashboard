import base64
import io
import math
import uuid
from urllib import parse

import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from xlrd import XLRDError

from src.components.navbar import Navbar
from src.config import PROJECT_ROOT
from src import create_dashbord_helper

UPLOAD_PATH = PROJECT_ROOT / "data"


def setup_callbacks(app: dash.Dash):
    session_id = uuid.uuid4().hex[:8]
    create_upload_callback(app, "compliance-report", session_id)
    create_upload_callback(app, "training-report", session_id)
    create_button_callback(app)
    pass


def create_upload_callback(app: dash.Dash, upload_id: str, guid):
    @app.callback([Output(f'upload-{upload_id}', 'children')],
                  [Input(f'upload-{upload_id}', 'filename')],
                  [State(f'upload-{upload_id}', 'contents')])
    def update_output(filename, contents):
        if filename is not None:
            data = contents.split(",")[1]
            with open(UPLOAD_PATH / f"{guid}-{filename}", "wb") as fp:
                fp.write(base64.b64decode(data))
            return [_upload_text(children=html.H5(filename))]
        return dash.no_update


def create_button_callback(app: dash.Dash, ):
    @app.callback([Output(f'button', "children"),
                   Output('url', 'pathname'),
                   Output('url', 'search'),
                   Output("report-query", "data"), ],
                  [Input("button", "n_clicks")],
                  [State(f'upload-compliance-report', 'contents'),
                   State(f'upload-training-report', 'contents'),
                   State(f'input-title', 'value'),
                   State(f'input-location', 'value'),
                   State(f'input-disclosures', 'value'), ],
                  prevent_initial_call=True)
    def update_button(clicked, c_contents, t_contents, title, location, valid_disclosures):
        ctx = dash.callback_context
        num_outputs = len(ctx.outputs_list)

        # Short circuit if empty
        if not clicked:
            return [dash.no_update] * len(ctx.outputs_list)

        def update_button_text(new_text: str):
            return [new_text] + [dash.no_update] * (num_outputs - 1)

        # Check all values are present
        inputs = [
            (c_contents, "Compliance Assistant Report"),
            (t_contents, "Training Assistant Report"),
            (title, "Report Title"),
            (location, "Report Location"),
            (valid_disclosures, "Valid Disclosures"),
        ]

        blank_inputs = []
        input_missing = False
        for input_tuple in inputs:
            if input_tuple[0] is None:
                input_missing = True
                blank_inputs.append(input_tuple[1])

        if input_missing:
            return update_button_text(f"Inputs missing: {'; '.join(blank_inputs)}")

        out = create_dashbord_helper.create_query_string(c_contents, t_contents, title, location, valid_disclosures)
        value = out["value"]
        if out["type"] == "button":
            return update_button_text(out["value"])
        else:
            query = value
            return [dash.no_update, "/report", query, query]


def new_dashboard(app: dash.Dash):
    return html.Div([
        Navbar(app),
        _new_dashboard(),
    ], className="page")


def _new_dashboard():
    return html.Div([
        html.Div([
            _upload_component("compliance-report", "Compliance Assistant Report"),
            _upload_component("training-report", "Training Assistant Report"),
        ], className="upload-group"),
        dcc.Input(
            id="input-title",
            type="text",
            placeholder="County Team",
        ),
        dcc.Input(
            id="input-location",
            type="text",
            placeholder="Central Yorkshire",
        ),
        dcc.Input(
            id="input-disclosures",
            type="number",
            placeholder=98.5,
            min=0, max=100, step=0.1,
        ),
        html.Button("Create Report", id="button")
    ], className="page-container app-container new-dash")


def _upload_component(upload_id: str, file_desc: str):
    return dcc.Upload(
        _upload_text(file_desc=file_desc),
        id=f'upload-{upload_id}',
        className="new-upload"
    )


def _upload_text(file_desc: str = None, children: str = None):
    if children is None:
        children = [
            html.Span(f"Upload a {file_desc}"),
            'Drag and Drop here or ',
            html.A('Select Files')
        ]
    return html.Div(children, className="upload-text")
