import dash_bootstrap_components as dbc
from dash import html

# page footer section
footer_layout = html.Footer(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    "© 2023 Cockpit. All rights reserved BOBST Manchester LTD."
                                )
                            ]
                        ),
                    ],
                    align="center",
                    justify="center",
                ),
            ]
        ),
    ],
    className="content-footer",
)
