import os
from flask import Flask
from app.models import db
from redis import Redis


def register_blueprint(_app):
    from app.views.auth import auth
    from app.views.base import base
    from app.views.email import email
    # from app.views.duplicate import duplicate
    from app.views.file import file

    _app.register_blueprint(auth)
    _app.register_blueprint(base)
    _app.register_blueprint(email)
    # _app.register_blueprint(duplicate)
    _app.register_blueprint(file)


def create_app():
    _app = Flask(__name__)
    _app.config.from_object('secure')
    _app.config.from_object('settings')
    db.init_app(_app)

    register_blueprint(_app)
    return _app


redis_conn = Redis(db=1)

base_dir = os.path.dirname(__file__)
attachment_dir = '{0}/../Attachments'.format(base_dir)
temp_dir = '{0}/../Attachments/temp'.format(base_dir)





