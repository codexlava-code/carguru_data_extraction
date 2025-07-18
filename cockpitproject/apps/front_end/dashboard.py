from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback, ctx
from dash.exceptions import PreventUpdate

from datasets.access_data import AccessData


def dashboard_machine_list() -> str:
    """_This is dashboard page where will show the machine list_

    Returns:
        _string_: _return a layout of html code_
    """

    def blob_dict(platform_id: str, equipment_id: str, data_type: str) -> Dict:
        """_Blob dictionary function make dictionary of machine list data_

        Args:
            platform_id (_string_): _Machine platform number_
            equipment_id (_string_): _Machine equipment number_
            data_type (_string_): _Machine data type_

        Returns:
            _dict_: _machine dictionary data_
        """
        dict_data = {
            "machine_name": platform_id,
            "equipment_name": equipment_id,
            "data_type": data_type,
        }
        return blob_list_all.append(dict_data)

    # setup a blob container path link
    blob_path = "K5METALLIZER"  # + "/variables/" + equipment_id
    blob_file_lists = AccessData.client().list_blobs(blob_path)

    blob_list_all = []
    # Volta R&D machine manually added in the list
    volta_machine = {
        "machine_name": "89234",
        "equipment_name": "GENV17G017",
        "data_type": "variable",
    }
    blob_list_all.append(volta_machine)

    for blob in blob_file_lists:
        # get the blob information
        file_date = str(blob.name)

        if 33 == len(file_date):
            platform_id = file_date[0:12]
            equipment_id = file_date[23:33]
            data_type = file_date[13:21]
            blob_dict(platform_id, equipment_id, data_type)
        # # check the machine faults data type
        # elif 30 == len(file_date):
        #     platform_id = file_date[0:12]
        #     equipment_id = file_date[20:32]
        #     data_type = file_date[13:19]
        #     blob_dict(platform_id,equipment_id,data_type)
        # # check the machine machineevent data type
        # elif 36 == len(file_date):
        #     platform_id = file_date[0:12]
        #     equipment_id = file_date[26:36]
        #     data_type = file_date[13:25]
        #     blob_dict(platform_id,equipment_id,data_type)

    return html.Div(
        [
            # pass the prefix to the url
            dcc.Location(id="machine_url_path", refresh=True),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.NavbarSimple(
                                        children=[
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Category", href="/category"
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Subcategory",
                                                    href="/subcategory",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Machines",
                                                    href="/machines",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink("logout", href="/logout")
                                            ),
                                            # dbc.DropdownMenu(
                                            #     children=[
                                            #         dbc.DropdownMenuItem("More pages", header=True),
                                            #         dbc.DropdownMenuItem("Page 2", href="#"),
                                            #         dbc.DropdownMenuItem("Page 3", href="#"),
                                            #     ],
                                            #     nav=True,
                                            #     in_navbar=True,
                                            #     label="More",
                                            # ),
                                        ],
                                        brand=html.Img(
                                            src="assets/images/logo.svg", height="30px"
                                        ),
                                        brand_href="#",
                                        color="black",
                                        dark=False,
                                    ),
                                ],
                                width={"size": 12},
                            )
                        ],
                        align="center",
                        justify="center",
                    )
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div([html.H4("Machine dashboard list")]),
                                ],
                                width={"size": 12},
                            ),
                        ],
                        align="center",
                        justify="center",
                    )
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Table(
                                        [
                                            html.Thead(
                                                [
                                                    html.Tr(
                                                        [
                                                            html.Th("Machine Name"),
                                                            html.Th("Equipment Number"),
                                                            html.Th("Event Type"),
                                                            html.Th("Action"),
                                                        ]
                                                    )
                                                ]
                                            ),
                                            html.Tbody(
                                                [
                                                    html.Tr(
                                                        [
                                                            html.Td(
                                                                blob_value[
                                                                    "machine_name"
                                                                ]
                                                            ),
                                                            html.Td(
                                                                blob_value[
                                                                    "equipment_name"
                                                                ]
                                                            ),
                                                            html.Td(
                                                                blob_value["data_type"]
                                                            ),
                                                            html.Td(
                                                                dbc.Button(
                                                                    "Open",
                                                                    id=blob_value[
                                                                        "equipment_name"
                                                                    ]
                                                                    + "_"
                                                                    + blob_value[
                                                                        "machine_name"
                                                                    ],
                                                                )
                                                            ),
                                                        ]
                                                    )
                                                    for blob_value in blob_list_all  # user for loop to show machine data
                                                ]
                                            ),
                                        ],
                                        dark=True,
                                        hover=True,
                                        responsive=True,
                                        color="light",
                                    ),
                                ],
                                width={"size": 12},
                            ),
                        ],
                        align="center",
                        justify="center",
                    )
                ]
            ),
        ],
        className="dashboard container_header",
    )


# get dashboard layout
dashboard_layout = dashboard_machine_list()


@callback(
    [Output("machine_url_path", "pathname")],
    [
        Input("GENV17G017_89234", "n_clicks"),
        Input("GENV21G022_K5METALLIZER", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def machine_selection(*machines: str) -> List:
    """_machine list selection system_

    Args:
        select (_string_): _Select machine _
    """
    if machines is None:
        # prevent the None callbacks is important with the store component.
        raise PreventUpdate
    else:
        triggered_value = ctx.triggered_id
        equipment_id = triggered_value[0:10]
        platform_id = triggered_value[11:]
        # print(f"dashboard data: {platform_id}")

        try:
            if "GENV17G017" in triggered_value:
                return [equipment_id + "_" + platform_id]
            elif "GENV21G022" in triggered_value:
                return [equipment_id + "_" + platform_id]
            else:
                return [dashboard_layout]
        except Exception as err:
            print(f" select the machine: {err}")
