from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

"""Initialises application and other modules of the application"""
app = Flask(__name__)

""" Secret key was gotten by using a python interpreter and importing the secrets module
    and then using 'secrets.token_hex(16)' to get a 16 byte secret token, this is necessary for the flask application to run"""

app.config["SECRET_KEY"] = "1deef2f0b5b64295bfe291975201d7c9"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://root:finalyearproject@grapereview.ckmg0nb39mlo.eu-west-1.rds.amazonaws.com/grapereview"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"
""" imports routes """
from winesite import routes
