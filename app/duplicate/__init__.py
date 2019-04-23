from flask import Blueprint

duplicate = Blueprint('duplicate', __name__)

from . import views