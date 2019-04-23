from flask import Flask
from app.models import db


def register_blueprint(_app):
    from app.auth import auth
    from app.base import base
    from app.download import download
    from app.duplicate import duplicate
    from app.upload import upload

    _app.register_blueprint(auth)
    _app.register_blueprint(base)
    _app.register_blueprint(download)
    _app.register_blueprint(duplicate)
    _app.register_blueprint(upload)


def create_app():
    _app = Flask(__name__)
    _app.config.from_object('secure')
    _app.config.from_object('settings')
    db.init_app(_app)

    register_blueprint(_app)
    return _app
