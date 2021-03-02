from __future__ import annotations
import base64
import json
from urllib import parse

import dateutil.parser
import pydantic

import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import pyarrow

from src.components import navbar
import src.config as config

from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from dash import Dash


class DashbordGenerator:
    def __init__(self, app: Dash):
        self.report_name: str = ""
        self.data_date: str = ""
        self.report_location: str = ""
        self.num_adults: int = 0
        self.num_roles: int = 0
        self.compliance_components: list[html.Div] = []
        self.app: Dash = app

    def _set_info(self, report_name: str, data_date: str, report_location: str) -> None:
        self.report_name = report_name
        self.data_date = dateutil.parser.parse(data_date).strftime("%B %Y")
        self.report_location = report_location

    def _set_people(self, num_adults: int, num_roles: int) -> None:
        self.num_adults = num_adults
        self.num_roles = num_roles

    def _asset_path(self, asset_file: str) -> str:
        return str(self.app.get_asset_url(asset_file))  # FIXME wrapping in str unecessary but MyPy doesn't understand Dash types. Remove when Dash type hints.

    def _set_components(self, trend_keys: dict[str, Union[str, bool]], params: ParamsModel) -> None:
        try:
            trends_df = pd.read_feather(config.DOWNLOAD_DIR / "trends.feather")
            trends_df["Date"] = pd.to_datetime(trends_df["Date"])
            trends_df = trends_df.set_index(["Location", "Include Descendents", "Date"])
        except (FileNotFoundError, pyarrow.lib.ArrowInvalid):
            trend_dict: dict[str, Union[int, float]] = {}   # TODO check int float
        else:
            valid_periods = trends_df.xs([trend_keys["location"], trend_keys["children"]])
            prior_periods = valid_periods.loc[valid_periods.index < pd.to_datetime(trend_keys["date"]), "JSON"]

            # Might be no valid trend values
            try:
                trend_period = prior_periods.iloc[0]  # TODO implement time-based getting instead of first entry before period
            except IndexError:
                trend_dict = {}   # TODO check int float
            else:
                trend_date = prior_periods.index[0]
                trend_dict_unparsed: Union[str, dict[str, Union[int, float]]] = json.loads(str(trend_period))   # TODO check double JSON FIXME shouldn't need to pass through str
                try:
                    assert isinstance(trend_dict_unparsed, str)
                    trend_dict = json.loads(trend_dict_unparsed)
                except (AssertionError, TypeError):
                    assert isinstance(trend_dict_unparsed, dict)
                    trend_dict = dict(trend_dict_unparsed)

        target_value = params.tv
        core_params = CoreParams(**params.__dict__)
        components_properties: dict[str, list[dict[str, Union[float, int, bool, str, None]]]] = {k[:2]: [] for k, _v in core_params}
        for full_key, v in core_params:
            prev_trend_val = trend_dict.get(full_key)
            key = full_key[:2]
            label = None

            if key not in ["WB", "GS"]:
                target: Union[float, int, str] = target_value
            elif key == "WB":
                target = target_value / 2  # Custom target value for woodbadges
            elif key == "GS":
                target = target_value
                label = f"Module {'/'.join(full_key[2:])}"
            else:
                target = target_value

            aim: Union[int, str] = 0
            actual: Union[float, int, str] = v
            compliant = v <= target_value
            trend_up: Optional[bool] = v <= prev_trend_val if prev_trend_val else None

            if key == "AA":
                aim = "100%"  # Render with percent sign
                target = "98.5%"
                actual = f"{v:.1f}%"
                compliant = v >= 98.5  # Custom target value for disclosures
                trend_up = v >= prev_trend_val if prev_trend_val else None

            components_properties[key].append(dict(
                aim=aim,
                target=target,
                actual=actual,
                compliant=compliant,
                trend_up=trend_up,
                label=label,
            ))

        components = pd.read_csv(config.DOWNLOAD_DIR / "compliance-components.csv", index_col=0)
        props_series = pd.Series(components_properties)
        components = components.merge(props_series.rename("Properties"), left_index=True, right_index=True)

        self.compliance_components = [self._create_component(c['Subheads'], c['Descriptions'], c['Colours'], c["Properties"]) for c in components.to_dict('records')]

    def _create_component(self, head: str, desc: str, colour: str, component_properties: list[dict[str, Any]]) -> html.Div:
        component_stats = []
        num_props = len(component_properties)
        class_name = "component-stats component-stats-1" if num_props <= 2 else "component-stats component-stats-3"
        for target_props in component_properties:
            trend = target_props["trend_up"]
            if trend is not None:
                trend = "happy" if target_props["trend_up"] else "sad"
            target_props["status"] = "compliant" if target_props["compliant"] else "non-compliant"

            component_stats.append(html.Div([
                html.Span(target_props["label"], className="component-label") if target_props.get("label") else None,
                html.Div([
                    html.Span(f"Aim: {target_props['aim']} (T {target_props['target']})", className="component-aim-text")
                ], className="component-aim"),
                html.Div([
                    html.Span(f"Actual: {target_props['actual']}", className="component-actual-text"),
                    html.Img(src=self._asset_path(f"{trend}.svg"), className="trend-svg") if trend is not None else None,
                ], className=f"component-actual {target_props['status']}")
            ], className=class_name))

        return html.Div([
            html.Div([
                html.H4(f"{head}", className="component-header"),
                html.Span(f"{desc}", className="component-description"),
            ], className="component-summary"),
            *component_stats
        ], className=f"component-info {colour}")

    def _setup_dashboard(self, params: ParamsModel) -> None:
        data_date = params.dd
        total_adults = params.ta
        total_roles = params.tr
        report_title = params.rt
        report_location = params.rl
        self._set_info(report_name=report_title, data_date=data_date, report_location=report_location)
        self._set_people(num_adults=total_adults, num_roles=total_roles)
        trends_keys: dict[str, Union[str, bool]] = dict(location=report_location, children=True, date=data_date)  # TODO data date needs to be before
        self._set_components(trends_keys, params)

    def _generate_dashboard(self) -> html.Div:
        if not (self.report_name and self.data_date and self.report_location and self.num_adults and self.num_roles):
            raise AttributeError("Make sure all values are set before calling generate(). Have you called set_info and set_people?")

        return html.Div([
            html.Div([
                html.H3(f"The Basics Dashboard – {self.report_name}", className="report-title"),
                html.Div([
                    html.Span(f"Data: {self.data_date}", className="legend-text"),
                    html.Div([
                        html.Img(src=self._asset_path("happy.svg"), className="trend-svg"),
                        html.Span("Getting better", className="legend-text"),
                    ], className="legend-entry"),
                    html.Div([
                        html.Img(src=self._asset_path("sad.svg"), className="trend-svg"),
                        html.Span("Getting worse", className="legend-text")
                    ], className="legend-entry"),
                ], className="legend"),
                html.Div([
                    html.Img(src=self._asset_path("scout-logo-stack.svg"), className="logo-image"),
                    html.Span(f"{self.report_location}", className="logo-text")
                ], className="logo")

            ], className="report-header"),
            html.Div(self.compliance_components, className="compliance-components"),
            html.Div([
                html.Span(["Remember, figures are per role not per person", html.Br(), "(makes it better but not right!)"], className="roles-reminder-text")
            ], className="roles-reminder"),
            html.Div([
                html.H3(f"{self.num_adults} Adults - {self.num_roles} Roles", className="people-stats")
            ], className="report-footer"),
        ], className="page-container vertical-center app-container", id="report-container")

    # Entry point
    def get_dashboard(self, query: str) -> html.Div:
        if not query:
            return html.Div([
                navbar.Navbar(self.app),
                html.Div([
                    html.H3("Report not found"),
                    html.H4([
                        "Please ",
                        dcc.Link("generate a new report", href="/new"),
                        " or check your URL"
                    ])
                ], className="page-container vertical-center static-container")
            ], className="page")

        param_string = parse.parse_qsl(query)[0][1]
        split = {k.lower(): v for k, v in parse.parse_qsl(base64.urlsafe_b64decode(param_string.encode()).decode("UTF8"))}
        self._setup_dashboard(ParamsModel(**split))

        return html.Div([
            navbar.Navbar(self.app, download=True),
            self._generate_dashboard(),
            html.Div(id="download-popup", className="popup", style={"display": "none"})
        ], className="page")


class CoreParams(pydantic.BaseModel):
    aa: float
    ar: Union[float, int]
    gs1: Union[float, int]
    gs2: Union[float, int]
    gs34: Union[float, int]
    dp: Union[float, int]
    sa: Union[float, int]
    sf: Union[float, int]
    fa: Union[float, int]
    wb: Union[float, int]


class ParamsModel(CoreParams):
    ta: int
    tr: int
    tv: int
    dd: str
    rt: str
    rl: str
