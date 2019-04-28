from app.models import User, db
from flask import request, session, redirect, render_template, url_for, flash, Blueprint
from app.utils.auth_func import valid_login, valid_regist

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['email'], request.form['password']):
            session['email'] = request.form.get('email')
            return redirect(url_for('base.home'))
        else:
            error = '错误的用户名或密码！'

    return render_template('login.html', error=error)


@auth.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('base.home'))


@auth.route('/regist', methods=['GET', 'POST'])
def regist():
    error = None
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            error = 'two password is not equal'
        elif valid_regist(request.form['email']):
            user = User(email=request.form['email'],
                        password=request.form['password1'])
            db.session.add(user)
            db.session.commit()
            flash('regist success')
            return redirect(url_for('auth.login'))
        else:
            error = 'email is registed'
    return render_template('regist.html', error=error)
