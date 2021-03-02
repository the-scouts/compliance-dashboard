from collections.abc import Callable
import functools

from flask import session

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

from src.config import password
from src.config import user

from typing import Any, Optional, TypeVar, Union

users = {user: password}

# https://mypy.readthedocs.io/en/stable/generics.html#declaring-decorators
F = TypeVar('F', bound=Callable[..., Any])


def authenticate_user(credentials: tuple[Optional[str], Optional[str]]) -> bool:
    """
    generic authentication function
    returns True if user is correct and False otherwise
    """

    # replace with your code
    username = credentials[0]
    pw = credentials[1]
    authed = (username in users) and (pw == users[username])

    return authed


def validate_login_session(f: F) -> Union[F, html.Div]:
    """
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session.
    If not, returns an error with link to the login page
    """
    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Union[F, html.Div]:
        # return f(*args, **kwargs)
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
def login_layout() -> html.Div:
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


def setup_callbacks(app: dash.Dash) -> None:
    # authenticate
    @app.callback(
        [Output("login-url", "pathname"),
         Output("login-alert", "children")],
        [Input("login-button", "n_clicks")],
        [State("login-username", "value"),
         State("login-password", "value"),
         State("old-url", "data"), ],
        prevent_initial_call=True)
    def login_auth(_: int, username: Optional[str], pw: Optional[str], pathname: str) -> Union[tuple[dash.no_update, html.Div], tuple[str, str]]:
        """
        check credentials
        if correct, authenticate the session
        otherwise, authenticate the session and send user to login
        """
        if pathname == "/login":
            pathname = "/home"

        credentials = (username, pw)
        if credentials == (None, None):
            return dash.no_update, dash.no_update

        if authenticate_user(credentials):
            session["authed"] = True
            return pathname, ""
        session["authed"] = False
        return dash.no_update, html.Div("Incorrect credentials.", className="auth-alert")
