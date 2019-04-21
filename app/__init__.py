from flask import Flask
from app.models import db


def register_blueprint(_app):
    from app.auth import auth
    from app.base import base
    from app.download import download

    _app.register_blueprint(auth)
    _app.register_blueprint(base)
    _app.register_blueprint(download)


def create_app():
    _app = Flask(__name__)
    _app.config.from_object('secure')
    _app.config.from_object('settings')
    db.init_app(_app)

    register_blueprint(_app)
    return _app
