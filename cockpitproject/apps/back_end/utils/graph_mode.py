from typing import List, Optional

import plotly.graph_objs as go
import pandas as pd
from pandas import DataFrame
import plotly.express as px
from sklearn.preprocessing import StandardScaler

# from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from memoization import cached, CachingAlgorithmFlag


@cached(ttl=86400, algorithm=CachingAlgorithmFlag.LFU)
def type_selection(
    mode_id: str,
    sub_categories: List[str],
    df_categories: DataFrame,
    x_axis: str = "",
    formula_selection: Optional[int] = None,
) -> DataFrame:
    """_different kind of graph mode selection_

    Args:
        graph_mode_id (_string_): _graph type value name_
        fscategories (_string_): _subcategories name_
        df_categories (_string_): _specific categories selection_
        fcategories (_string_): _all categories list_
        foxaxis (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    choose_type = ["lines", "markers", "lines+markers"]  # choose the graph type
    yaxis = ["y", "y2", "y3", "y4", "y5", "y6", "y7", "y8"]  # multi yaxis line setup
    trace = []

    mode_result = mode_id.split("_", 1)
    match mode_result[-1]:
        case "graph_mode1":
            trace = graph_choose(
                sub_categories,
                df_categories,
                x_axis,
                choose_type[0],
                yaxis,
                formula_selection,
            )
        case "graph_mode2":
            trace = graph_choose(
                sub_categories,
                df_categories,
                x_axis,
                choose_type[1],
                yaxis,
                formula_selection,
            )
        case "graph_mode3":
            if formula_selection:
                df_formula_result = formula_function(
                    df_categories, sub_categories, formula_selection
                )
                trace.append(
                    go.Histogram(
                        {
                            "x": df_formula_result.index,
                            "y": df_formula_result["formula_result"],
                            "name": f"{df_formula_result.loc[:,['formula_result']].iloc[0]}",
                        }
                    )
                )
            else:
                for idx, dataset in enumerate(sub_categories):
                    xaxis = x_axis if x_axis else dataset
                    datal = "value" if x_axis else "timestamp"
                    trace.append(
                        go.Histogram(
                            {
                                "x": df_categories.loc[
                                    df_categories["variable"] == xaxis, datal
                                ],
                                "y": df_categories.loc[
                                    df_categories["variable"] == dataset, "value"
                                ],
                                "name": f"{df_categories.loc[df_categories['variable'] == dataset, 'variable'].iloc[0]}",
                                "yaxis": yaxis[idx],
                            }
                        )
                    )
        case "graph_mode4":
            trace = anomaly_detection(
                sub_categories, df_categories, x_axis, choose_type[1], yaxis
            )
        case _:
            trace = graph_choose(
                sub_categories,
                df_categories,
                x_axis,
                choose_type[2],
                yaxis,
                formula_selection,
            )

    # get the graphical object figure output
    final_figure_data = go.Figure(data=trace)
    variable_color = [
        "#3D84CA",
        "#262626",
        "#FF5A00",
        "#00BEFF",
        "#006C4C",
        "#FFFFFF",
        "#868686",
        "#F4C723",
    ]

    def custom_update_layout(
        variable_color: int,
        yaxis_min: int,
        yaxis_max: int,
        idx_inc: int,
    ):
        final_figure_data.update_layout(
            yaxis2=dict(
                overlaying="y",
                anchor="free",
                side="left",
                autoshift=True,
                showgrid=True,
                showspikes=True,
                showticklabels=True,
                griddash="dash",
                tickfont=dict(color=variable_color),
                ticks="outside",
                tickwidth=1,
                tickcolor=variable_color,
                range=[yaxis_min, yaxis_max],
                tickmode="sync",
                ticklen=2,
            )
        )

    # Yaxis figure layout update where also used the custom limitation of yaxis figure
    for idx, dataset in enumerate(sub_categories):
        yaxis_min = df_categories.loc[df_categories["variable"] == dataset, "min"].iloc[
            0
        ]
        yaxis_max = df_categories.loc[df_categories["variable"] == dataset, "max"].iloc[
            0
        ]
        idx_inc = idx + 1
        if idx_inc == 2:
            custom_update_layout(variable_color[idx], yaxis_min, yaxis_max, idx_inc)
        elif idx_inc == 3:
            final_figure_data.update_layout(
                yaxis3=dict(
                    overlaying="y",
                    anchor="free",
                    side="left",
                    autoshift=True,
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )
        elif idx_inc == 4:
            final_figure_data.update_layout(
                yaxis4=dict(
                    overlaying="y",
                    anchor="free",
                    side="left",
                    autoshift=True,
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )
        elif idx_inc == 5:
            final_figure_data.update_layout(
                yaxis5=dict(
                    overlaying="y",
                    anchor="free",
                    side="left",
                    autoshift=True,
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )
        elif idx_inc == 6:
            final_figure_data.update_layout(
                yaxis6=dict(
                    overlaying="y",
                    anchor="free",
                    side="left",
                    autoshift=True,
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )
        elif idx_inc == 7:
            # tickfont as a dictionary and store it an
            # variable yaxis 7
            final_figure_data.update_layout(
                yaxis7=dict(
                    overlaying="y",  # specifyinfg y - axis has to be separated
                    anchor="free",  # specifying x - axis has to be the fixed
                    side="left",  # specifying the side the axis should be present
                    autoshift=True,
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )
        elif idx_inc == 8:
            # tickfont as a dictionary and store it an
            # variable yaxis 8
            final_figure_data.update_layout(
                yaxis8=dict(
                    overlaying="y",  # specifyinfg y - axis has to be separated
                    anchor="free",  # specifying x - axis has to be the fixed
                    side="left",  # specifying the side the axis should be present
                    autoshift=True,
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )
        else:
            final_figure_data.update_layout(
                yaxis=dict(
                    showgrid=True,
                    showspikes=True,
                    showticklabels=True,
                    griddash="dash",
                    tickfont=dict(color=variable_color[idx]),
                    ticks="outside",
                    tickwidth=1,
                    tickcolor=variable_color[idx],
                    range=[yaxis_min, yaxis_max],
                    tickmode="sync",
                    ticklen=2,
                )
            )

    # graph figure layout update code
    final_figure_data.update_layout(
        paper_bgcolor="LightSteelBlue",
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            title_font_family="Times New Roman",
            font=dict(size=15),
        ),
        colorway=variable_color,  # sets default trace color
    )
    return final_figure_data  # returning figure update layout data


def graph_choose(
    sub_categories: List[str],
    df_categories: DataFrame,
    x_axis: str,
    choose_type: str,
    yaxis: List[str],
    formula_selection: int,
) -> List[None | str]:
    """_graph selection type _

    Args:
        sub_categories (_string_): _get sub categories list data_
        df_categories (_string_): _get dataframe categories data_
        x_axis (_string_): _x axis selection information_
        choose_type (_int_): _choose the type of graph_

    Returns:
        _figure_: _send graph figure values_
    """
    try:
        trace = []
        if formula_selection:
            df_formula_result = formula_function(
                df_categories, sub_categories, formula_selection
            )
            trace = []
            trace.append(
                go.Scatter(
                    {
                        "x": df_formula_result.index,
                        "y": df_formula_result["formula_result"],
                        "name": f"{df_formula_result.loc[:,'formula_result'].name}",
                        "mode": choose_type,
                    }
                )
            )
        else:
            for idx, dataset in enumerate(sub_categories):
                xaxis = x_axis if x_axis else dataset
                datal = "value" if x_axis else "timestamp"
                trace.append(
                    go.Scatter(
                        {
                            "x": df_categories.loc[
                                df_categories["variable"] == xaxis, datal
                            ],
                            "y": df_categories.loc[
                                df_categories["variable"] == dataset, "value"
                            ],
                            "name": f"{df_categories.loc[df_categories['variable'] == dataset, 'variable'].iloc[0]} ({df_categories.loc[df_categories['variable'] == dataset, 'unit'].iloc[0]})",
                            "mode": choose_type,
                            "yaxis": yaxis[idx],
                        }
                    )
                )
        return trace
    except Exception as error:
        return print(error)


def formula_function(
    df_categories: DataFrame, sub_categories: List[str], formula_selection: int
) -> List[None | DataFrame]:
    """_formula function used to get calculation output_

    Args:
        df_categories (_list_): _description_
        sub_categories (_list_): _description_
        formula_selection (_list_): _description_
        choose_type (_list_): _description_

    Returns:
        _list_: _return back calculation result_
    """
    df_cloumn_data = df_categories.pivot(
        index=["timestamp"], columns="variable", values="value"
    )
    try:

        def notify_message(message):
            with open("datasets/emessage.txt", "w") as error_file:
                error_file.write(message)  # message writing the file  + "\n"

        if (len(sub_categories) == 1) and formula_selection:
            notify_message("select another variable")
            return px.line(x=[0], y=[0])

        elif (len(sub_categories) > 2) and (formula_selection <= 4):
            notify_message("select only two variable for calculation")
            return px.line(x=[0], y=[0])

        elif (len(sub_categories) == 2) and (formula_selection == 5):
            notify_message("select another variable for calibration")
            return px.line(x=[0], y=[0])

        else:

            def select_formula(formula_selection: int) -> DataFrame:
                """_selection of formula type and calculate the variables_

                Args:
                    formula_selection (_int_): _type of formula select_

                Returns:
                    _dataframe_: _return the result_
                """
                first_item = df_cloumn_data.loc[:, sub_categories[0]]
                second_item = df_cloumn_data.loc[:, sub_categories[1]]

                if (formula_selection == 1) and (len(sub_categories) == 2):
                    df_cloumn_data["formula_result"] = first_item + second_item
                elif (formula_selection == 2) and (len(sub_categories) == 2):
                    df_cloumn_data["formula_result"] = first_item - second_item
                elif (formula_selection == 3) and (len(sub_categories) == 2):
                    df_cloumn_data["formula_result"] = first_item * second_item
                elif (formula_selection == 4) and (len(sub_categories) == 2):
                    df_cloumn_data["formula_result"] = first_item / second_item
                elif (formula_selection == 5) and (len(sub_categories) == 3):
                    third_item = df_cloumn_data.loc[:, sub_categories[2]]
                    average = (second_item + third_item) / 2
                    df_cloumn_data["formula_result"] = first_item / average
                else:
                    notify_message("Please select formula variable")
                return df_cloumn_data

            df_cloumn_data = select_formula(formula_selection)
            # dataframe final formula result
            df_formula_result = df_cloumn_data.loc[:, ["formula_result"]]
            return df_formula_result

    except Exception as err:
        print(f"the text file isn't exist : {err}")
        with open("datasets/emessage.txt", "w") as error_file:
            error_file.write(
                f"Formula function:{err}"
            )  # Formula function exception error message


def anomaly_detection(
    graph_sub_categories: List[str],
    df_categories: DataFrame,
    x_axis: str,
    choose_type: str,
    yaxis: List[str],
) -> List[None | str]:
    try:
        # make dataframe from melt to pivot structure, locate the specific columns list of data. Next, drop all null value from the dataset
        df_list_pivot = pd.pivot_table(
            df_categories,
            values="value",
            index="timestamp",
            columns=["variable"],
            dropna=True,
        )  # from melt structure to convert pivot table
        df_list_loc = df_list_pivot.loc[
            :, graph_sub_categories
        ]  # get the specific selected sub categories data
        trace = []
        for idx, dataset in enumerate(graph_sub_categories):
            # check the condition if x axis selected column then will execute the column, otherwise dataframe index timestamp
            # get the y axis column values
            df_timestamp = df_list_loc[x_axis] if x_axis else df_list_loc.index
            trace.append(
                go.Scatter(
                    {
                        "x": df_timestamp,
                        "y": df_list_loc[dataset],
                        "name": f"{df_list_loc[dataset].name}",
                        "mode": choose_type,
                        "yaxis": yaxis[idx],
                    }
                )
            )

            # Anomaly detection Isolation forest algorithm setup
            # make the dataframe of those data.
            scaler = (
                StandardScaler()
            )  # function to standardize the data values into a standard format.
            fit_scaler = scaler.fit_transform(
                df_list_loc[dataset].values.reshape(-1, 1)
            )  # we use fit_transform() along with the assigned object to transform the data and standardize it.
            # df_fit_scaler = DataFrame(fit_scaler)
            # Initializing Isolation Forest
            # model = IsolationForest(random_state=np.random.RandomState(42), contamination=float(0.2), n_estimators=100, max_samples='auto')  #  max_features=1.0, bootstrap=False, n_jobs=-1, verbose=0
            # Training and fitting the model
            # model.fit(df_fit_scaler)
            # df_list_loc['anomaly'] = model.predict(df_list_loc[[dataset]])

            # LOCAL OUTLIER FACTOR ALGORITHM
            model = LocalOutlierFactor(n_neighbors=20, contamination="auto")
            df_list_loc["anomaly"] = model.fit_predict(fit_scaler)

            # Saving anomalies to a separate dataset for visualization purposes
            outliers = df_list_loc.loc[df_list_loc["anomaly"] == -1]
            # outliers_index = list(outliers.index)
            df_list_loc["anomaly"].value_counts()

            # load the anomaly data to the graph
            trace.append(
                go.Scatter(
                    {
                        "x": df_timestamp,
                        "y": outliers[dataset],
                        "name": f"anomaly detect:{outliers[dataset].name}",
                        "mode": choose_type,
                        "marker": {"color": "red"},
                    }
                )
            )

        return trace
    except Exception as err:
        return print(f"anomaly error: {err}")
