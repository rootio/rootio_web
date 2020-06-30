# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user

from rootio.user import ADMIN
from .forms import GovernanceMeetingForm
from ..extensions import db, csrf
from ..onair import GovernanceMeeting
from ..radio.models import Network


governance = Blueprint('governance', __name__, url_prefix='/governance')


@governance.route('/')
@login_required
def index():
    # re-write using ORM
    # Filter by network when Track contains network id, filter by uploader
    status_query = "select ct.id, ct.name \"track\", rct.name \"content type\", count(*) \"uploads\" , " \
                   "(select count(*) from radio_program where structure like '%'||ct.description||'%') " \
                   "\"subscriptions\" from content_track as ct join content_type as rct on \"ct\".type_id = rct.id " \
                   "join content_uploads as cu on ct.id = cu.track_id  group by ct.id, rct.name"
    contents = db.session.execute(status_query)
    return render_template('content/index.html', content=contents, active="Status")


@governance.route('/meetings')
@login_required
def meetings():
    if current_user.role_code == ADMIN:
        networks = Network.query.all()
    else:
        networks = current_user.networks

    network_ids = [network.id for network in networks]
    all_meetings = db.session.query(GovernanceMeeting).filter(GovernanceMeeting.archived != True).filter(Network.id.in_(network_ids)).all()
    return render_template('governance/governance_meetings.html', meetings=all_meetings, active='Meetings')


@governance.route('/meetings/<int:meeting_id>/archive', methods=['GET'])
@login_required
def archive_meeting(meeting_id):
    meeting = GovernanceMeeting.query.filter_by(id=meeting_id).first_or_404()
    meeting.archived = True
    db.session.add(meeting)
    db.session.commit()
    return redirect(url_for('governance.meetings'))


@governance.route('/meetings/<int:track_id>', methods=['GET', 'POST'])
@login_required
def edit_meeting(meeting_id):
    meeting = GovernanceMeeting.query.filter_by(id=meeting_id).first_or_404()
    form = GovernanceMeetingForm(obj=meeting)

    if form.validate_on_submit():
        form.populate_obj(meeting)
        db.session.add(meeting)
        db.session.commit()
        flash(_('Meeting updated.'), 'success')
    return render_template('governance/governance_meeting.html', meeting=meeting, form=form, active="Meetings")


@governance.route('/meetings/add/', methods=['GET', 'POST'])
@login_required
def add_meeting():
    form = GovernanceMeetingForm(request.form)
    meeting = None
    if form.validate_on_submit():

        cleaned_data = form.data  # make a copy
        cleaned_data['creator_id'] = current_user.id
        cleaned_data.pop('submit', None)  # remove submit field from list
        meeting = GovernanceMeeting(**cleaned_data)  # create new object from data
        db.session.add(meeting)
        db.session.commit()
        flash(_('Meeting created.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')
    return render_template('governance/governance_meeting.html', meeting=meeting, form=form, active="Meetings")

