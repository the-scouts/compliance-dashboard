from __future__ import annotations
import base64
import hashlib
import json
import math
import os
from pathlib import Path
import threading
import time
from urllib import parse

import pydantic

import pandas as pd
import pyarrow

import src.cache as cache_int
import src.config as config
import src.utility as utility
import src.xml_excel_reader as xlsx

from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from collections.abc import Callable

    import dash


# TODO look into serialising dataframe w/ pyarrow and saving to redis etc.
# https://stackoverflow.com/questions/60365919/
# https://community.plotly.com/t/6199/4

class ReportBase:
    def __init__(self, cache: cache_int.CacheInterface, app: Optional[dash.Dash] = None, session_id: bool = False):
        self.app: Optional[dash.Dash] = app
        self.cache: cache_int.CacheInterface = cache

        # Set logger if app exists
        if app:
            self.logger = app.server.logger

        # Get flask session id. Must be in a flask request context.
        if session_id:
            self.session_id: str = utility.get_session_id()

    @staticmethod
    def run_thread(lambda_func: Callable[[], Any]) -> None:
        threading.Thread(target=lambda_func).start()
        threading.Thread(target=lambda_func).start()


class ReportsParser(ReportBase):
    def __init__(self, cache: cache_int.CacheInterface, app: Optional[dash.Dash] = None, session_id: bool = False):
        super().__init__(cache=cache, app=app, session_id=session_id)
        self.parsed_data: dict[str, dict[str, pd.DataFrame]] = {}

    def create_query_string(self, title: str, valid_disclosures: float) -> dict[str, str]:
        key_map = {
            "appropriate_adults": "AA",
            "appropriate_roles": "AR",
            "getting_started_1": "GS1",
            "getting_started_2": "GS2",
            "getting_started_3_4": "GS34",
            "gdpr": "DP",
            "managing_safety": "SA",
            "safe_spaces": "SF",
            "preparedness": "FA",
            "knowledge": "WB",
            "total_adults": "TA",
            "total_roles": "TR",
            "target_value": "TV",
            "data_date": "DD",
            "RT": "RT",
            "RL": "RL",
        }
        self.logger.info("Parsing results")
        user_provided_values = {"appropriate_adults": valid_disclosures, "RT": title}

        parsed_values = self.get_parsed_values()
        values = {**user_provided_values, **parsed_values.__dict__}
        parameters = {key_map.get(k) or k: v for k, v in values.items()}

        trend_data = {"Location": parsed_values.RL, "Include Descendents": parsed_values.has_children, "Date": parsed_values.data_date, "JSON": parameters}
        self.logger.debug(f"trend_data: {trend_data}")
        self.run_thread(lambda_func=lambda: self.save_trends(trend_data))

        encoded = base64.urlsafe_b64encode(parse.urlencode(parameters).encode()).decode("UTF8")
        return utility.output_value(f"?params={encoded}", path=True)

    def get_parsed_values(self) -> ParsedData:
        self.logger.info("Reading main sheets")

        def get_processed_workbooks_values() -> list[str]:
            processed = self.cache.get_dict_from_partial("session_cache", self.session_id, "processed_workbooks") or {}
            return list(processed.values())

        i = 0
        processed_wbs = get_processed_workbooks_values()
        while (not all(processed_wbs) or len(processed_wbs) == 0) and i < 90 / 0.25:
            self.logger.info(f"Processed workbook vals: {processed_wbs}")
            time.sleep(0.25)
            i += 1
            processed_wbs = get_processed_workbooks_values()
        self.logger.info("ALL PROCESSED!")

        reports_paths: dict[str, dict[str, str]] = {}
        for paths_dict in [self.cache.get_dict_from_partial("b64_cache", code) for code in processed_wbs]:
            reports_paths |= paths_dict
        self.logger.info("Reports Paths:")
        self.logger.info(reports_paths)
        self.logger.info(f"Debug pin: {os.environ['WERKZEUG_DEBUG_PIN']}")

        for report_name, sheets in reports_paths.items():
            self.parsed_data[report_name] = {}
            for sheet_name, sheet_path in sheets.items():
                frame = pd.read_feather(sheet_path).replace("<NA>", pd.NA)
                frame.columns = frame.columns.astype("int64")
                self.parsed_data[report_name][sheet_name] = frame
                del frame

        self.logger.info("Calling store trend data")
        # TODO get trend data and use in report
        self.logger.debug(self.parsed_data.keys())
        self.logger.debug(self.parsed_data.get("Compliance", {}).keys())
        appt_props = self.read_appointments_report(self.parsed_data["Compliance"]["Appointments"])
        self.logger.info(f"Appointments Props: {appt_props}")
        report_location = appt_props["location_name"]

        parsed_values = self._parse_reports()
        data_date = parsed_values.data_date.compliance or parsed_values.data_date.training or None,
        pruned_parsed = {key: value for key, value in parsed_values if key not in {'assistant_versions', 'data_date'}}

        metadata = {
            "data_date": data_date,
            "RL": report_location,
            "has_children": appt_props["has_children"],
        }

        self.run_thread(lambda_func=self.cache.save_to_disk)
        return ParsedData(**pruned_parsed, **metadata)

    @staticmethod
    def read_appointments_report(appointments_sheet: pd.DataFrame) -> dict[str, Union[str, Optional[bool]]]:
        data_start_row = 7
        location_columns = [11, 12, 13]
        locations = appointments_sheet.rename(columns=appointments_sheet.iloc[0]).iloc[data_start_row:, location_columns].fillna("").drop_duplicates()

        # filter out empty columns:
        locations = locations.replace("", pd.NA).dropna(axis=1)

        location_name = " "  # UK/National has a blank logo
        has_children: Optional[bool] = False
        multi_index = pd.MultiIndex.from_frame(locations).levels
        for i, level in enumerate(multi_index):
            if len(level) != 1:
                break
            location_name = level[0]
            has_children = len(multi_index[i + 1]) > 0 if i + 1 < len(multi_index) else None

        return dict(location_name=location_name, has_children=has_children)

    def _parse_reports(self, compliance_sheets: Optional[dict[str, pd.DataFrame]] = None, training_sheets: Optional[dict[str, pd.DataFrame]] = None) -> ReportsData:
        self.logger.info("Parsed data keys:")
        self.logger.info(self.parsed_data.keys())
        self.logger.info((self.parsed_data.get("Compliance", {})).keys())
        self.logger.info((self.parsed_data.get("Training", {})).keys())
        compliance_sheets = compliance_sheets or self.parsed_data["Compliance"]
        training_sheets = training_sheets or self.parsed_data["Training"]

        assistant_versions = {}
        data_date = {}
        # Compliance Report parsing:
        compliance_notes_df = compliance_sheets["Report Notes"]
        compliance_summary_df = compliance_sheets["Summary"]
        compliance_overdue_values = compliance_summary_df[[0, 10]].dropna()
        compliance_total_values = compliance_summary_df[[0, 4]].dropna()

        # Training Report parsing:
        training_summary_df = training_sheets["Summary"]
        training_notes_df = training_sheets["Notes"]

        # Values from Compliance Assistant Report
        data_date["compliance"] = xlsx.datetime_from_excel(cell(compliance_notes_df, (4, 2), return_float=True)).isoformat()

        assistant_versions["compliance"] = cell(compliance_notes_df, (0, 17), convert_float=True)
        if assistant_versions["compliance"] < 6065:
            offset = 1
        else:
            # Mod 4 removed in CA versions 6065 and above
            offset = 0

        coords_plp = (offset + 6, 1)
        coords_wb_l = (offset + 7, 1)
        coords_wb_m = (offset + 8, 1)
        coords_fa = (offset + 9, 1)
        coords_sa = (offset + 10, 1)
        coords_sf = (offset + 11, 1)

        overdue_full_roles = cell(compliance_overdue_values, (0, 1))  # Overdue Full role
        overdue_getting_started_standard = cell(compliance_overdue_values, (4, 1))  # Overdue M01 (Getting Started)
        overdue_personal_learning_plan = cell(compliance_overdue_values, coords_plp)  # Overdue M02 (Personal Learning Plan)
        overdue_tools_for_the_role_leaders = cell(compliance_overdue_values, (5, 1))  # Overdue M03 (Tools for the Role - Leaders)
        overdue_woodbadge_leader = cell(compliance_overdue_values, coords_wb_l)  # Overdue Section Woodbadge
        overdue_woodbadge_manager = cell(compliance_overdue_values, coords_wb_m)  # Overdue Manager Woodbadge
        overdue_first_aid = cell(compliance_overdue_values, coords_fa)  # Overdue First Aid MOL
        overdue_safety = cell(compliance_overdue_values, coords_sa)  # Overdue Safety MOL
        overdue_safeguarding = cell(compliance_overdue_values, coords_sf)  # Overdue Safeguarding MOL

        total_adults = cell(compliance_total_values, (0, 1))  # Total Adults in report
        total_roles = cell(compliance_total_values, (1, 1))  # Total Roles in report

        # Values from Training Assistant Report
        data_date["training"] = xlsx.datetime_from_excel(cell(training_notes_df, (3, 4), return_float=True)).isoformat()
        assistant_versions["training"] = cell(training_notes_df, (0, 31), convert_float=True)
        if assistant_versions["training"] < 1029:
            training_overdue_values = training_summary_df[[0, 3]].dropna()
        else:
            training_overdue_values = training_summary_df[[0, 5]].dropna()

        overdue_getting_started_trustee = cell(training_overdue_values, (2, 1))  # Overdue M01EX (Getting Started for Trustees)
        overdue_gdpr = cell(training_overdue_values, (3, 1))  # Overdue GDPR
        overdue_tools_for_the_role_managers = cell(training_overdue_values, (7, 1))  # Overdue M04 (Tools for the Role - Managers)

        # Clean up
        overdue_getting_started = overdue_getting_started_standard + overdue_getting_started_trustee
        overdue_tools_for_the_role = overdue_tools_for_the_role_leaders + overdue_tools_for_the_role_managers
        overdue_woodbadge = overdue_woodbadge_leader + overdue_woodbadge_manager

        target_val = int(10 ** round(math.log(total_roles) / 2 - 2, 0)) if total_roles >= 150 else 1

        return ReportsData(
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
            assistant_versions=ReportsAssistantVersions(**assistant_versions),
            data_date=ReportsDataDate(**data_date),
        )

    @staticmethod
    def save_trends(trend_props: dict[str, Any]) -> None:
        trends_path = config.DOWNLOAD_DIR / "trends.feather"
        try:
            trends = pd.read_feather(trends_path)
        except (FileNotFoundError, pyarrow.lib.ArrowInvalid):
            trends = pd.DataFrame(columns=['Location', 'Include Descendents', 'Date', 'JSON'])

        trend_props["JSON"] = json.dumps(trend_props["JSON"])
        idx_cols = [k for k in trend_props if k != "JSON"]
        new_trends = trends.append(trend_props, ignore_index=True).drop_duplicates(subset=idx_cols)  # can't drop_duplicates with non-hashable
        if not trends.equals(new_trends):  # Only save if changed
            new_trends.to_feather(trends_path)


