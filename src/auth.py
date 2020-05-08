from functools import wraps
from flask import session
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
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
    password = credentials[1]
    authed = (username in users) and (password == users[username])

    return authed


def validate_login_session(f):
    """
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session.
    If not, returns an error with link to the login page
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('authed'):
            return f(*args, **kwargs)
        return html.Div(
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        html.H2('401 - Unauthorized', className='card-title'),
                        html.A(dcc.Link('Login', href='/login'))
                    ], body=True)
                ], width=5),
            ], justify='center')
        )

    return wrapper


# login layout content
def login_layout():
    return html.Div([
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        html.H4('Login', className='card-title'),
                        dbc.Input(id='login-username', placeholder='User'),
                        dbc.Input(id='login-password', placeholder='Assigned password', type='password'),
                        dbc.Button('Submit', id='login-button', color='success', block=True),
                        html.Br(),
                        html.Div(id='login-alert')
                        ], body=True),
                    width=6),
                justify='center')
            ])
        ])


def setup_auth_callbacks(app: dash.Dash):
    # authenticate
    @app.callback(
        [Output('login-url', 'pathname'),
         Output('login-alert', 'children')],
        [Input('login-button', 'n_clicks')],
        [State('login-username', 'value'),
         State('login-password', 'value')],
        prevent_initial_call=True)
    def login_auth(_, username, pw):
        """
        check credentials
        if correct, authenticate the session
        otherwise, authenticate the session and send user to login
        """
        credentials = (username, pw)
        if authenticate_user(credentials):
            session['authed'] = True
            return '/home', ''
        session['authed'] = False
        return dash.no_update, dbc.Alert('Incorrect credentials.', color='danger', dismissable=True)

    # # logout
    # @app.callback(Output('url', 'pathname'),
    #               [Input('logout-button', 'n_clicks'), ],
    #               prevent_initial_call=True)
    # def logout_(_):
    #     """clear the session and send user to login"""
    #     session['authed'] = False
    #     return '/login'
