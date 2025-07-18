from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from apps.back_end.cloud_data.cloud_data_filter import CloudFilter


class DiagsFrontEnd:
    """_Diagnostic page front end design layout_"""

    def __init__(self, cloud_obj: CloudFilter):
        self._cloud_obj = cloud_obj

    def section_layout(
        self,
        dashboard_btn: str,
        date_range: str,
        timestamp_resampling: str,
        chart: str,
        categories: str,
        sub_categories: str,
        formula: str,
        x_axis: str,
        graph_mode1: str,
        graph_mode2: str,
        graph_mode3: str,
        graph_mode4: str,
        submit_text: str,
        submit_id: str,
        submit_name: str,
        submit_class: str,
        loader_id: str,
        loader_content_id: str,
        loader_type: str,
        loader_fullscreen: str,
        color: str,
        loading_state: str,
    ) -> str:
        """_main section layout method to show the front-end component_

        Args:
            dashboard_btn (_type_): _description_
            date_range (_type_): _description_
            timestamp_resampling (_type_): _description_
            chart (_type_): _description_
            categories (_type_): _description_
            sub_categories (_type_): _description_
            formula (_type_): _description_
            x_axis (_type_): _description_
            graph_mode1 (_type_): _description_
            graph_mode2 (_type_): _description_
            graph_mode3 (_type_): _description_
            graph_mode4 (_type_): _description_
            submit_text (_type_): _description_
            submit_id (_type_): _description_
            submit_name (_type_): _description_
            submit_class (_type_): _description_
            notify (_type_): _description_
            loader_id (_type_): _description_
            loader_content_id (_type_): _description_
            loader_type (_type_): _description_
            loader_fullscreen (_type_): _description_
            color (_type_): _description_
            loading_state (_type_): _description_

        Returns:
            _string_: _section layout code_
        """
        # print(f"front_end:{self._cloud_obj.platform_id}")

        # validate date_range and platform_id. the component date_picker,resampling,confirm dialog called
        date_range_compnt = ""
        dataframe_csv_download = ""
        timestamp_resampling_compnt = ""
        if date_range and self._cloud_obj.platform_id:
            date_range_compnt = self.date_picker(date_range)
            timestamp_resampling_compnt = self.timestamp_resampling(
                timestamp_resampling
            )
            dataframe_csv_download = self.confirm_dialog(
                "submit_csv_data",
                "download_csv_data",
                "csv_submit_btn",
                "Download CSV",
                "Do you want to download CSV file",
            )

        # validate formula. the component math_formula called
        formula_compnt = ""
        if formula:
            formula_compnt = self.math_formula(formula)

        # validate x_axis and platform_id. the component x_axis_variable  called
        xaxis_compnt = ""
        if x_axis and self._cloud_obj.platform_id:
            xaxis_compnt = self.x_axis_variable(x_axis)

        # validate dashboard_btn. the component dashboard_button  called
        dashboard_return_btn = ""
        if dashboard_btn:
            dashboard_return_btn = self.dashboard_button("Dashboard", "me-1 gsubmitb")

        # validate platform_id. the component categories called
        categories_section = ""
        if self._cloud_obj.platform_id:
            categories_section = self.categories(categories)

        section_layout = dbc.Card(
            dbc.CardBody(
                [
                    dbc.Container(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [self.graph_chart(chart)], width=10
                                    ),  # graph chart method called to get the chart layout
                                    dbc.Col(
                                        [
                                            # date picker method called to get date range layout
                                            date_range_compnt,
                                            # timestamp sampling method called to get sample dorpdown layout
                                            timestamp_resampling_compnt,
                                            # categories method called to get categories layout
                                            categories_section,
                                            # categories method called to get categories layout
                                            self.sub_categories(sub_categories),
                                            # mathmetical formula selection
                                            formula_compnt,
                                            # x axis variable method called to get x_axis layout
                                            xaxis_compnt,
                                            # graph mode method called to get mode options layout
                                            self.graph_type(
                                                graph_mode1,
                                                graph_mode2,
                                                graph_mode3,
                                                graph_mode4,
                                            ),
                                            # confirm dialog method called to get popup layout
                                            dataframe_csv_download,
                                            # button method called to get button layout
                                            self.submit_button(
                                                submit_text,
                                                submit_id,
                                                submit_name,
                                                submit_class,
                                            ),
                                            # Dashboard return button
                                            dashboard_return_btn,
                                            # page loader method called to get loader layout
                                            self.page_loader(
                                                loader_id,
                                                loader_content_id,
                                                loader_type,
                                                loader_fullscreen,
                                                color,
                                                loading_state,
                                            ),
                                            # Notification system setup
                                            dmc.MantineProvider(
                                                dmc.NotificationsProvider(
                                                    [
                                                        html.Div(
                                                            id="notify_container",
                                                            children=[],
                                                        )
                                                    ],
                                                    position="top-right",
                                                )
                                            ),
                                        ],
                                        width=2,
                                    ),
                                ]
                            )
                        ],
                        fluid=True,
                    ),
                ],
                className="graph_layout",
            ),
            color="light",
        )
        return section_layout

    def date_picker(self, date_range_id: str) -> str:
        """_date range component layout structure_

        Args:
            date_range_id (_string_): _date_range id name_

        Returns:
            _string_: _component layout structure_
        """
        date_picker = dcc.DatePickerRange(
            id=date_range_id,
            className="date_range",
            start_date=self._cloud_obj.dflt_start_date,
            end_date=self._cloud_obj.dflt_end_date,
            month_format="DD MMM YY",
            display_format="DD MMM YY",
            min_date_allowed=self._cloud_obj.calendar_date_range()[0],
            max_date_allowed=self._cloud_obj.calendar_date_range()[1],
            # persistence=True,
            # persistence_type='session',
            # persisted_props=['start_date', 'end_date']
            # start_date_placeholder_text='Select a date!',
            # end_date_placeholder_text='Select a date!',
        )
        return date_picker

    def graph_chart(self, graph_name: str) -> str:
        """_graphchart component layout structure_

        Args:
            graph_name (_string_): _graph id name_

        Returns:
            _string_: _component layout structure_
        """
        graph_chart = dcc.Graph(
            id=graph_name,
            figure=px.line(x=[0], y=[0]),
            config={"displayModeBar": True},
        )
        return graph_chart

    def categories(self, categories: str) -> str:
        """_categories component layout structure_

        Args:
            categories (_string_): _categories id name_

        Returns:
            _string_: _component layout structure_
        """
        categories = dcc.Dropdown(
            id=categories,
            className="dropdown catgrs_slct",
            options=[
                {"label": categories, "value": categories}
                for categories in self._cloud_obj.get_categories()["category"].unique()
            ],
            clearable=True,
            placeholder="Select Categories",
        )
        return categories

    def sub_categories(self, subcategories: str) -> str:
        """_sub categories component layout structure_

        Args:
            subcategories (_string_): _sub categories id name_

        Returns:
            _string_: _component layout structure_
        """
        subcategories = dcc.Dropdown(
            id=subcategories,
            className="dropdown subcatgrs_slct",
            options={"label": "", "value": ""},
            clearable=True,
            multi=True,
            placeholder="Select Sub Categories",
        )
        return subcategories

    def graph_type(
        self, graph_mode1: str, graph_mode2: str, graph_mode3: str, graph_mode4: str
    ) -> str:
        """_Graph mode component layout structure_

        Args:
            graph_mode1 (_string_): _mode1 id name_
            graph_mode2 (_string_): _mode2 id name_
            graph_mode3 (_string_): _mode3 id name_

        Returns:
            _string_: _component layout structure_
        """
        mode_choose = [
            {"id": graph_mode1, "mode": "mode1", "text": "Line"},
            {"id": graph_mode2, "mode": "mode2", "text": "Scatter"},
            {"id": graph_mode3, "mode": "mode3", "text": "Histogram"},
            {"id": graph_mode4, "mode": "mode4", "text": "Detection1"},
        ]
        graph_type = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            item["text"],
                            id=item["id"],
                            value=item["mode"],
                            size="sm",
                            className="me-1 graph_slct_btn",
                            disabled=True,
                        ),
                    ],
                    width=4,
                )
                for item in mode_choose  # user for loop to show graph mode option
            ],
            style={"marginBottom": "5px"},
        )
        return graph_type

    def confirm_dialog(
        self,
        submit_id: str,
        download_id: str,
        button_id: str,
        button_text: str,
        message_text: str,
    ) -> str:
        """_Confirm dialog popup component layout structure_

        Args:
            submit_id (_string_): _submit button id_
            download_id (_string_): _download location id_
            button_id (_string_): _button id name_
            button_text (_string_): _button text_
            message_text (_string_): _button message text_

        Returns:
            _string_: _Component layout structure_
        """
        confirm_dialog = dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.ConfirmDialogProvider(
                            children=dbc.Button(
                                button_text,
                                id=button_id,
                                size="sm",
                                color="success",
                                className="me-1 download_csv",
                                disabled=True,
                            ),
                            id=submit_id,
                            message=message_text,
                        ),
                        dcc.Download(id=download_id),
                    ],
                    width=4,
                ),
            ]
        )
        return confirm_dialog

    def page_loader(
        self,
        loader_id: str,
        content_id: str,
        loader_type: str,
        fullscreen: str,
        color: str,
        status: str,
    ) -> str:
        """_Page loader component layout structure_

        Args:
            loader_id (_string_): _loader id _
            content_id (_string_): _loader load data id_
            loader_type (_string_): _loading type feature_
            fullscreen (_boolean_): _load fullscreen or not_
            color (_hexa_): _choosing color code_
            status (_boolean_): _activation of loader_

        Returns:
            _string_: _Component layout structure_
        """
        page_loader = dcc.Loading(
            id=loader_id,
            children=[html.Div([html.Div(id=content_id)])],
            type=loader_type,
            fullscreen=fullscreen,
            color=color,
            loading_state={"is_loading": status},
        )
        return page_loader

    def submit_button(
        self, button_name: str, button_id: str, button_value: str, button_classname: str
    ) -> str:
        """_submit button component layout structure_
        Args:
            button_name (_string_): _button name text_
            button_id (_string_): _button id name_
            button_value (_string_): _button value text_
            button_classname (_string_): _stylesheet class name_
        Returns:
            _string_: _component layout structure_
        """
        button = dbc.Button(
            button_name,
            id=button_id,
            value=button_value,
            size="lg",
            className=button_classname,
            disabled=True,
        )
        return button

    def math_formula(self, formula_id: str) -> str:
        """_Math formula component layout structure_
        Args:
            formula_id (_string_): _id name_
        Returns:
            _string_: _component layout structure_
        """
        formulas = [
            {"label": "add", "value": 1, "title": "add"},
            {"label": "subtract", "value": 2, "title": "subtract"},
            {"label": "multiply", "value": 3, "title": "multiply"},
            {"label": "devide", "value": 4, "title": "devide"},
            {"label": "calibrate", "value": 5, "title": "calibrate"},
        ]  # formula title for 3rd layout graph
        math_formula = dcc.Dropdown(
            id=formula_id,
            className="dropdown formula_slct",
            options=[
                {
                    "label": formula["label"],
                    "value": formula["value"],
                    "title": formula["title"],
                }
                for formula in formulas[:]
            ],
            clearable=False,
            placeholder="Select formula",
        )
        return math_formula

    def x_axis_variable(self, x_axis_id: str) -> str:
        """_x_axis component layout structure_

        Args:
            x_axis_id (_string_): _x axis variable id name_

        Returns:
            _string_: _x_axis component layout structure_
        """
        x_axis_id = dcc.Dropdown(
            id=x_axis_id,
            className="dropdown catgrs_slct",
            options=[
                {"label": x_axis, "value": x_axis, "title": x_axis}
                for x_axis in self._cloud_obj.get_categories()[
                    "variable"
                ].drop_duplicates()
            ],
            clearable=False,
            placeholder="Choose X Axis",
        )
        return x_axis_id

    def timestamp_resampling(self, sampling_id: str) -> str:
        """_timestamp resampling layout structure_

        Args:
            sampling_id (_string_): _id name_

        Returns:
            _string_: _resampling information_
        """
        sampling = [
            {"title": "1 Minute", "value": "1Min", "label": "1 Minute"},
            {"title": "5 Minute", "value": "5Min", "label": "5 Minute"},
            {"title": "10 Minute", "value": "10Min", "label": "10 Minute"},
            {"title": "30 Minute", "value": "30Min", "label": "30 Minute"},
            {"title": "60 Minute", "value": "60Min", "label": "60 Minute"},
            {"title": "1 Day", "value": "1440Min", "label": "1 Day"},
        ]
        resampling = dcc.Dropdown(
            id=sampling_id,
            className="dropdown formula_slct",
            options=[
                {
                    "label": sample["label"],
                    "value": sample["value"],
                    "title": sample["title"],
                }
                for sample in sampling[:]
            ],
            clearable=False,
            value="1Min",
        )
        return resampling

    def dashboard_button(self, button_name: str, button_classname: str) -> str:
        """_dashboard button component layout structure_
        Args:
            button_name (_string_): _button name text_
            button_id (_string_): _button id name_
            button_value (_string_): _button value text_
            button_classname (_string_): _stylesheet class name_
        Returns:
            _string_: _component layout structure_
        """
        button = dbc.Button(
            button_name, size="lg", className=button_classname, href="/dashboard"
        )
        return button
