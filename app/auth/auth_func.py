from . import auth
from sqlalchemy import and_
from functools import wraps
from flask import session, redirect, url_for, request


def valid_login(email, password):
    from app.models import User
    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    return True if user else False


def valid_regist(email):
    from app.models import User
    user = User.query.filter(User.email == email).first()
    return False if user else True


# todo 增加对邮箱的验证，防止伪造sesion中的无效邮箱
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('email'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.url))

    return wrapper



