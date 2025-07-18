from datetime import datetime
from typing import Dict, List

from dash import dcc, Input, Output, State, callback
from dash.exceptions import PreventUpdate

from apps.back_end.cloud_data.cloud_data_filter import CloudFilter


@callback(
    [
        Output("download_csv_data", "data"),
    ],
    [
        Input("submit_csv_data", "submit_n_clicks"),
        Input("machine_mem", "modified_timestamp"),
    ],
    [
        State("graph_date_range", "start_date"),
        State("graph_date_range", "end_date"),
        State("timestamp_resampling", "value"),
        State("machine_mem", "data"),
    ],
    prevent_initial_call=True,
)
def graph_to_csv(
    submit_n_clicks: str,
    modified: str,
    start_date: datetime,
    end_date: datetime,
    resampling: str,
    machine_mem: Dict[str, str],
) -> List:
    """_ Download data _
    Args:
        n_clicks (_string_): _button clicking option_
    Returns:
        _string_: _return with location of the file_
    """
    if submit_n_clicks is None:
        raise PreventUpdate

    # Timestamp resampling not selected it will default take 1 minute data sampling
    if not resampling:
        resampling = "1Min"
        try:  # creating/opening a file
            with open("datasets/emessage.txt", "w") as error_file:
                # writing in the file
                error_file.write("Please, select resample option" + "\n")
        except Exception as err:
            print(f"the text file isn't exist : {err}")
    try:
        # Data download query and path link
        equipment_id = machine_mem[
            "equipment"
        ]  # get a machine equipment id #GENV17G017
        platform_id = machine_mem["platform"]  # get a machine platform id
        cloud_obj = CloudFilter(
            platform_id, equipment_id, start_date, end_date
        )  # called cloudfilter class to get cloud data
        print(f"download callback: {cloud_obj.platform_id}")
    except Exception as err:
        print(f"download cloudfilter error:{err}")

    df_days, df_filtered = cloud_obj.get_filter_data(
        start_date, end_date, resampling
    )  # date range system bring the date to specific date
    df_days.drop(columns=["timestamp"], axis=1, inplace=True)
    df_days.reset_index(inplace=True)
    download_file = f"cockpit_data_{start_date}_{end_date}_.csv"
    return [dcc.send_data_frame(df_days.to_csv, download_file, index=False)]
