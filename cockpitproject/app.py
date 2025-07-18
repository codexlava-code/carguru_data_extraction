import dash_bootstrap_components as dbc
from jupyter_dash import JupyterDash
from flask import Flask
from flask_login import LoginManager

from apps.db_model.models import User
from apps.config import CONFIG


# Initialize the app application setup with flask server
# (server, stylesheet, callback_exceptions,prevent_initial)
app = JupyterDash(
    __name__,
    server=Flask(__name__, instance_relative_config=False),
    title="BOBST Manchester LTD Machine Diagnosis and analytics tools",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "assets/css/style.css",  # Custom css
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale: 1"},
    ],
    suppress_callback_exceptions=True,
    serve_locally=True,
    prevent_initial_callbacks=True,
)

server = app.server
# to manage the secert key!
app.server.secret_key = CONFIG.get("SECRET_KEY")

# Authenticaton login system
login_manager = LoginManager(app.server)
login_manager.login_view = "/login"


@login_manager.user_loader
def load_user(user_id):
    """_load user information_

    Args:
        user_id (_int_): _get user id number_

    Returns:
        _int_: _user_id primary key of our user table, use to query for the user._
    """
    return User.select().where(User.id == int(user_id)).first()