class ReportProcessor(ReportBase):
    def __init__(self, app: dash.Dash, b64data: str, cache: cache_int.CacheInterface):
        super().__init__(cache=cache, app=app, session_id=True)
        self.check_cache = True

        self.b64data = b64data
        self.hash_string = utility.str_from_hash(int(hashlib.sha256(b64data.encode()).hexdigest(), 16))

    def parse_data(self, name: str) -> None:
        keys = self.cache.get_dict_from_partial("b64_cache", self.hash_string)
        if keys and self.check_cache:
            sheet = next(iter(keys.keys()))
            self.cache.set_to_cache("session_cache", self.session_id, "processed_workbooks", sheet, value=self.hash_string)
            return

        now = time.strftime("%H%M%S")[1:-1]
        filename = config.UPLOAD_DIR / f"{self.session_id}#{now}-{name}"

        data = base64.b64decode(self.b64data.split(",")[1])
        self.run_thread(lambda_func=lambda: filename.write_bytes(data))
        self.run_thread(lambda_func=lambda: self.process_uploaded_data(filename))

    def process_uploaded_data(self, filename: Path) -> None:
        # atomic operations and thread safe
        # https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe

        workbooks_data = utility.read_workbooks([self.b64data], self.app, self.cache, excluded_worksheets=["Report", "Subtotal"], session_id=self.session_id)

        for workbook_name, workbook_data in workbooks_data.items():
            sheets = {}
            for sheet_name, sheet_data in workbook_data.items():
                sheet_data.columns = sheet_data.columns.astype(str)  # Convert col names to string for feather. #TODO .astype("string")
                for col, dtype in sheet_data.dtypes.to_dict().items():  # convert mixed-type object columns to str
                    if dtype == "object":
                        sheet_data[col] = sheet_data[col].fillna(pd.NA).astype(str)

                cache_filename = filename.with_suffix(f".{workbook_name}.{sheet_name}.feather")
                # noinspection PyTypeChecker
                sheet_data.to_feather(cache_filename)
                sheets[sheet_name] = str(cache_filename)

            # Mark workbook as processed:
            self.cache.set_to_cache("session_cache", self.session_id, "processed_workbooks", workbook_name, value=self.hash_string)
            self.cache.set_to_cache("b64_cache", self.hash_string, workbook_name, value=sheets)


