# -*- coding: utf-8 -*-

from flask import Blueprint, render_template

onair = Blueprint('onair', __name__, url_prefix='/onair')


@onair.route('/', methods=['GET'])
def index():
    return render_template('onair/index.html')
