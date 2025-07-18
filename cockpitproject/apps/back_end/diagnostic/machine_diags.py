from datetime import datetime
from typing import Tuple, List, Dict, Optional

import pandas as pd
from pandas import DataFrame
import plotly.express as px
from memoization import cached, CachingAlgorithmFlag
from dash import Input, Output, State, callback, ctx

from apps.back_end.utils import graph_mode
from apps.back_end.cloud_data.cloud_data_filter import CloudFilter
from apps.back_end.utils.notification_callback import notify_message

start_date_g = "2024-07-03"
end_date_g = "2023-07-03"
df_filtered = pd.Series([start_date_g, end_date_g], name="timestamp")


def filter_data(
    machine_mem: Dict,
    triggered_value: str,
    start_date: datetime,
    end_date: datetime,
    resampling: str,
) -> DataFrame:
    """_get check date then filter data based on timestamp_

    Args:
        triggered_value (_string_): _when press any button it will get triggered value_
        start_date (_date_): _get the start date selecton date_
        end_date (_date_): _get the end date selection date_
        start_date_g (_date_): _get the previous selection start date_
        end_date_g (_date_): _get the previous selection end date _

    Returns:
        _list_: _return dataframe data list_
    """
    global df_filtered, start_date_g, end_date_g  # save global date data

    cloud_obj = CloudFilter(
        machine_mem["platform"], machine_mem["equipment"], start_date, end_date
    )
    # print(f"first backend object: {cloud_obj.platform_id}")

    triggered = [
        "graph_submit",
        "graph_mode1",
        "graph_mode2",
        "graph_mode3",
        "graph_mode4",
    ]
    # Check the condition of button submission the query the timestamp data
    if any(trig in triggered_value for trig in triggered):
        # compare previous date and current data. if its new date call the function
        if (start_date != start_date_g) or (end_date != end_date_g) or resampling:
            data = cloud_obj.get_filter_data(start_date, end_date, resampling)
            df_days, df_filtered = data
            start_date_g, end_date_g = start_date, end_date

        date_filtered = df_filtered[
            (df_filtered.timestamp >= start_date) & (df_filtered.timestamp <= end_date)
        ]
    else:
        date_filtered = cloud_obj.get_categories()
    return date_filtered


def filter_categories(
    date_filtered: List[int | str], categories: str
) -> Tuple[DataFrame]:
    """_get categories filter data and sub categories filter data_

    Args:
        date_filtered (_list_): _get dataframe list data_
        categories (_string_): _get the categories name_

    Returns:
        _list_: _return categories and subcategories data_
    """
    categories_filtered = date_filtered[
        date_filtered["category"] == categories
    ]  # get the categories data type list
    sub_categories_filtered = categories_filtered.drop_duplicates("variable")
    sub_categories_list = sub_categories_filtered["variable"]
    return categories_filtered, sub_categories_list


def check_subcategories(
    sub_categories: List[int | str],
    triggered_value: str,
    categories_filtered: List[int | str],
    x_axis: str = "",
    formula_selection: Optional[int] = None,
) -> DataFrame:
    """_check the subcategories status then send feedback_

    Args:
        sub_categories (_list_): _description_
        triggered_value (_string_): _description_
        categories_filtered (_list_): _description_
    """
    if sub_categories:
        # Check the limitation of sub_categories choose
        if count := len(sub_categories) > 8:
            figure_data = px.scatter(x=[0], y=[count])
            notify_message("Please don't choose more than 8 variables")
        else:
            figure_data = graph_mode.type_selection(
                triggered_value,
                sub_categories,
                categories_filtered,
                x_axis,
                formula_selection,
            )
    else:
        figure_data = px.scatter(x=[0], y=[0])
        triggered = ["submit", "mode1", "mode2", "mode3", "mode4"]
        # Subcategories none select notification system
        if any(mode in triggered_value for mode in triggered):
            # Notification message
            notify_message("Please select sub categories")
    return figure_data


