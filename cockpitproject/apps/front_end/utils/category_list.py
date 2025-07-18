from typing import List

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback, ctx

from apps.db_model.category import (
    create_category,
    view_category,
    delete_category,
)
from apps.back_end.utils.notification_callback import notify_message

category_layout = html.Div(
    [
        dcc.Location(id="category_list_path", refresh=True),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Category name", html_for="category_name"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="category_name",
                                            placeholder="Category name",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width={"size": 6, "offset": 3},
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Create category",
                                    id="category_submit",
                                    n_clicks=0,
                                    value="category_submit",
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
                            [html.Div(id="category_list_table", className="table_list")]
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
        Output("category_list_table", "children"),
    ],
    [Input("category_list_path", "pathname")],
)
def category_list(url_path: str) -> List:
    if url_path == "/category":
        category_list = view_category()
        return [
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Id"),
                                html.Th("category name"),
                                html.Th("Actions"),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(idx + 1),
                                    html.Td(item.name),
                                    html.Td(
                                        [html.A("Delete", href="#{}".format(item.name))]
                                    ),
                                ]
                            )
                            for idx, item in enumerate(category_list)
                        ],
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
    [Output("category_list_path", "pathname", allow_duplicate=True)],
    [Input("category_list_path", "hash")],
    prevent_initial_call=True,
)
def category_delete(hash: str) -> List:
    if hash is None:
        raise Exception("you haven't submitted")
    else:
        delete_category(hash[1:])
    return ["/category"]


@callback(
    [
        Output("category_list_path", "pathname"),
    ],
    [
        Input("category_submit", "n_clicks"),
    ],
    [
        State("category_name", "value"),
    ],
    prevent_initial_call=True,
)
def category_register(*category_info: List) -> List:
    """_register new category_

    Args:
        category_info (_list_): _category information_
    Returns:
        _list_: _return empty list_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    if "category_submit" not in triggered_value:
        raise Exception("you haven't submitted the form")

    if category_info[1] is not None:
        category = category_info[1].upper()
        create_category(category)
        notify_message("category information registered")
    else:
        notify_message("Please write all the information")

    return ["/category"]
