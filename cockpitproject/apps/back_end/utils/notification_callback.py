import time
import os
import logging
from typing import List

from dash import Input, Output, callback, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from apps.back_end.utils.logger import ErrorLogger


def notify_message(message: str) -> None:
    """_notification message of the front page_

    Args:
        message (_string_): _notify message_
    """
    try:
        with open("datasets/emessage.txt", "w") as error_file:
            error_file.write(message + "\n")  # writing the notify message on the file
    except Exception as err:
        print(f"the text file isn't exist : {err}")
        # Create a logging instance
        logger = logging.getLogger("file_error")
        obj_err_log = ErrorLogger()
        obj_err_log.debug_logger(logger)
        # logger exception path location error
        logger.exception(err)  # Will send the errors to the file


@callback(
    [
        Output("notify_container", "children", allow_duplicate=True),
    ],
    [
        Input("first_graph_categories", "value"),  # First graph list of inputs
        Input("first_graph_mode1", "n_clicks"),
        Input("first_graph_mode2", "n_clicks"),
        Input("first_graph_mode3", "n_clicks"),
        Input("first_graph_mode4", "n_clicks"),
        Input("first_graph_submit", "n_clicks"),
        Input("second_graph_categories", "value"),  # Second graph list of inputs
        Input("second_graph_mode1", "n_clicks"),
        Input("second_graph_mode2", "n_clicks"),
        Input("second_graph_mode3", "n_clicks"),
        Input("second_graph_mode4", "n_clicks"),
        Input("second_graph_submit", "n_clicks"),
        Input("third_graph_categories", "value"),  # Third graph list of inputs
        Input("third_graph_mode1", "n_clicks"),
        Input("third_graph_mode2", "n_clicks"),
        Input("third_graph_mode3", "n_clicks"),
        Input("third_graph_mode4", "n_clicks"),
        Input("third_graph_submit", "n_clicks"),
        Input("fourth_graph_categories", "value"),  # Fourth graph list of inputs
        Input("fourth_graph_mode1", "n_clicks"),
        Input("fourth_graph_mode2", "n_clicks"),
        Input("fourth_graph_mode3", "n_clicks"),
        Input("fourth_graph_mode4", "n_clicks"),
        Input("fourth_graph_submit", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def graph_notification(*compnt_values: str) -> List[str]:
    """_The graph notification system_

    Returns:
        _type_: _description_
    """
    triggered_value = [p["prop_id"] for p in ctx.triggered][0]
    time.sleep(1)
    try:
        if os.path.getsize("datasets/emessage.txt") == 0:
            (
                notify_icon,
                notify_color,
                notify_header,
                notify_message,
            ) = graph_type_notify(triggered_value)
        else:
            try:
                with open("datasets/emessage.txt", "r+") as error_file:
                    read_error = error_file.readline()
                    print("notification message: {read_error}")
                    error_file.truncate(0)  # truncate method reduces a document's size.
                    error_file.seek(
                        0
                    )  # change the position of the File handle to a given specific position.
                notify_icon = "ic:baseline-add-alert"
                notify_color = "red"
                notify_header = "Error information"
                notify_message = read_error
            except Exception as err:
                notify_icon = "ic:baseline-add-alert"
                notify_color = "red"
                notify_header = "Error information"
                notify_message = err

    except Exception as err:
        # notification message information
        notify_icon = "ic:baseline-add-alert"
        notify_color = "red"
        notify_header = "Error information"
        notify_message = str(err)
        # debug logger error list
        logger = logging.getLogger("file_error")
        err_logger = ErrorLogger()
        err_logger.debug_logger(logger)
        logger.exception(err)  # send the debug logging error to debug file.

    return [
        dmc.Notification(
            title=notify_header,
            id="simple-notify",
            action="show",
            autoClose=2000,
            color=notify_color,
            message=notify_message,
            icon=DashIconify(icon=notify_icon),
        )
    ]


def graph_type_notify(triggered_value: str) -> tuple[str]:
    notify_icon = "ic:baseline-add-alert"
    notify_color = "green"
    notify_header = "Options feedback"

    match triggered_value[7:17]:
        case "graph_categories":
            notify_message = "subcategories list has loaded"
        case "graph_mode1":
            notify_message = "Line graph has loaded"
        case "graph_mode2":
            notify_message = "Scatter graph has loaded"
        case "graph_mode3":
            notify_message = "Histogram graph has loaded"
        case "graph_mode4":
            notify_message = "Anomaly detection graph has loaded"
        case "graph_submit":
            notify_message = "the graph has loaded"
        case _:
            notify_message = "please,choose the graph option"
    return notify_icon, notify_color, notify_header, notify_message