def cell(frame: pd.DataFrame, coordinate: tuple[int, int], return_float: bool = False, convert_float: bool = False) -> Union[float, int]:
    y = coordinate[0]
    x = coordinate[1]
    val = frame.iat[y, x]
    if return_float:
        return float(val)
    return int(float(val) if convert_float else val)


class ReportsDataDate(pydantic.BaseModel):
    compliance: Optional[str]
    training: Optional[str]


class ReportsAssistantVersions(pydantic.BaseModel):
    compliance: Optional[Union[float, int]]
    training: Optional[Union[float, int]]


class ReportsDataCore(pydantic.BaseModel):
    appropriate_roles: Union[float, int]
    getting_started_1: Union[float, int]
    getting_started_2: Union[float, int]
    getting_started_3_4: Union[float, int]
    gdpr: Union[float, int]
    managing_safety: Union[float, int]
    safe_spaces: Union[float, int]
    preparedness: Union[float, int]
    knowledge: Union[float, int]
    total_adults: Union[float, int]
    total_roles: Union[float, int]
    target_value: Union[float, int]


class ReportsData(ReportsDataCore):
    assistant_versions: ReportsAssistantVersions
    data_date: ReportsDataDate


class ParsedData(ReportsDataCore):
    data_date: Optional[str]
    RL: str
    has_children: bool
