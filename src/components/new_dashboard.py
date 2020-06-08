import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ClientsideFunction, Input, Output, State

import src.create_dashbord_helper as create_dashbord_helper
import src.components.navbar as navbar


def setup_callbacks(app: dash.Dash, cache):
    create_upload_callback(app, "compliance-report", cache)
    create_upload_callback(app, "training-report", cache)
    create_button_callback(app, "button", "compliance-report", "training-report", cache)

    # Show a waiting spinner on clicking the button
    app.clientside_callback(
        ClientsideFunction(
            namespace="compliance",
            function_name="new_dashboard_spinner"
        ),
        Output("button", "data-popup"),
        [Input("button", "n_clicks")]
    )

    # If components are missing, re-hide the spinner
    app.clientside_callback(
        ClientsideFunction(
            namespace="compliance",
            function_name="new_dashboard_spinner_hide"
        ),
        Output("button", "data-popup-hide"),
        [Input("button", "children")]
    )


def create_upload_callback(app: dash.Dash, upload_id: str, cache):
    @app.callback(Output(f"upload-{upload_id}", "children"),
                  [Input(f"upload-{upload_id}", "filename")],
                  [State(f"upload-{upload_id}", "contents")])
    def update_output(filename: str, contents: str) -> html.Div:
        # Return quickly if no file exists
        if filename is None:
            raise dash.exceptions.PreventUpdate
        else:
            app.server.logger.info(f"Processing uploaded file {filename}")
            report_processor = create_dashbord_helper.ReportProcessor(app, contents, cache)
            report_processor.parse_data(filename)
        return _upload_text(children=html.H5(filename))


def create_button_callback(app: dash.Dash, button_id: str, compliance_upload_id: str, training_upload_id: str, cache):
    @app.callback([Output(button_id, "children"),
                   Output("url", "pathname"),
                   Output("url", "search"),
                   Output("report-query", "data"), ],
                  [Input(button_id, "n_clicks")],
                  [State(f"upload-{compliance_upload_id}", "contents"),
                   State(f"upload-{training_upload_id}", "contents"),
                   State("input-title", "value"),
                   State("input-disclosures", "value"), ],
                  prevent_initial_call=True)
    def update_button(clicked: int, c_contents: str, t_contents: str, title: str, valid_disclosures: float) -> tuple:
        # TODO accept only CSV/XLS(X)?

        # Short circuit if empty
        if not clicked:
            raise dash.exceptions.PreventUpdate

        start_time = time.time()
        ctx = dash.callback_context
        num_outputs = len(ctx.outputs_list)

        def update_button_text(new_text: str) -> tuple:
            return (new_text,) + (dash.no_update, ) * (num_outputs - 1)

        # Check all values are present
        inputs = [
            (c_contents, "Compliance Assistant Report"),
            (t_contents, "Training Assistant Report"),
            (title, "Report Title"),
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

        app.server.logger.info(f"Input validation took: {time.time() - start_time}")

        reports_parser = create_dashbord_helper.ReportsParser(app=app, session_id=True, cache=cache)
        out = reports_parser.create_query_string(title, valid_disclosures)
        value = out["value"]
        app.server.logger.info(f"Report processing took: {time.time() - start_time}")

        if out["type"] == "path":
            query = value
            return dash.no_update, "/report", query, query
        else:
            return update_button_text(out["value"])


def _upload_text(file_desc: str = None, children: str = None) -> html.Div:
    if children is None:
        children = [
            html.Span(f"Upload a {file_desc}"),
            "Drag and Drop here or ",
            html.A("Select Files")
        ]
    return html.Div(children, className="upload-text")


def _upload_component(upload_id: str, file_desc: str) -> dcc.Upload:
    return dcc.Upload(
        _upload_text(file_desc=file_desc),
        id=f"upload-{upload_id}",
        className="new-upload"
    )


def _new_dashboard() -> html.Div:
    return html.Div([
        html.Div([
            _upload_component("compliance-report", "Compliance Assistant Report"),
            _upload_component("training-report", "Training Assistant Report"),
        ], className="upload-group"),
        html.Span("Dashboard Report Title (e.g. County Team, Whole Region)"),
        dcc.Input(
            id="input-title",
            type="text",
            persistence=True,
        ),
        html.Span("Percentage of valid disclosures from Compass Disclosure Management Report (e.g. 98.5)"),
        html.Em("Please type only the number and not a percentage sign etc."),
        dcc.Input(
            id="input-disclosures",
            type="number",
            persistence=True,
            min=0, max=100, step=0.1,
        ),
        html.Button("Create Report", id="button"),
        html.Div(hidden=True, id="new-dashboard-warnings")
    ], className="page-container app-container new-dash")


def new_dashboard(app: dash.Dash) -> html.Div:
    return html.Div([
        navbar.Navbar(app),
        _new_dashboard(),
        html.Div(id="new-dash-popup", className="popup", style={"display": "none"}),
    ], className="page")
