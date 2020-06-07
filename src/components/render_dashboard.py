from __future__ import annotations
import base64
import json
from urllib import parse

import dateutil.parser

import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import pyarrow

import src.config as config
from src.components.navbar import Navbar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash import Dash


class DashbordGenerator:
    def __init__(self, app):
        self.report_name: str = ""
        self.data_date: str = ""
        self.report_location: str = ""
        self.num_adults: int = 0
        self.num_roles: int = 0
        self.component_list: list = []
        self.compliance_components: list = []
        self.app: Dash = app

    def _set_info(self, report_name: str, data_date: str, report_location: str):
        self.report_name = report_name
        self.data_date = dateutil.parser.parse(data_date).strftime("%B %Y")
        self.report_location = report_location

    def _set_people(self, num_adults: int, num_roles: int):
        self.num_adults = num_adults
        self.num_roles = num_roles

    def _asset_path(self, asset_file: str):
        return self.app.get_asset_url(asset_file)

    def _set_components(self, trend_keys: dict, **kwargs):
        try:
            trends_df = pd.read_feather(config.DOWNLOAD_DIR / "trends.feather").set_index(["Location", "Include Descendents", "Date"])
        except (FileNotFoundError, pyarrow.lib.ArrowInvalid):
            trend_dict = {}
        else:
            valid_periods = trends_df.xs([trend_keys["location"], trend_keys["children"]])
            prior_periods = valid_periods.loc[valid_periods.index < pd.to_datetime(trend_keys["date"]), "JSON"]
            trend_period = prior_periods.iloc[0]  # TODO implement time-based getting instead of first entry before period
            trend_date = prior_periods.index[0]
            trend_dict = json.loads(trend_period)

        target_value = kwargs.pop("TV")
        components_properties = {k[:2]: [] for k in kwargs.keys()}
        for full_key, v in kwargs.items():
            prev_trend_val = trend_dict[full_key]
            key = full_key[:2]
            label = None

            if key not in ["WB", "GS"]:
                target = target_value
            elif key == "WB":
                target = target_value / 2  # Custom target value for woodbadges
            elif key == "GS":
                target = target_value
                label = f"Module {'/'.join(full_key[2:])}"
            else:
                target = target_value

            aim = 0
            actual = v
            compliant = v <= target_value
            trend_up = v <= prev_trend_val

            if key == "AA":
                aim = "100%"  # Render with percent sign
                target = "98.5%"
                actual = f"{v:.1f}%"
                compliant = v >= 98.5  # Custom target value for disclosures
                trend_up = v >= prev_trend_val

            components_properties[key].append(dict(
                aim=aim,
                target=target,
                actual=actual,
                compliant=compliant,
                trend_up=trend_up,
                label=label,
            ))

        components = pd.read_csv(config.DATA_ROOT / "compliance-components.csv", index_col=0)
        props_series = pd.Series(components_properties)
        components = components.merge(props_series.rename("Properties"), left_index=True, right_index=True)

        self.compliance_components = [self._create_component(c['Subheads'], c['Descriptions'], c['Colours'], c["Properties"]) for c in components.to_dict('records')]

    def _create_component(self, head: str, desc: str, colour: str, component_properties: list):
        component_stats = []
        num_props = len(component_properties)
        class_name = "component-stats component-stats-1" if num_props <= 2 else "component-stats component-stats-3"
        for target_props in component_properties:
            trend = "happy" if target_props["trend_up"] else "sad"
            target_props["status"] = "compliant" if target_props["compliant"] else "non-compliant"

            component_stats.append(html.Div([
                html.Span(target_props["label"], className="component-label") if target_props.get("label") else None,
                html.Div([
                    html.Span(f"Aim: {target_props['aim']} (T {target_props['target']})", className="component-aim-text")
                ], className="component-aim"),
                html.Div([
                    html.Span(f"Actual: {target_props['actual']}", className="component-actual-text"),
                    html.Img(src=self._asset_path(f"{trend}.svg"), className="trend-svg"),
                ], className=f"component-actual {target_props['status']}")
            ], className=class_name))

        return html.Div([
            html.Div([
                html.H4(f"{head}", className="component-header"),
                html.Span(f"{desc}", className="component-description"),
            ], className="component-summary"),
            *component_stats
        ], className=f"component-info {colour}")

    def _setup_dashboard(self, params):
        data_date = params.pop("DD")
        total_adults = params.pop("TA")
        total_roles = params.pop("TR")
        report_title = params.pop("RT")
        report_location = params.pop("RL")
        self._set_info(report_name=report_title, data_date=data_date, report_location=report_location)
        self._set_people(num_adults=total_adults, num_roles=total_roles)
        trends_keys = dict(location=report_location, children=True, date=data_date)  # TODO data date needs to be before
        self._set_components(trends_keys, **params)

    def _generate_dashboard(self):
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
                    html.Img(src=self._asset_path("scout-logo-purple-stack.png"), className="logo-image"),
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
    def get_dashboard(self, query):
        if not query:
            return html.Div([
                Navbar(self.app),
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
        param_dict = {k: v for k, v in parse.parse_qsl(base64.urlsafe_b64decode(param_string.encode()).decode("UTF8"))}
        for k, v in param_dict.items():
            try:
                param_dict[k] = int(v) if "." not in v else float(v)
            except ValueError:
                param_dict[k] = v if v else None

        self._setup_dashboard(param_dict)

        return html.Div([
            Navbar(self.app, download=True),
            self._generate_dashboard(),
            html.Div(id="download-popup", className="popup", style={"display": "none"})
        ], className="page")
