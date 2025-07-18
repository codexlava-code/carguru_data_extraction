from typing import List, Tuple

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, State, callback, ctx

from apps.db_model.machine import (
    create_machine,
    view_machine,
    delete_machine,
)
from apps.back_end.utils.notification_callback import notify_message

machines_layout = html.Div(
    [
        dcc.Location(id="machine_list_path", refresh=True),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        dbc.Label(
                                            "Machine name", html_for="machine_name"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="machine_name",
                                            placeholder="Machine name",
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
                                        dbc.Label(
                                            "Equipment Id", html_for="equipment_id"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="equipment_id",
                                            placeholder="Equipment Id",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                        dbc.FormFeedback(
                                            "That looks like a equipment name :-)",
                                            type="valid",
                                        ),
                                        dbc.FormFeedback(
                                            "Sorry, we only accept genv...",
                                            type="invalid",
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
                                        dbc.Label(
                                            "Company Name", html_for="company_name"
                                        ),
                                        dbc.Input(
                                            type="text",
                                            id="company_name",
                                            placeholder="Company name",
                                            required=True,
                                            autoFocus=False,
                                        ),
                                    ],
                                    className="form_input",
                                )
                            ],
                            width=4,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Button(
                                    "Create machine",
                                    id="machine_submit",
                                    n_clicks=0,
                                    value="machine_submit",
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
                            [html.Div(id="machine_list_table", className="table_list")]
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
        Output("machine_list_table", "children"),
    ],
    [Input("machine_list_path", "pathname")],
)
def machine_list(url_path: str) -> List:
    if url_path == "/machines":
        machine_list = view_machine()
        return [
            dbc.Table(
                [
                    html.Thead(
                        html.Tr(
                            [
                                html.Th("Id"),
                                html.Th("Machine name"),
                                html.Th("Equipment Id"),
                                html.Th("Company name"),
                                html.Th("Actions"),
                            ]
                        )
                    ),
                    html.Tbody(
                        [
                            html.Tr(
                                [
                                    html.Td(idx + 1),
                                    html.Td(item.machine_name),
                                    html.Td(item.equipment_id),
                                    html.Td(item.company_name),
                                    html.Td(
                                        [
                                            html.A(
                                                "Delete",
                                                href="#{}".format(
                                                    item.equipment_id
                                                ),
                                            )
                                        ]
                                    ),
                                ]
                            )
                            for idx, item in enumerate(machine_list)
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
    [Output("machine_list_path", "pathname", allow_duplicate=True)],
    [Input("machine_list_path", "hash")],
    prevent_initial_call=True,
)
def machine_delete(hash: str) -> List:
    if hash is None:
        raise Exception("you haven't submitted")
    else:
        delete_machine(hash[1:])
    return ["/machines"]


@callback(
    [
        Output("machine_list_path", "pathname"),
        Output("equipment_id", "valid"),
        Output("equipment_id", "invalid"),
    ],
    [
        Input("machine_submit", "n_clicks"),
    ],
    [
        State("machine_name", "value"),
        State("equipment_id", "value"),
        State("company_name", "value"),
    ],
    prevent_initial_call=True,
)
def machine_register(*machine_info: List) -> Tuple[str, bool]:
    """_register new machine_

    Args:
        machine_info (_list_): _machine information_
    Returns:
        _list_: _return empty list_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    if "machine_submit" not in triggered_value:
        raise Exception("you haven't submitted the form")

    if machine_info[1:3] is not None:
        machine_equipment = machine_info[2].upper()
        is_genv = machine_equipment.startswith("GENV")
        if is_genv:
            create_machine(machine_info)
            notify_message("machine information registered")
    else:
        notify_message("Please write all the information")

    return "/machines", is_genv, not is_genv
