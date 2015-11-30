import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

application = Flask(__name__)
application.config.from_object('config')
db = SQLAlchemy(application)


