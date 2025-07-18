import dash_bootstrap_components as dbc
from dash import html


from app import app

# header layout section
header_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Img(
                                    src=app.get_asset_url("images/logo.svg"),
                                    height="30px",
                                )
                            ]
                            
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
            ]
        ),
    ],
    className="header_section",
)
