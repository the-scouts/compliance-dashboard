import uuid
from functools import wraps

from flask import session
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from src.config import user, password


users = {
    user: password
}


def authenticate_user(credentials):
    """
    generic authentication function
    returns True if user is correct and False otherwise
    """

    # replace with your code
    username = credentials[0]
    pw = credentials[1]
    authed = (username in users) and (pw == users[username])

    return authed


def validate_login_session(f):
    """
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session.
    If not, returns an error with link to the login page
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("authed"):
            return f(*args, **kwargs)
        return html.Div(
            html.Div([
                html.H3(dcc.Link("Please Log In", href="/login")),
                html.H4("login not found (unauthorised)"),
            ], className="page-container vertical-center static-container"),
            className="page"
        )

    return wrapper


# login layout content
def login_layout():
    return html.Div(
        html.Div([
            html.H4("Login"),
            dcc.Input(id="login-username", placeholder="Username", type="text"),
            dcc.Input(id="login-password", placeholder="Password", type="password"),
            html.Button("Submit", id="login-button", className="green"),
            html.Br(),
            html.Div(id="login-alert")
        ], className="page-container vertical-center static-container auth"),
        className="page"
    )


def setup_auth_callbacks(app: dash.Dash):
    # authenticate
    @app.callback(
        [Output("login-url", "pathname"),
         Output("login-alert", "children")],
        [Input("login-button", "n_clicks")],
        [State("login-username", "value"),
         State("login-password", "value"),
         State("old-url", "data"), ],
        prevent_initial_call=True)
    def login_auth(_, username, pw, pathname):
        """
        check credentials
        if correct, authenticate the session
        otherwise, authenticate the session and send user to login
        """
        if pathname == "/login":
            pathname = "/home"

        credentials = (username, pw)
        if credentials.count(None) == len(credentials):
            return dash.no_update, dash.no_update

        if authenticate_user(credentials):
            session["authed"] = True
            session["uid"] = uuid.uuid4().hex[:8]
            return pathname, ""
        session["authed"] = False
        return dash.no_update, html.Div("Incorrect credentials.", className="auth-alert")
