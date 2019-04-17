from functools import wraps
from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from flask_redis import FlaskRedis

from app.helper import Saver, EmailSpider, to_timestamp

app = Flask(__name__)

db = SQLAlchemy(app)
redis_store = FlaskRedis()
redis_store.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:7873215@127.0.0.1:3306/check_homework'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['REDIS_URL'] = 'redis://'
app.secret_key = 'squirrel'


# models
# ====================================

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


# view functions
# ====================================

@app.route('/test_redis')
def test_redis():
    redis_store.set('name', 'carl')
    return redis_store.get('name')


@app.route('/')
def home():
    return render_template('home.html', username=session.get('username'))


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


@app.route('/check_email', methods=['GET', 'POST'])
@login_required
def check_email():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    error = None
    if request.method == 'POST':
        # if valid_regist(request.form['email'], request.form['email_password']):
        email = request.form['email']
        email_password = request.form['email_password']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        report_name = request.form['report_name']
        send_receipt = request.form.getlist('send_receipt')
        start_time = to_timestamp(start_time)
        end_time = to_timestamp(end_time)

        saver = Saver(email, email_password,
                      start_time, end_time,
                      report_name, send_receipt)
        email_sender = EmailSpider(saver)
        email_sender.run()
        return render_template('check_email.html', success=True, error=error)
    # else:
    #     error = 'email error'
    return render_template('check_email.html', user=user, error=error)


if __name__ == '__main__':
    app.run(debug=True)