@callback(
    [
        Output("first_graph_chart", "figure"),
        Output("first_graph_sub_categories", "options"),
        Output("first_graph_loader", "children"),
        Output("first_graph_submit", "disabled"),
        Output("first_graph_mode1", "disabled"),
        Output("first_graph_mode2", "disabled"),
        Output("first_graph_mode3", "disabled"),
        Output("first_graph_mode4", "disabled"),
        Output("csv_submit_btn", "disabled"),
    ],
    [
        Input("first_graph_categories", "value"),
        Input("first_graph_mode1", "n_clicks"),
        Input("first_graph_mode2", "n_clicks"),
        Input("first_graph_mode3", "n_clicks"),
        Input("first_graph_mode4", "n_clicks"),
        Input("first_graph_submit", "n_clicks"),
        Input("machine_mem", "modified_timestamp"),
    ],
    [
        State("graph_date_range", "start_date"),
        State("graph_date_range", "end_date"),
        State("timestamp_resampling", "value"),
        State("first_graph_sub_categories", "value"),
        State("machine_mem", "data"),
    ],
    prevent_initial_call=True,
)
@cached(ttl=86400, algorithm=CachingAlgorithmFlag.LFU)
def first_diags_callback(
    categories: str,
    mode1: str,
    mode2: str,
    mode3: str,
    mode4: str,
    submit: str,
    nothing: str,
    start_date: datetime,
    end_date: datetime,
    resampling: str,
    sub_categories: List[str],
    machine_mem: Dict[str, str],
) -> Tuple[List[int | str], str, bool]:
    """_ first graph layout callback function setup_

    Args:
        categories (str, optional): _get categories data_. Defaults to "".
        mode1 (str, optional): _ select line graph_. Defaults to "".
        mode2 (str, optional): _select dot graph_. Defaults to "".
        mode3 (str, optional): _select histogram graph_. Defaults to "".
        submit (str, optional): _ submit graph and data selection_. Defaults to "".
        start_date (datetime, optional): _get start date_. Defaults to "".
        end_date (datetime, optional): _get end date_. Defaults to "".
        sub_categories (str, optional): _get subcategories data_. Defaults to "".

    Returns:
        _figure_: _return graph figure data_
        _list_: _return subcategories list data_
        _loader_: _return preloader activation_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]
    # triggered_value = [p["prop_id"] for p in ctx.triggered][0]
    # triggered_value = ctx.triggered_id

    # date filtered data
    date_filtered = filter_data(
        machine_mem, triggered_value, start_date, end_date, resampling
    )

    # categories information list
    categories_filtered, sub_categories_list = filter_categories(
        date_filtered, categories
    )
    # Check categories trigger change
    if "categories.value" in triggered_value:
        sub_categories = []
    # check subcategories is exist or not when exist send to the graph mode function
    figure_data = check_subcategories(
        sub_categories, triggered_value, categories_filtered
    )

    return (
        figure_data,
        [{"label": list, "value": list} for list in sub_categories_list],
        "",
        False,
        False,
        False,
        False,
        False,
        False,
    )  # return figure graph data


@callback(
    [
        Output("second_graph_chart", "figure"),
        Output("second_graph_sub_categories", "options"),
        Output("second_graph_loader", "children"),
        Output("second_graph_submit", "disabled"),
        Output("second_graph_mode1", "disabled"),
        Output("second_graph_mode2", "disabled"),
        Output("second_graph_mode3", "disabled"),
    ],
    [
        Input("second_graph_categories", "value"),
        Input("second_graph_mode1", "n_clicks"),
        Input("second_graph_mode2", "n_clicks"),
        Input("second_graph_mode3", "n_clicks"),
        Input("second_graph_submit", "n_clicks"),
        Input("machine_mem", "modified_timestamp"),
    ],
    [
        State("graph_date_range", "start_date"),
        State("graph_date_range", "end_date"),
        State("timestamp_resampling", "value"),
        State("second_graph_sub_categories", "value"),
        State("machine_mem", "data"),
    ],
    prevent_initial_call=True,
)
# @cached(max_size=None,algorithm=CachingAlgorithmFlag.LFU)
def second_diags_callback(
    categories: str,
    mode1: str,
    mode2: str,
    mode3: str,
    submit: str,
    nothing: str,
    start_date: datetime,
    end_date: datetime,
    resampling: str,
    sub_categories: List[str],
    machine_mem: Dict[str, str],
) -> Tuple[List[str | int], str, bool]:
    """_ second layout chart filter date,categories and subcategories_
    Args:
        categories (str, optional): _get categories data_. Defaults to "".
        mode1 (str, optional): _ select line graph_. Defaults to "".
        mode2 (str, optional): _select dot graph_. Defaults to "".
        mode3 (str, optional): _select histogram graph_. Defaults to "".
        submit (str, optional): _ submit graph and data selection_. Defaults to "".
        start_date (datetime, optional): _get start date_. Defaults to "".
        end_date (datetime, optional): _get end date_. Defaults to "".
        sub_categories (str, optional): _get subcategories data_. Defaults to "".

    Returns:
        _list_: _return figure graph data_
        _list_: _return subcategories list_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    # date filtered data
    date_filtered = filter_data(
        machine_mem, triggered_value, start_date, end_date, resampling
    )

    # categories information list
    categories_filtered, sub_categories_list = filter_categories(
        date_filtered, categories
    )

    # Check categories trigger change
    if "categories.value" in triggered_value:
        sub_categories = []

    # check subcategories is exist or not when exist send to the graph mode function
    figure_data = check_subcategories(
        sub_categories, triggered_value, categories_filtered
    )

    return (
        figure_data,
        [{"label": list, "value": list} for list in sub_categories_list],
        "",
        False,
        False,
        False,
        False,
    )


