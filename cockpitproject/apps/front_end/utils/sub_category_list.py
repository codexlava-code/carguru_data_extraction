from typing import List

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback, ctx

from apps.db_model.sub_category import (
    create_sub_category,
    view_sub_category,
    delete_sub_category,
)
from apps.db_model.category import view_category
from apps.back_end.utils.notification_callback import notify_message

sub_category_layout = html.Div(
    [
        dcc.Location(id="sub_category_list_path", refresh=True),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "category name", html_for="choose_category_name"
                                        ),
                                        dcc.Dropdown(
                                            id="choose_category_name",
                                            className="dropdown",
                                            options=[
                                                {"label": category.name, "value": category.id}
                                                for category in view_category()
                                                ],
                                            clearable=True,
                                            placeholder="Select Categories",
                                        ),
                                    ],
                                    className="form_input",
                                ),
                            ],
                            width={"size": 4},
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Sub category name", html_for="sub_category_name"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="sub_category_name",
                                            placeholder="Sub category name",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width={"size": 4},
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Sub category Variable Name", html_for="sub_category_variable_name"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="sub_category_variable_name",
                                            placeholder="Sub category Variable name",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width={"size": 4},
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Unit", html_for="sub_category_unit"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="sub_category_unit",
                                            placeholder="Sub category unit",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                ),
                            ],
                            width={"size": 4},
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Minimum limit", html_for="sub_category_mini_limit"
                                        ),
                                        dbc.Input(
                                            type="number",
                                            id="sub_category_mini_limit",
                                            placeholder="Sub category minimum limit",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width={"size": 4},
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Maximum limit", html_for="sub_category_maxi_limit"
                                        ),
                                        dbc.Input(
                                            type="number",
                                            id="sub_category_maxi_limit",
                                            placeholder="Sub category maximum limit",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width={"size": 4},
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Create sub category",
                                    id="sub_category_submit",
                                    n_clicks=0,
                                    value="sub_category_submit",
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
                            [html.Div(id="sub_category_list_table", className="table_list")]
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
        Output("sub_category_list_table", "children"),
    ],
    [Input("sub_category_list_path", "pathname")],
)
def sub_category_list(url_path: str) -> List:
    if url_path == "/subcategory":
        sub_category_list = view_sub_category()
        return [
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Id"),
                                html.Th("Category name"),
                                html.Th("Sub category name"),
                                html.Th("Variable name"),
                                html.Th("Unit"),
                                html.Th("minimum"),
                                html.Th("maximum"),
                                html.Th("Actions"),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(idx + 1),
                                    html.Td(item.category_id.name),
                                    html.Td(item.name),
                                    html.Td(item.variable_name),
                                    html.Td(item.unit),
                                    html.Td(item.mini_limit),
                                    html.Td(item.maxi_limit),
                                    html.Td(
                                        [
                                            html.A(
                                                "Delete",
                                                href="#{}".format(item.variable_name)
                                                )
                                            ]
                                    ),
                                ]
                            )
                            for idx, item in enumerate(sub_category_list)
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
    [
        Output(
            "sub_category_list_path",
            "pathname",
            allow_duplicate=True
            )
        ],
    [
        Input("sub_category_list_path", "hash")
        ],
    prevent_initial_call=True,
)
def sub_category_delete(hash: str) -> List:
    if hash is None:
        raise Exception("you haven't submitted")
    else:
        delete_sub_category(hash[1:])
    return ["/subcategory"]


@callback(
    [
        Output("sub_category_list_path", "pathname"),
    ],
    [
        Input("sub_category_submit", "n_clicks"),
    ],
    [
        State("choose_category_name", "value"),
        State("sub_category_name", "value"),
        State("sub_category_variable_name", "value"),
        State("sub_category_unit", "value"),
        State("sub_category_mini_limit", "value"),
        State("sub_category_maxi_limit", "value"),
    ],
    prevent_initial_call=True,
)
def sub_category_register(*sub_category_info: List) -> List:
    """_register new sub category_

    Args:
        sub category_info (_list_): _sub category information_
    Returns:
        _list_: _return empty list_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    if "sub_category_submit" not in triggered_value:
        raise Exception("you haven't submitted the form")

    if sub_category_info[1:6] is not None:
        create_sub_category(sub_category_info)
        notify_message("sub category information registered")
    else:
        notify_message("Please write all the information")

    return ["/subcategory"]
