import dash_html_components as html
import pandas as pd
from page_components.navbar import Navbar, Navbar2
from app import app


def compliance_component(head: str, desc: str, aim, target, actual, compliant: bool, colour: str):
    status = "compliant" if compliant else "non-compliant"

    return html.Div([
        html.Div([
            html.H4(f"{head}", className="component-header"),
            html.Span(f"{desc}", className="component-description"),
        ], className="component-summary"),
        html.Div([
            html.Div([
                html.Span(f"Aim: {aim} (T {target})", className="component-aim-text")
            ], className="component-aim"),
            html.Div([
                html.Span(f"Actual: {actual}", className="component-actual-text")
            ], className=f"component-actual {status}")
        ], className="component-stats")
    ], className=f"component-info {colour}")


def create_compliance_components():
    components: pd.DataFrame = pd.read_csv("./data/compliance-components.csv")
    return [compliance_component(c['Subheads'], c['Descriptions'],  0, 10, 5, True, c['Colours']) for c in components.to_dict('records')]


class DashbordGenerator:
    def __init__(self):
        self.report_name: str = ""
        self.data_date: str = ""
        self.report_location: str = ""
        self.num_adults: int = 0
        self.num_roles: int = 0
        self.component_list: list = []

        self.compliance_components: list = create_compliance_components()

    def set_info(self, report_name: str, data_date: str, report_location: str):
        self.report_name = report_name
        self.data_date = data_date
        self.report_location = report_location

    def set_people(self, num_adults: int, num_roles: int):
        self.num_adults = num_adults
        self.num_roles = num_roles

    def generate_dashboard(self):
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
        ], className="report-container")

    def get_dashboard(self):
        return html.Div([
            Navbar(),
            self.generate_dashboard()
        ], className="reports-page")
