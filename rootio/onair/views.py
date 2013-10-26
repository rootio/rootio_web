# -*- coding: utf-8 -*-

import os

from flask import g, current_app, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _

from .models import OnAirProgram

from ..decorators import returns_json
from ..utils import error_dict
from ..extensions import db

onair = Blueprint('onair', __name__, url_prefix='/onair')

@onair.route('/', methods=['GET'])
def index():
    return render_template('onair/index.html')