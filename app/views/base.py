from app.utils.auth_func import login_required
from flask import session, render_template, Blueprint
from app.models import User

base = Blueprint('base', __name__)


@base.route('/')
@base.route('/home')
def home():
    return render_template('home.html', email=session.get('email'))


@base.route('/panel')
@login_required
def panel():
    email = session.get('email')
    user = User.query.filter(User.email == email).first()
    return render_template('panel.html', user=user)
