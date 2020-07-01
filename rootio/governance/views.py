# -*- coding: utf-8 -*-
import os
import string
import urllib

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user

from rootio.config import DefaultConfig
from rootio.content import ContentUploads
from rootio.user import ADMIN
from telephony.cereproc.cereproc_rest_agent import CereprocRestAgent
from .forms import GovernanceMeetingForm
from ..extensions import db, csrf
from ..onair import GovernanceMeeting
from ..radio.models import Network


governance = Blueprint('governance', __name__, url_prefix='/governance')


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


@governance.route('/meetings/<int:meeting_id>', methods=['GET', 'POST'])
@login_required
def edit_meeting(meeting_id):
    meeting = GovernanceMeeting.query.filter_by(id=meeting_id).first_or_404()
    form = GovernanceMeetingForm(obj=meeting)

    if form.validate_on_submit():
        form.populate_obj(meeting)
        db.session.add(meeting)
        db.session.commit()
        if meeting.track is not None:
            if create_media_for_track(meeting.id, meeting.meeting_date, meeting.stations, meeting.agenda,
                                      meeting.minutes, meeting.attendees, meeting.track_id):
                flash(_('Meeting created. An audio transcript for the meeting has been added to the selected track'),
                      'success')
            else:
                flash(_('Meeting created. An audio transcript for the meeting could not be created'), 'warn')
        else:
            flash(_('Meeting created.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')
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
        db.session.flush()
        db.session.commit()
        if meeting.track is not None:
            if create_media_for_track(meeting.id, meeting.meeting_date, meeting.stations, meeting.agenda, meeting.minutes, meeting.attendees, meeting.track_id):
                flash(_('Meeting created. An audio transcript for the meeting has been added to the selected track'), 'success')
            else:
                flash(_('Meeting created. An audio transcript for the meeting could not be created'), 'warn')
        else:
            flash(_('Meeting created.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')
    return render_template('governance/governance_meeting.html', meeting=meeting, form=form, active="Meetings")


def create_media_for_track(meeting_id, meeting_date, stations, agenda, minutes, attendees, track_id):
    # get the text first.
    reasonable_date = meeting_date.strftime('%A %d of %B %Y')
    file_name_date = meeting_date.strftime('%d %B %Y')
    my_path = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(my_path, "../templates/governance/meeting_summary_template.txt")
    body = string.Template(open(file_path).read())
    details = {"meeting_date": reasonable_date, "stations": ",".join(map(lambda x: x.name, stations)), "agenda": agenda, "minutes": minutes, "attendees":attendees}
    tts_text = body.substitute(details)

    # generate the audio file
    tts_agent = CereprocRestAgent(DefaultConfig.CEREPROC_SERVER, DefaultConfig.CEREPROC_USERNAME,
                                             DefaultConfig.CEREPROC_PASSWORD)
    tts_data = tts_agent.get_cprc_tts(tts_text)

    # download audio file to directory for track
    try:
        if not os.path.exists(os.path.join(DefaultConfig.CONTENT_DIR, 'media', str(track_id))):
            os.makedirs(os.path.join(DefaultConfig.CONTENT_DIR, 'media', str(track_id)))
        urllib.urlretrieve(tts_data[0],
                               os.path.join(DefaultConfig.CONTENT_DIR, 'media', str(track_id),  str(meeting_id) + ".mp3"))
        # create a track file - but only if none exists for this meeting
        content = ContentUploads.query.filter(ContentUploads.uri == "{0}/{1}/{2}".format('media', str(track_id), str(meeting_id) + ".mp3")).first()
        if content is None:
            content = ContentUploads()
        content.uri = "{0}/{1}/{2}".format('media', str(track_id), str(meeting_id) + ".mp3")
        content.track_id = track_id
        content.uploaded_by = current_user.id
        content.name = "Meeting on " + file_name_date
        db.session.add(content)
        db.session.flush()
        db.session.commit()
        return True
    except Exception as e:
        return False