@callback(
    [
        Output("third_graph_chart", "figure"),
        Output("third_graph_sub_categories", "options"),
        Output("third_graph_loader", "children"),
        Output("third_graph_submit", "disabled"),
        Output("third_graph_mode1", "disabled"),
        Output("third_graph_mode2", "disabled"),
        Output("third_graph_mode3", "disabled"),
    ],
    [
        Input("third_graph_categories", "value"),
        Input("third_graph_mode1", "n_clicks"),
        Input("third_graph_mode2", "n_clicks"),
        Input("third_graph_mode3", "n_clicks"),
        Input("third_graph_submit", "n_clicks"),
        Input("machine_mem", "modified_timestamp"),
    ],
    [
        State("graph_date_range", "start_date"),
        State("graph_date_range", "end_date"),
        State("timestamp_resampling", "value"),
        State("third_graph_sub_categories", "value"),
        State("third_graph_formula_selection", "value"),
        State("machine_mem", "data"),
    ],
    prevent_initial_call=True,
)
# @cached(max_size=None,algorithm=CachingAlgorithmFlag.LRU)
def third_diags_callback(
    categories: str,
    mode1: str,
    mode2: str,
    mode3: str,
    submit: str,
    nothing: str,
    start_date: datetime,
    end_date: datetime,
    resampling: str,
    sub_categories: List[str],
    formula_selection: int,
    machine_mem: Dict[str, str],
) -> Tuple[List[str | int], str, bool]:
    """_ third layout chart filter date,categories and subcategories_
    Args:
        categories (str, optional): _get categories data_. Defaults to "".
        mode1 (str, optional): _ select line . Defaults to "".
        mode2 (str, optional): _select dot . Defaults to "".
        mode3 (str, optional): _select histogram . Defaults to "".
        submit (str, optional): _ submit graph and data selection_. Defaults to "".
        start_date (datetime, optional): _get start date_. Defaults to "".
        end_date (datetime, optional): _get end date_. Defaults to "".
        sub_categories (str, optional): _get subcategories data_. Defaults to "".

    Returns:
        _list_: _return figure graph data_
        _list_: _return subcategories list_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    # date filtered data
    date_filtered = filter_data(
        machine_mem, triggered_value, start_date, end_date, resampling
    )
    # categories information list
    categories_filtered, sub_categories_list = filter_categories(
        date_filtered, categories
    )
    # Check categories trigger change
    if "categories.value" in triggered_value:
        sub_categories = []
    # check subcategories is exist or not when exist send to the graph mode function
    figure_data = check_subcategories(
        sub_categories, triggered_value, categories_filtered, None, formula_selection
    )

    return (
        figure_data,
        [{"label": list, "value": list} for list in sub_categories_list],
        "",
        False,
        False,
        False,
        False,
    )  # return figure graph data


@callback(
    [
        Output("fourth_graph_chart", "figure"),
        Output("fourth_graph_sub_categories", "options"),
        Output("fourth_graph_loader", "children"),
        Output("fourth_graph_submit", "disabled"),
        Output("fourth_graph_mode1", "disabled"),
        Output("fourth_graph_mode2", "disabled"),
        Output("fourth_graph_mode3", "disabled"),
    ],
    [
        Input("fourth_graph_categories", "value"),
        Input("fourth_graph_mode1", "n_clicks"),
        Input("fourth_graph_mode2", "n_clicks"),
        Input("fourth_graph_mode3", "n_clicks"),
        Input("fourth_graph_submit", "n_clicks"),
        Input("machine_mem", "modified_timestamp"),
    ],
    [
        State("graph_date_range", "start_date"),
        State("graph_date_range", "end_date"),
        State("timestamp_resampling", "value"),
        State("fourth_graph_sub_categories", "value"),
        State("fourth_graph_x_axis", "value"),
        State("machine_mem", "data"),
    ],
    prevent_initial_call=True,
)
# @cached(max_size=None,algorithm=CachingAlgorithmFlag.LRU)
def fourth_diags_callback(
    categories: str,
    mode1: str,
    mode2: str,
    mode3: str,
    submit: str,
    nothing: str,
    start_date: datetime,
    end_date: datetime,
    resampling: str,
    sub_categories: List[str],
    x_axis: str,
    machine_mem: Dict[str, str],
) -> Tuple[List[str | int], list[str], bool]:
    """_ fourth graph layout callback function setup_

    Args:
        categories (str, optional): _get categories data_. Defaults to "".
        mode1 (str, optional): _ select line graph_. Defaults to "".
        mode2 (str, optional): _select dot graph_. Defaults to "".
        mode3 (str, optional): _select histogram graph_. Defaults to "".
        submit (str, optional): _ submit graph and data selection_. Defaults to "".
        start_date (datetime, optional): _get start date_. Defaults to "".
        end_date (datetime, optional): _get end date_. Defaults to "".
        sub_categories (str, optional): _get subcategories data_. Defaults to "".

    Returns:
        _figure_: _return graph figure data_
        _list_: _return subcategories list data_
        _loader_: _return preloader activation_
    """
    triggered_value = ctx.triggered[0]["prop_id"].split(".")[0]

    # date filtered data
    date_filtered = filter_data(
        machine_mem, triggered_value, start_date, end_date, resampling
    )
    # categories information list
    categories_filtered, sub_categories_list = filter_categories(
        date_filtered, categories
    )
    # Check categories trigger change
    if "categories.value" in triggered_value:
        sub_categories = []
    # check subcategories is exist or not when exist send to the graph mode function
    figure_data = check_subcategories(
        sub_categories, triggered_value, categories_filtered, x_axis, None
    )

    return (
        figure_data,
        [{"label": list, "value": list} for list in sub_categories_list],
        "",
        False,
        False,
        False,
        False,
    )
