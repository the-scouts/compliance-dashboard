import base64
import io
import zipfile
from typing import Dict

import flask
import pandas as pd

import config as config
import xml_excel_reader as xlsx


def read_workbooks(b64_data_list, app, included_worksheets: list = None, excluded_worksheets: list = None, session_id: str = None) -> Dict[str, Dict[str, pd.DataFrame]]:
    front_sheets = {"Report Notes": "Compliance", "Notes": "Training"}

    def include_worksheet(worksheet: str) -> bool:
        if excluded_worksheets is not None:
            return worksheet not in excluded_worksheets
        if included_worksheets is None:
            return True
        return worksheet in included_worksheets

    session_id = session_id or "dummy"

    workbooks = {}
    for data in b64_data_list:
        report_type = "unknown"
        try:
            sheets = {}
            data = data.split(",")[1]

            with xlsx.XMLExcelReader(io.BytesIO(base64.b64decode(data))) as xls:
                sheets_to_open = [s for s in xls.sheet_names if include_worksheet(s)]
                for sheet in sheets_to_open:
                    sheets[sheet] = xls.read(sheet_name=sheet)

                    # Detect report / workbook type
                    if sheet in front_sheets:
                        cell_a1 = sheets[sheet].iloc[0, 0].lower()
                        if "compliance" in cell_a1:
                            report_type = "Compliance"
                        elif "training" in cell_a1:
                            report_type = "Training"

                        # Mark workbook as processing:
                        config.set_to_cache("session_cache", session_id, "processed_workbooks", report_type, value=False)
        except (zipfile.BadZipFile, ) as e:
            app.server.logger.warning(e)
            raise ValueError(output_value(f"This file can't be read, please check it is you have saved the {report_type} Assistant Report as an Excel file.", button=True))
        except PermissionError as e:
            app.server.logger.warning(e)
            raise ValueError(output_value(f"There was an error processing the {report_type} Assistant Report file. Please ensure it is closed.", button=True))
        workbooks[report_type] = sheets
    return workbooks


def get_session_id():
    return flask.session.get("s_id")


def str_from_hash(hash_code: int) -> str:
    # upside down floor division to get ceil
    hash_code = hash_code % (10 ** 20)
    num_bytes = -(-(hash_code.bit_length() + 1) // 8)
    return base64.urlsafe_b64encode(hash_code.to_bytes(num_bytes, "big", signed=True)).decode("UTF8")


def output_value(value: str, button: bool = False, path: bool = False) -> dict:
    if not button != path:
        raise ValueError("Exactly one of button or path must be set!")

    if path:
        return dict(type="path", value=value)
    else:
        return dict(type="button", value=value)
