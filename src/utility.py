from __future__ import annotations
import base64
import io
import zipfile

import flask

import src.xml_excel_reader as xlsx

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import dash

    import pandas as pd

    import src.cache as cache_int


def read_workbooks(
        b64_data_list: list[str],
        app: dash.Dash,
        cache: cache_int.CacheInterface,
        included_worksheets: Optional[list[str]] = None,
        excluded_worksheets: Optional[list[str]] = None,
        session_id: str = "dummy"
) -> Dict[str, Dict[str, pd.DataFrame]]:
    front_sheets = {"Report Notes": "Compliance", "Notes": "Training"}
    if included_worksheets is None:
        included_worksheets = []
    if excluded_worksheets is None:
        excluded_worksheets = []

    workbooks = {}
    for data in b64_data_list:
        report_type = "unknown"
        try:
            sheets = {}
            data = data.split(",")[1]

            with xlsx.XMLExcelReader(io.BytesIO(base64.b64decode(data))) as xls:
                sheets_to_open = [s for s in xls.sheet_names if (s not in excluded_worksheets) and (s in included_worksheets if excluded_worksheets else True)]
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
                        cache.set_to_cache("session_cache", session_id, "processed_workbooks", report_type, value=False)
        except zipfile.BadZipFile as e:
            app.server.logger.warning(e)
            raise ValueError(output_value(f"This file can't be read, please check it is you have saved the {report_type} Assistant Report as an Excel file.", button=True))
        except PermissionError as e:
            app.server.logger.warning(e)
            raise ValueError(output_value(f"There was an error processing the {report_type} Assistant Report file. Please ensure it is closed.", button=True))
        workbooks[report_type] = sheets
    return workbooks


def get_session_id() -> str:
    return str(flask.session.get("s_id"))  # FIXME shouldn't need to  wrap with str, but mypy complains


def str_from_hash(hash_code: int) -> str:
    # upside down floor division to get ceil
    hash_code = hash_code % (10 ** 20)
    num_bytes = -(-(hash_code.bit_length() + 1) // 8)
    return base64.urlsafe_b64encode(hash_code.to_bytes(num_bytes, "big", signed=True)).decode("UTF8")


def output_value(value: str, button: bool = False, path: bool = False) -> dict[str, str]:
    if not button != path:
        raise ValueError("Exactly one of button or path must be set!")

    if path:
        return dict(type="path", value=value)
    else:
        return dict(type="button", value=value)
