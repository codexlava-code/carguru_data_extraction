from typing import Tuple, List, Optional

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input, State, no_update
from flask_login import login_user

from app import app
from apps.db_model.models import User
from apps.common.utils import check_password
from apps.back_end.utils.notification_callback import notify_message

home_layout = html.Div(
    [
        # check user logged in or not
        dcc.Location(
            id="user_login_success", refresh=True
            ),
        # transfer the callback output path
        dcc.Location(
            id="url_login_home", refresh=True
            ),
        html.Div(
            [
                dbc.Container(
                    [
                        html.A(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Img(
                                            src=app.get_asset_url("images/logo.svg"),
                                            height="30px",
                                        )
                                    ),
                                ]
                            ),
                            href="/",
                        ),
                    ]
                ),
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H2(
                                            "Welcome to BOBST Manchester LTD machine diagnosis and analytics tools"
                                        ),
                                        html.P(
                                            "Online diagnosis and data analysis tool of managing, analysing, visualising,\
                                               and monitoring dataset from various sensors."
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ]
                )
            ], className="home_header"
        ),
        html.Div(
            [
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            placeholder="Enter Username",
                                            type="text",
                                            id="user_name",
                                            required="REQUIRED",
                                        ),
                                        dbc.Input(
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
                                            id="output_state_home",
                                            className="logerror_message",
                                        ),
                                    ],
                                    width={"size": 6,"offset": 3},
                                ),
                            ]
                        )
                    ]
                )
            ],
            className="home_login",
        ),
        html.Footer(
            [
                dbc.Container(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.P(
                                            "© 2023 Cockpit. All rights reserved BOBST Manchester LTD."
                                        )
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            className="home_footer",
        )
    ],
    className="content_home",
)


@callback(
    [
        Output("url_login_home", "pathname"),
        Output("output_state_home", "children")
        ],
    [
        Input("login_submit", "n_clicks")
        ],
    [
        State("user_name", "value"),
        State("user_password", "value")
        ],
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
            _url_: _send the url_
            _text_: _user auth error status_
    """
    if (user_name and user_password) is not None:
        try:
            if user_check := User.select().where(User.username == user_name).first():
                if check_password(user_password, user_check.password.encode("utf-8")):
                    login_user(user_check)
                    return "/dashboard", no_update
                else:
                    return "/", "Password is incorrect"
            else:
                return "/", "Username is incorrect"
        except Exception as err:
            print(f"authentication error: {err}")
            message = "authentication error" + str(err)
            notify_message(message)
    else:
        return "/", "Please input username and password"
