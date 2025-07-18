import dash_bootstrap_components as dbc
from dash import html

p404_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H2("The Page Does not exist"),
                                html.Br(),
                                html.P("Contact with developer"),
                                dbc.Button(
                                    "Back Home", href="/", size="lg", className="me-1"
                                ),
                            ],
                            width={"size": 8},
                        ),
                    ],
                    align="center",
                    justify="center",
                )
            ]
        )
    ],
    className="page-404",
)
