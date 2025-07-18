from typing import List, Tuple

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback, ctx

from apps.db_model.User import create_user, view_user, delete_user
from apps.back_end.utils.notification_callback import notify_message

register_layout = html.Div(
    [
        dcc.Location(id="register_url_path", refresh=True),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label("User name", html_for="user_name"),
                                        dbc.Input(
                                            type="text",
                                            id="user_name",
                                            placeholder="User name",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label("Password", html_for="user_password"),
                                        dbc.Input(
                                            type="password",
                                            id="user_password",
                                            placeholder="Password",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label("Email", html_for="user_email"),
                                        dbc.Input(
                                            type="email",
                                            id="user_email",
                                            placeholder="Email",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                        dbc.FormFeedback(
                                            "That looks like a bobst email :-)",
                                            type="valid",
                                        ),
                                        dbc.FormFeedback(
                                            "Sorry, we only accept bobst email...",
                                            type="invalid",
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width=4,
                        ),
                    ],
                    align="center",
                    justify="center",
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Register user",
                                    id="register_submit",
                                    n_clicks=0,
                                    value="register_submit",
                                    color="success",
                                    size="lg",
                                    className="me-1",
                                ),
                            ],
                            width={"size": 6, "offset": 3},
                        ),
                    ],
                    align="center",
                    justify="center",
                ),
            ]
        ),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    id="register_list_table", className="table_list"
                                ),
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ],
    className="form_section container_header",
)


@callback(
    [
        Output("register_list_table", "children"),
    ],
    [Input("register_url_path", "pathname")],
)
def machine_list(url_path: str) -> List:
    if url_path == "/register":
        user_list = view_user()
        return [
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Id"),
                                html.Th("Username"),
                                html.Th("Email"),
                                html.Th("Action"),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(idx + 1),
                                    html.Td(item.username),
                                    html.Td(item.email),
                                    html.Td(
                                        [
                                            html.A(
                                                "Delete",
                                                href="#{}".format(item.username),
                                            )
                                        ]
                                    ),
                                ]
                            )
                            for idx, item in enumerate(user_list)
                        ]
                    ),
                ],
                dark=True,
                hover=True,
                responsive=True,
                color="light",
                className="form_list",
            )
        ]
    return [None]


@callback(
    [
        Output("register_url_path", "pathname", allow_duplicate=True),
    ],
    [Input("register_url_path", "hash")],
    prevent_initial_call=True,
)
def user_delete(hash: str) -> List:
    if hash is None:
        raise Exception("you haven't submitted")
    else:
        delete_user(hash[1:])
    return ["/register"]


@callback(
    [
        Output("register_url_path", "pathname"),
        Output("user_email", "valid"),
        Output("user_email", "invalid"),
    ],
    [Input("register_submit", "n_clicks")],
    [
        State("user_name", "value"),
        State("user_password", "value"),
        State("user_email", "value"),
    ],
    prevent_initial_call=True,
)
def register_user(*user_info) -> Tuple[str, bool]:
    """_register new users_

    Args:
        user_info (_list_): _user info setup_

    Returns:
        _string_: _return to the home page_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    if "register_submit" not in triggered_value:
        raise Exception("you haven't submitted the form")

    if user_info[1:3] is None:
        print(user_info)
        notify_message("Please write all the input field")
    else:
        is_email = user_info[3].endswith("@bobst.com")
        if is_email:
            create_user(user_info)
            notify_message("User information registered")
    return "/register", is_email, not is_email
