from typing import Tuple

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback
from flask_login import login_user

from apps.db_model.models import User
from apps.common.utils import check_password

login_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Location(id="url_login"),
                                html.H5("Welcome to login page"),
                                dcc.Input(
                                    placeholder="Enter Username",
                                    type="text",
                                    id="user_name",
                                    required="REQUIRED",
                                ),
                                dcc.Input(
                                    placeholder="Enter Password",
                                    type="password",
                                    id="user_password",
                                    required="REQUIRED",
                                ),
                                dbc.Button(
                                    "Sign In",
                                    id="login_submit",
                                    n_clicks=0,
                                    color="primary",
                                    size="lm",
                                    className="me-1",
                                ),
                                html.Div(
                                    children="",
                                    id="login_output_status",
                                    className="logerror_message",
                                ),
                            ],
                            width={"size": 8},
                        ),
                    ],
                    align="center",
                    justify="center",
                )
            ]
        )
    ],
    className="auth_design container_header",
)


@callback(
    [Output("url_login", "pathname"), Output("login_output_status", "children")],
    [Input("login_submit", "n_clicks")],
    [State("user_name", "value"), State("user_password", "value")],
    prevent_initial_call=True,
)
def login_validation(
    login_submit: str, user_name: str, user_password: str
) -> Tuple[str]:
    """_check login user and password validation_

    Args:
        login_submit (_post_): _submit the form by post method_
        user_name (_text_): _get the user name_
        user_password (_password_): _get the user password_

    Returns:
        _url_: _send the url to the browser_
        _text_: _user auth error status_
    """
    if user_name and user_password:
        try:
            if user_check := User.select().where(User.username == user_name).first():
                if check_password(user_password, user_check.password.encode("utf-8")):
                    login_user(user_check)
                    return "/dashboard", ""
                else:
                    return "/", "User password is incorrect"
            else:
                return "/", "Username is incorrect"
        except Exception as err:
            print(f" the user authentication error: {err}")
    else:
        return "/", "Enter username and password"
