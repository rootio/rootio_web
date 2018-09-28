# -*- coding: utf-8 -*-

import os
import hashlib

from datetime import datetime

from flask import Blueprint, render_template, current_app, request, flash, abort
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _

from ..extensions import db
from ..user import User, UserDetail
from ..utils import allowed_file, make_dir
from .forms import ProfileForm, PasswordForm
from ..user.constants import USER_ROLE, ADMIN


settings = Blueprint('settings', __name__, url_prefix='/settings')


@settings.route('/profile', methods=['GET', 'POST'], defaults={'user_id': None})
@settings.route('/profile/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if current_user.id != user_id:
        if current_user.role != USER_ROLE[ADMIN]:
            abort(403)

    if user_id:
        edit = True
        user = User.query.get(user_id)
    else:
        edit = False
        user = User.query.filter_by(name=current_user.name).first_or_404()
    if not user.user_detail:
        user.user_detail = UserDetail()
    form = ProfileForm(obj=user.user_detail,
                       email=user.email,
                       role_code=user.role_code,
                       status_code=user.status_code,
                       next=request.args.get('next'))

    if form.validate_on_submit():

        if form.avatar_file.data:
            upload_file = request.files[form.avatar_file.name]
            if upload_file and allowed_file(upload_file.filename):
                # Don't trust any input, we use a random string as filename.
                # or use secure_filename:
                # http://flask.pocoo.org/docs/patterns/fileuploads/

                user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], "user_%s" % user.id)
                current_app.logger.debug(user_upload_dir)

                make_dir(user_upload_dir)
                root, ext = os.path.splitext(upload_file.filename)
                today = datetime.now().strftime('_%Y-%m-%d')
                # Hash file content as filename.
                hash_filename = hashlib.sha1(upload_file.read()).hexdigest() + "_" + today + ext
                user.avatar = hash_filename

                avatar_ab_path = os.path.join(user_upload_dir, user.avatar)
                # Reset file curso since we used read()
                upload_file.seek(0)
                upload_file.save(avatar_ab_path)

        form.populate_obj(user)
        form.populate_obj(user.user_detail)

        db.session.add(user)
        db.session.commit()

        flash(_('Public profile updated.'), 'success')

    return render_template('settings/profile.html', user=user,
                           active="profile", form=form, edit=edit)


@settings.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = PasswordForm(next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)
        user.password = form.new_password.data

        db.session.add(user)
        db.session.commit()

        flash(_('Password updated.'), 'success')

    return render_template('settings/password.html', user=user,
                           active="password", form=form)
