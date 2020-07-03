from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import os

db = SQLAlchemy()
login = LoginManager()
BASEDIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(BASEDIR, 'static')


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        os.path.join(BASEDIR, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'this is secret'
    db.init_app(app)
    login.init_app(app)
    db.create_all(app=app)
    print("app started")
    return app
