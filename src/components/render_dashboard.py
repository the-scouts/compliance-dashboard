import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from src.components.navbar import Navbar
from urllib import parse
import base64

# Type hints:
from dash import Dash


def compliance_component(head: str, desc: str, colour: str, component_properties: list):
    component_stats = []
    num_props = len(component_properties)
    class_name = "component-stats component-stats-1" if num_props <= 2 else "component-stats component-stats-3"
    for target_props in component_properties:
        target_props["status"] = "compliant" if target_props["compliant"] else "non-compliant"
        component_stats.append(html.Div([
            html.Div([
                html.Span(f"Aim: {target_props['aim']} (T {target_props['target']})", className="component-aim-text")
            ], className="component-aim"),
            html.Div([
                html.Span(f"Actual: {target_props['actual']}", className="component-actual-text")
            ], className=f"component-actual {target_props['status']}")
        ], className=class_name))

    return html.Div([
        html.Div([
            html.H4(f"{head}", className="component-header"),
            html.Span(f"{desc}", className="component-description"),
        ], className="component-summary"),
        *component_stats
    ], className=f"component-info {colour}")


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
        self.data_date = data_date
        self.report_location = report_location

    def _set_people(self, num_adults: int, num_roles: int):
        self.num_adults = num_adults
        self.num_roles = num_roles

    def _set_components(self, **kwargs):
        target_value = kwargs.pop("TV")
        components_properties = {k[:2]: [] for k in kwargs.keys()}
        for k, v in kwargs.items():
            key = k[:2]
            if k == "AA":
                aim = "100%"  # Render with percent sign
                target = "98.5%"
                actual = f"{v:.1f}%"
                compliant = v >= 98.5  # Custom target value for disclosures

            elif k == "WB":
                target = target_value / 2  # Custom target value for woodbadges
                aim = 0
                actual = v
                compliant = v <= target
            else:
                target = target_value
                aim = 0
                actual = v
                compliant = v <= target_value

            components_properties[key].append(dict(
                aim=aim,
                target=target,
                actual=actual,
                compliant=compliant
            ))

        components = pd.read_csv("./data/compliance-components.csv", index_col=0)
        props_series = pd.Series(components_properties)
        components = components.merge(props_series.rename("Properties"), left_index=True, right_index=True)
        self.compliance_components = [compliance_component(c['Subheads'], c['Descriptions'],  c['Colours'], c["Properties"]) for c in components.to_dict('records')]

    def _setup_dashboard(self, params):
        data_date = params.pop("DD")
        total_adults = params.pop("TA")
        total_roles = params.pop("TR")
        report_title = params.pop("RT")
        report_location = params.pop("RL")
        self._set_info(report_name=report_title, data_date=data_date, report_location=report_location)
        self._set_people(num_adults=total_adults, num_roles=total_roles)
        self._set_components(**params)

    def _generate_dashboard(self, app: Dash):
        if not (self.report_name and self.data_date and self.report_location and self.num_adults and self.num_roles):
            raise AttributeError("Make sure all values are set before calling generate(). Have you called set_info and set_people?")

        return html.Div([
            html.Div([
                html.H3(f"The Basics Dashboard – {self.report_name}", className="report-title"),
                html.Div([
                    html.Span(f"Data: {self.data_date}", className="legend-text"), html.Br(),
                    html.Span("Getting better", className="legend-text"), html.Br(),
                    html.Span("Getting worse", className="legend-text")
                ], className="legend"),
                html.Div([
                    html.Img(src=app.get_asset_url("scout-logo-purple-stack.png"), className="logo-image"),
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

        param_string = parse.parse_qsl(query)[0][1].encode()
        param_dict = dict(parse.parse_qsl(base64.urlsafe_b64decode(param_string).decode("UTF8")))
        for k, v in param_dict.items():
            try:
                param_dict[k] = int(v) if "." not in v else float(v)
            except ValueError:
                param_dict[k] = v if v else None

        self._setup_dashboard(param_dict)

        return html.Div([
            Navbar(self.app, download=True),
            self._generate_dashboard(self.app),
            html.Div(id="download-popup", className="popup", style={"display": "none"})
        ], className="page")
