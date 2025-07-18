from typing import Tuple, Dict

from dash import callback, Output, Input
from flask_login import logout_user, current_user
from peewee import fn

from apps.home import home_layout
from apps.auth import login, p404, register
from apps.front_end.utils import machine_list, category_list, sub_category_list
from apps.front_end.dashboard import dashboard_layout
from apps.front_end.diagnostic import machine_diags
from apps.back_end.cloud_data.cloud_data_filter import CloudFilter
from apps.db_model.models import Machine, MachineData


@callback(
    [
        Output("page_content", "children"),
        Output("machine_mem", "data"),
        ],
    [
        Input("page_url", "pathname")
        ],
    prevent_initial_call=True,
)
def display_page(url_address: str) -> Tuple[str, Dict]:
    """_setup page url authentication and send the url to get page data_

    Args:
        url_address (_url_): _ getting url from browser check auth_

    Returns:
        _text_: _return back page content data_
    """
    if current_user.is_authenticated:
        if url_address == "/":
            return dashboard_layout, {}
        elif url_address == "/logout":
            logout_user()
            return home_layout, {}
        elif url_address == "/machines":
            return machine_list.machines_layout, {}
        elif url_address == "/category":
            return category_list.category_layout, {}
        elif url_address == "/subcategory":
            return sub_category_list.sub_category_layout, {}
        elif url_address == "/dashboard":
            return dashboard_layout, {}
        elif (url_address == "/GENV17G017_89234") or (
            url_address == "/GENV21G022_K5METALLIZER"
        ):
            try:
                equipment_id = url_address[1:11]
                platform_id = url_address[12:]
                # From Cloud connection system
                # get blob file path
                # paths = platform_id + "/variables/" + equipment_id
                # blob_file_lists = AccessData.client().list_blobs(paths)
                # # get dates from all blob files
                # file_date_list = []
                # for blob in blob_file_lists:
                #     if "K5METALLIZER" == platform_id:
                #         file_date = str(blob.name)[49:59]
                #     else:
                #         file_date = str(blob.name)[42:52]
                #     date_number = file_date[0:4] + file_date[5:7] + file_date[8:]
                #     file_date_list.append(date_number)

                # From Database connection system
                # From Database connection system
                machine_info = (
                    Machine.select().where(Machine.equipment_id == equipment_id).first()
                )

                machine_data_query = (
                    (
                        MachineData.select(
                            fn.MIN(MachineData.timestamp.cast("date")).alias("min_date")
                        )
                    )
                    .where(MachineData.machine_id == machine_info.id)
                    .first()
                )
                dflt_start_date = machine_data_query.min_date
                dflt_end_date = machine_data_query.min_date
            except Exception as err:
                print(f" url path is not getting a value: {err}")

            # cloud object from CloudFilter class
            cloud_obj = CloudFilter(
                platform_id, equipment_id, dflt_start_date, dflt_end_date
            )
            diags_front_end = machine_diags.DiagsFrontEnd(cloud_obj)
            # called diagnostic page first section layout
            first_section = diags_front_end.section_layout(
                "dashboard_btn",
                "graph_date_range",
                "timestamp_resampling",
                "first_graph_chart",
                "first_graph_categories",
                "first_graph_sub_categories",
                "",
                "",
                "first_graph_mode1",
                "first_graph_mode2",
                "first_graph_mode3",
                "first_graph_mode4",
                "Load Graph",
                "first_graph_submit",
                "graph_submit",
                "me-1 gsubmitb",
                "loader4",
                "first_graph_loader",
                "circle",
                True,
                "#db0720",
                True,
            )
            # called diagnostic page second section layout
            second_section = diags_front_end.section_layout(
                "",
                "",
                "",
                "second_graph_chart",
                "second_graph_categories",
                "second_graph_sub_categories",
                "",
                "",
                "second_graph_mode1",
                "second_graph_mode2",
                "second_graph_mode3",
                "second_graph_mode4",
                "Load Graph",
                "second_graph_submit",
                "graph_submit",
                "me-1 gsubmitb",
                "loader4",
                "second_graph_loader",
                "circle",
                True,
                "#db0720",
                True,
            )
            # called diagnostic page third section layout
            third_section = diags_front_end.section_layout(
                "",
                "",
                "",
                "third_graph_chart",
                "third_graph_categories",
                "third_graph_sub_categories",
                "third_graph_formula_selection",
                "",
                "third_graph_mode1",
                "third_graph_mode2",
                "third_graph_mode3",
                "third_graph_mode4",
                "Load Graph",
                "third_graph_submit",
                "graph_submit",
                "me-1 gsubmitb",
                "loader4",
                "third_graph_loader",
                "circle",
                True,
                "#db0720",
                True,
            )
            # called diagnostic page fourth section layout
            fourth_section = diags_front_end.section_layout(
                "",
                "",
                "",
                "fourth_graph_chart",
                "fourth_graph_categories",
                "fourth_graph_sub_categories",
                "",
                "fourth_graph_x_axis",
                "fourth_graph_mode1",
                "fourth_graph_mode2",
                "fourth_graph_mode3",
                "fourth_graph_mode4",
                "Load Graph",
                "fourth_graph_submit",
                "graph_submit",
                "me-1 gsubmitb",
                "loader4",
                "fourth_graph_loader",
                "circle",
                True,
                "#db0720",
                True,
            )
            return [first_section, second_section, third_section, fourth_section], {
                "platform": cloud_obj.platform_id,
                "equipment": cloud_obj.equipment_id,
            }
        else:
            return p404.p404_layout, {}
    elif url_address == "/login":
        return login.login_layout, {}
    elif url_address == "/register":
        return register.register_layout, {}
    else:
        return home_layout, {}
