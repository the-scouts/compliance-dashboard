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

UPLOAD_PATH = PROJECT_ROOT / "data"


def setup_callbacks(app: dash.Dash):
    session_id = uuid.uuid4().hex[:8]
    create_upload_callback(app, "compliance-report", session_id)
    create_upload_callback(app, "training-report", session_id)
    create_button_callback(app)
    pass


def create_upload_callback(app: dash.Dash, upload_id: str, guid):
    @app.callback([Output(f'upload-{upload_id}', 'children'),
                   Output(f'contents-{upload_id}', 'data'), ],
                  [Input(f'upload-{upload_id}', 'filename')],
                  [State(f'upload-{upload_id}', 'contents')])
    def update_output(filename, contents):
        if filename is not None:
            data = contents.split(",")[1]
            with open(UPLOAD_PATH / f"{guid}-{filename}", "wb") as fp:
                fp.write(base64.b64decode(data))
            return [_upload_text(children=html.H5(filename)), data]
        return dash.no_update


def create_button_callback(app: dash.Dash, ):
    @app.callback([Output(f'button', "children"),
                   Output('url', 'pathname'),
                   Output('url', 'search'),
                   Output("report-query", "data"), ],
                  [Input("button", "n_clicks")],
                  [State(f'contents-compliance-report', 'data'),
                   State(f'contents-training-report', 'data'),
                   State(f'input-title', 'value'),
                   State(f'input-location', 'value'),
                   State(f'input-disclosures', 'value'), ])
    def update_button(_, c_contents, t_contents, title, location, valid_disclosures):
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
            return [f"Inputs missing: {'; '.join(blank_inputs)}", dash.no_update, dash.no_update, dash.no_update]

        workbooks = {}
        for t in [(c_contents, "Compliance"), (t_contents, "Training")]:
            # _, content_string = t[0].split(',')
            # decoded = base64.b64decode(content_string)
            try:
                # sheets = pd.read_excel(io.BytesIO(t[0]), sheet_name=None, header=None)
                sheets = {}
                with pd.ExcelFile(io.BytesIO(base64.b64decode(t[0]))) as xls:
                    sheets_to_open = [s for s in xls.sheet_names if s not in ["Report", "Appointments"]]
                    for sheet in sheets_to_open:
                        sheets[sheet] = pd.read_excel(xls, sheet_name=sheet, header=None)
            except XLRDError as e:
                print(e)
                return [f'There was an error processing the {t[1]} Assistant Report file.', dash.no_update, dash.no_update, dash.no_update]
            workbooks[t[1]] = sheets

        values = _parse_reports(workbooks["Compliance"], workbooks["Training"])
        values["data_date"] = values["data_date"]["compliance"]
        values["appropriate_adults"] = valid_disclosures
        del values["assistant_versions"]
        key_map = {
            'appropriate_adults': "AA",
            'appropriate_roles': "AR",
            'getting_started_1': "GS1",
            'getting_started_2': "GS2",
            'getting_started_3_4': "GS34",
            'gdpr': "DP",
            'managing_safety': "SA",
            'safe_spaces': "SF",
            'preparedness': "FA",
            'knowledge': "WB",
            'total_adults': "TA",
            'total_roles': "TR",
            'target_value': "TV",
            'data_date': "DD",
        }
        parameters = {key_map[k]: v for k, v in values.items()}
        parameters["RT"] = title
        parameters["RL"] = location
        encoded = base64.urlsafe_b64encode(parse.urlencode(parameters).encode()).decode("UTF8")
        query = f"?params={encoded}"

        return [dash.no_update, "/report", query, query]


def _parse_reports(compliance_sheets, training_sheets):
    assistant_versions = {}
    data_date = {}
    # Compliance Report parsing:
    compliance_notes_df = compliance_sheets['Report Notes']
    compliance_summary_df = compliance_sheets['Summary']
    compliance_overdue_values = compliance_summary_df[[0, 10]].dropna()
    compliance_total_values = compliance_summary_df[[0, 4]].dropna()

    # Training Report parsing:
    training_summary_df = training_sheets["Summary"]
    training_notes_df = training_sheets["Notes"]
    training_overdue_values = training_summary_df[[0, 3]].dropna()

    # Values from Compliance Assistant Report

    data_date["compliance"] = compliance_notes_df.iat[4, 2].strftime("%B %Y")
    assistant_versions["compliance"] = compliance_notes_df.iat[0, 17]
    overdue_full_roles = compliance_overdue_values.iat[0, 1]                   # Overdue Full role
    overdue_getting_started_standard = compliance_overdue_values.iat[4, 1]     # Overdue M01 (Getting Started)
    overdue_personal_learning_plan = compliance_overdue_values.iat[7, 1]       # Overdue M02 (Personal Learning Plan)
    overdue_tools_for_the_role_leaders = compliance_overdue_values.iat[5, 1]   # Overdue M03 (Tools for the Role - Leaders)
    overdue_tools_for_the_role_managers = compliance_overdue_values.iat[6, 1]  # Overdue M04 (Tools for the Role - Managers)
    overdue_woodbadge_leader = compliance_overdue_values.iat[8, 1]             # Overdue Section Woodbadge
    overdue_woodbadge_manager = compliance_overdue_values.iat[9, 1]            # Overdue Manager Woodbadge
    overdue_first_aid = compliance_overdue_values.iat[10, 1]                   # Overdue First Aid MOL
    overdue_safety = compliance_overdue_values.iat[11, 1]                      # Overdue Safety MOL
    overdue_safeguarding = compliance_overdue_values.iat[12, 1]                # Overdue Safeguarding MOL

    total_adults = compliance_total_values.iat[0, 1]   # Total Adults in report
    total_roles = compliance_total_values.iat[1, 1]    # Total Roles in report

    # Values from Training Assistant Report
    data_date["training"] = training_notes_df.iat[3, 4].strftime("%B %Y")
    assistant_versions["training"] = training_notes_df.iat[0, 31]
    overdue_getting_started_trustee = training_overdue_values.iat[2, 1]     # Overdue M01EX (Getting Started for Trustees)
    overdue_gdpr = training_overdue_values.iat[3, 1]                        # Overdue GDPR

    # Clean up
    overdue_getting_started = overdue_getting_started_standard + overdue_getting_started_trustee
    overdue_tools_for_the_role = overdue_tools_for_the_role_leaders + overdue_tools_for_the_role_managers
    overdue_woodbadge = overdue_woodbadge_leader + overdue_woodbadge_manager

    target_val = int(10 ** round(math.log(total_roles) / 2 - 2, 0)) if total_roles > 20 else 1

    return dict(
        appropriate_roles=overdue_full_roles,
        getting_started_1=overdue_getting_started,
        getting_started_2=overdue_personal_learning_plan,
        getting_started_3_4=overdue_tools_for_the_role,
        gdpr=overdue_gdpr,
        managing_safety=overdue_safety,
        safe_spaces=overdue_safeguarding,
        preparedness=overdue_first_aid,
        knowledge=overdue_woodbadge,
        total_adults=total_adults,
        total_roles=total_roles,
        target_value=target_val,
        assistant_versions=assistant_versions,
        data_date=data_date,
    )


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
            placeholder=98.50,
            min=0, max=100, step=0.1,
        ),
        html.Button("Button", id="button")
    ], className="page-container app-container")


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
