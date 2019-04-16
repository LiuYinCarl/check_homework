from functools import wraps
from flask import Flask, request, session, render_template, redirect, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:7873215@127.0.0.1:3306/check_homework'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'squirrel'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(40))
    email = db.Column(db.String(80), unique=True)


@app.before_first_request
def create_db():
    db.drop_all()
    db.create_all()

    admin = User(username='admin', password='root', email='admin@example.com')
    db.session.add(admin)

    guestes = [User(username='guest1', password='guest1', email='guest1@example.com'),
               User(username='guest2', password='guest2', email='guest2@example.com'),
               User(username='guest3', password='guest3', email='guest3@example.com')]
    db.session.add_all(guestes)
    db.session.commit()


def valid_login(username, password):
    user = User.query.filter(and_(User.username == username, User.password == password)).first()
    return True if user else False


def valid_regist(username, email):
    user = User.query.filter(or_(User.username == username, User.email == email)).first()
    return False if user else True


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get('username'):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login', next=request.url))

    return wrapper


# 1.主页
@app.route('/')
def home():
    return render_template('home.html', username=session.get('username'))


# 2.登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            flash("成功登录！")
            session['username'] = request.form.get('username')
            return redirect(url_for('home'))
        else:
            error = '错误的用户名或密码！'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/regist', methods=['GET', 'POST'])
def regist():
    error = None
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            error = 'two password is not equal'
        elif valid_regist(request.form['username'], request.form['email']):
            user = User(username=request.form['username'],
                        password=request.form['password1'],
                        email=request.form['email'])
            db.session.add(user)
            db.session.commit()
            flash('regist success')
            return redirect(url_for('login'))
        else:
            error = 'username or email is registed'

    return render_template('regist.html', error=error)


@app.route('/panel')
@login_required
def panel():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    return render_template('panel.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
