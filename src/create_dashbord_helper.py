import base64
import io
import math
import time
from urllib import parse
import zipfile
from openpyxl.utils import exceptions
import threading
import flask
import pandas as pd

import src.config as config

from typing import Dict


def create_query_string(c_contents, t_contents, title, location, valid_disclosures, app) -> dict:
    def output_value(value: str, button: bool = False, path: bool = False):
        if not button != path:
            raise ValueError("Exactly one of button or path must be set!")

        if path:
            return dict(type="path", value=value)
        else:
            return dict(type="button", value=value)

    def read_workbooks(data_props_dict, excluded_worksheets: list = None) -> Dict[Dict[pd.DataFrame]]:
        if not excluded_worksheets:
            excluded_worksheets = []
        workbooks = {}
        for k, data in data_props_dict.items():
            try:
                sheets = {}
                data = data.split(",")[1]
                with pd.ExcelFile(io.BytesIO(base64.b64decode(data)),  engine="openpyxl") as xls:
                    sheets_to_open = [s for s in xls.sheet_names if s not in excluded_worksheets]
                    for sheet in sheets_to_open:
                        sheets[sheet] = xls.parse(sheet_name=sheet, header=None)
            except (exceptions.InvalidFileException, zipfile.BadZipFile) as e:
                app.server.logger.warning(e)
                return output_value(f"This file can't be read, please check it is you have saved the {k} Assistant Report as an Excel file.", button=True)
            except exceptions.ReadOnlyWorkbookException as e:
                app.server.logger.warning(e)
                return output_value(f'There was an error processing the {k} Assistant Report file. Please ensure it is closed.', button=True)
            workbooks[k] = sheets
        return workbooks

    data_properties = {"Compliance": c_contents, "Training": t_contents}
    parsed_data = read_workbooks(data_properties, ["Report", "Appointments", ])

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
    disclosure_values = {"appropriate_adults": valid_disclosures}
    parsed_values = _parse_reports(parsed_data["Compliance"], parsed_data["Training"])
    parsed_values["data_date"] = parsed_values["data_date"]["compliance"]
    del parsed_values["assistant_versions"]
    meta_values = {"RT": title, "RL": location}

    values = {**disclosure_values, **parsed_values, **meta_values}
    parameters = {key_map[k]: v for k, v in values.items()}
    encoded = base64.urlsafe_b64encode(parse.urlencode(parameters).encode()).decode("UTF8")
    return output_value(f"?params={encoded}", path=True)


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


def parse_data(b64data: str, name):
    s = flask.session.get("s_id")
    now = time.strftime("%H%M%S")[1:-1]
    data = base64.b64decode(b64data.split(",")[1])
    threading.Thread(target=lambda: config.UPLOAD_DIR.joinpath(f"{s}#{now}-{name}").write_bytes(data))
