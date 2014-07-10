# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, send_from_directory, abort
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from .models import User, UserDetail
from rootio.decorators import admin_required
from rootio.settings.forms import ProfileCreateForm
from ..extensions import db


user = Blueprint('user', __name__, url_prefix='/user')


@user.route('/')
@login_required
def index():
    if not current_user.is_authenticated():
        abort(403)
    return render_template('user/index.html', user=current_user)


@user.route('/<int:user_id>/profile')
def profile(user_id):
    user = User.get_by_id(user_id)
    return render_template('user/profile.html', user=user)


@user.route('/<int:user_id>/avatar/<path:filename>')
@login_required
def avatar(user_id, filename):
    dir_path = os.path.join(APP.config['UPLOAD_FOLDER'], 'user_%s' % user_id)
    return send_from_directory(dir_path, filename, as_attachment=True)


@user.route('/manager/')
@login_required
@admin_required
def user_dashboard():
    users = User.query.all()
    return render_template('user/manager.html', user=current_user, users=users)


@user.route('/add/', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    form = ProfileCreateForm()
    if form.validate_on_submit():
        _user = User()
        _user.user_detail = UserDetail()
        form.populate_obj(_user)
        form.populate_obj(_user.user_detail)
        db.session.add(_user)
        db.session.commit()
    return render_template('user/user.html', active="profile", form=form)