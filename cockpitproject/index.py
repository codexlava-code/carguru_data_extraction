from dash import html, dcc

from app import app
from apps.home import home_layout
from apps.back_end.utils import nav_callback
from apps.back_end.utils import (
    notification_callback,
    download_callback,
)
from apps.back_end.diagnostic.machine_diags import (
    first_diags_callback,
    second_diags_callback,
    third_diags_callback,
    fourth_diags_callback,
)

app.layout = html.Div(
    [
        dcc.Store(id="store"),
        dcc.Store(id="machine_mem", storage_type="session"),
        dcc.Store(id="login_status", storage_type="session"),
        dcc.Location(id="page_url", refresh=False),
        dcc.Location(id="logout", refresh=True),
        html.Div(id="page_content", className="content"),
    ]
)


#Running the app
app.run_server(
    port="8080",
    debug=True,
    dev_tools_hot_reload=True,
    dev_tools_ui=True,
    dev_tools_serve_dev_bundles=True,
    dev_tools_hot_reload_watch_interval=True,
)
