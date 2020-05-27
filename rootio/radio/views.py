# -*- coding: utf-8 -*-

import json
import socket
from datetime import datetime
import time
import re
import io
import re
import os
import glob
from itertools import islice
from os import path
from string import Template

from simplejson.scanner import JSONDecodeError
from sqlalchemy import Date, cast

import dateutil.parser
from dateutil import rrule
from flask import Blueprint, render_template, request, flash, json, abort
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user
from pytz import timezone
import arrow

from rootio.user.constants import ACCEPTED, REJECTED
from .forms import StationForm, NetworkForm, ProgramForm, BlockForm, LocationForm, \
    ScheduleProgramForm, PersonForm
from .models import Station, Program, ScheduledBlock, ScheduledProgram, Location, Person, Network, StationEvent
from ..config import DefaultConfig
from ..content.models import ContentMusicPlaylist, ContentTrack, ContentPodcast, ContentStream
from .models import ContentType
from ..decorators import returns_json, returns_flat_json
from ..extensions import db, csrf
from ..user.models import User, RootioUser, NetworkInvitation
from ..utils import error_dict, fk_lookup_form_data, format_log_line, events_action_display_map
from rootio.user import ADMIN, PENDING, redirect, url_for
from sqlalchemy import text
import pytz

radio = Blueprint('radio', __name__, url_prefix='/radio')


@radio.route('/', methods=['GET','POST'])
@login_required
def index():

    # any pending invitations
    invitations = NetworkInvitation.query.filter(NetworkInvitation.email == current_user.email)\
        .filter(NetworkInvitation.deleted == False).filter(NetworkInvitation.status_code == PENDING).all()

    # get all the user's networks and their stations
    if current_user.role_code == ADMIN:
        networks = Network.query.outerjoin(Station).join(User, Network.networkusers).all()
    else:
        networks = Network.query.outerjoin(Station).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('radio/index.html', active="Status", networks=networks, userid=current_user.id, now=datetime.now, invitations=invitations)


@radio.route('/invitation/<int:id>/<string:action>', methods=['GET'])
@login_required
def act_on_invitation(id, action):

    if action in ['accept', 'reject']:
        invitation = NetworkInvitation.query.filter(NetworkInvitation.email == current_user.email) \
            .filter(NetworkInvitation.deleted == False) \
            .filter(NetworkInvitation.status_code == PENDING) \
            .filter(NetworkInvitation.id == id).first_or_404()
        invitation.status_code = {'accept': ACCEPTED, 'reject': REJECTED}[action]
        db.session.add(invitation)
        if action == 'accept':
            current_user.networks.append(invitation.network)
            db.session.add(current_user)
        db.session.flush()
        db.session.refresh(current_user)
        db.session.commit()
        result = _('Invitation has been %s' % {'accept': 'accepted', 'reject': 'rejected'}[action])
    elif action == 'delete':
        invitation = NetworkInvitation.query.join(Network).filter(Network.networkusers.contains(current_user)) \
            .filter(NetworkInvitation.deleted == False) \
            .filter(NetworkInvitation.status_code == PENDING) \
            .filter(NetworkInvitation.id == id).first_or_404()
        invitation.deleted = True
        db.session.add(invitation)
        db.session.commit()
        result = _('Invitation has been deleted')
        flash(result, 'success')
        return redirect(url_for('user.invitations'))
    else:
        result = _('Unknown action specified')

    flash(result, 'success')
    return redirect(url_for('radio.index'))


@radio.route('/emergency/', methods=['GET'])
@login_required
def emergency():
    stations = Station.query.all()
    # demo, override station statuses
    for s in stations:
        s.status = "on"

    # end demo
    return render_template('radio/emergency.html', stations=stations)


@radio.route('/network/add/', methods=['GET', 'POST'])
@login_required
def network_add():
    form = NetworkForm(request.form)
    network = False

    if form.validate_on_submit():
        form_data = form.data  # copy it to remove items, it is immutable
        form_data.pop('submit', None)
        network = Network(**form_data)  # create new object from data

        # Associate creator with network - Fix this to use current_user, instead of querying new instance
        user = RootioUser.query.filter(RootioUser.id == current_user.id).first()
        network.networkusers.append(user)

        # Save the Network
        db.session.add(network)
        db.session.commit()
        flash(_('Network Created.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/network.html', network=network, form=form)


@radio.route('/station/', methods=['GET'])
@login_required
def list_stations():
    stations = Station.get_stations(current_user)
    # stations = Station.query.join(Network).join(User).filter(User.id == current_user.id).all()
    return render_template('radio/stations.html', stations=stations, active='Stations')


@radio.route('/station/<int:station_id>', methods=['GET', 'POST'])
@login_required
def station_definition(station_id):
    networks = current_user.networks
    station = Station.query.filter_by(id=station_id).first_or_404()

    if station.network.id not in [network.id for network in networks]:
        abort(403)

    form = StationForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Station updated.'), 'success')

    return render_template('radio/station.html', station=station, defaultConfig=DefaultConfig, form=form, active="Stations")


@radio.route('/station/add/', methods=['GET', 'POST'])
@login_required
def station_add():
    form = StationForm(request.form)
    station = None

    if form.validate_on_submit():
        try:
            cleaned_data = form.data  # make a copy
            cleaned_data.pop('submit', None)  # remove submit field from list
            cleaned_data.pop('phone_inline', None)  # and also inline forms
            cleaned_data.pop('location_inline', None)
            station = Station(**cleaned_data)  # create new object from data
            db.session.add(station)
            db.session.flush()
            db.session.refresh(station)

        #1) create SIP profile

            station.sip_username = "{0}{1}".format(DefaultConfig.DEFAULT_SIP_PREFIX, station.id)
            station.sip_password = DefaultConfig.DEFAULT_SIP_PASSWORD
            station.sip_port = DefaultConfig.DEFAULT_SIP_PORT
            station.sip_protocol = DefaultConfig.DEFAULT_SIP_TRANSPORT
            station.sip_server = DefaultConfig.DEFAULT_SIP_SERVER
            station.sip_reregister_period = DefaultConfig.DEFAULT_SIP_REREGISTER_PERIOD
            station.sip_stun_server = DefaultConfig.DEFAULT_STUN_SERVER
            station.is_high_bandwidth = True
            db.session.commit()
            station_status = _("Station created.")

        except Exception as e:
            station_status = _("Station creation failed.")

        # 2) Create FS profile
        try:
            my_path = os.path.abspath(os.path.dirname(__file__))
            file_path = os.path.join(my_path, "../templates/configuration/sip_profile_template.txt")
            filein = open(file_path)
            src = Template(filein.read())
            data = {"sip_username": station.sip_username}
            profile = src.substitute(data)
            sip_status = None

            with open(path.join(DefaultConfig.SIP_CONFIG_PATH, "{0}.xml".format(station.sip_username)), "w+") as conf_file:
                conf_file.write(str(profile))
                conf_file.flush()
            sip_status = _("SIP profile created.")
        except IOError as e:
            sip_status = _("SIP profile creation failed.")

        # 3) Reload Freeswitch
        reload_result = os.system("fs_cli -x \"reloadxml\"")
        reload_status = _({True: "SIP profile ready", False: "SIP profile not ready"}.get(reload_result == 0))

        flash("{0} {1} {2}".format(station_status, sip_status, reload_status), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/station.html', station=station, defaultConfig=DefaultConfig, form=form, active="Stations")


@radio.route('/program/', methods=['GET'])
@login_required
def programs():
    if current_user.role_code == ADMIN:
        programs = Program.query.filter(Program.program_type_id != 2).all()
    else:
        programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(
        User.id == current_user.id).filter(Program.program_type_id != 2).all()
    return render_template('radio/programs.html', programs=programs, active='Programs')


@radio.route('/program/<int:program_id>', methods=['GET', 'POST'])
@login_required
def program_definition(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()
    # form = ProgramForm(obj=program, program_structure="test", next=request.args.get('next'))

    # hosts in my network
    if current_user.role_code == ADMIN:
        hosts = Person.query.all()
        news = ContentTrack.query \
            .filter(ContentType.name == "News") \
            .filter(ContentTrack.deleted != True) \
            .join(ContentType) \
            .all()
        ads = ContentTrack.query \
            .filter(ContentType.name == "Advertisements") \
            .filter(ContentTrack.deleted != True) \
            .join(ContentType) \
            .all()
        medias = ContentTrack.query \
            .filter(ContentType.name == "Media") \
            .filter(ContentTrack.deleted != True) \
            .join(ContentType) \
            .all()
    else:
        networks = current_user.networks
        network_ids = [network.id for network in networks]
        medias = ContentTrack.query.join(ContentTrack.networks) \
            .filter(ContentTrack.deleted != True) \
            .filter(ContentType.name == "Media") \
            .filter(Network.id.in_(network_ids)) \
            .join(ContentType) \
            .all()
        news = ContentTrack.query.join(ContentTrack.networks) \
            .filter(ContentTrack.deleted != True) \
            .filter(ContentType.name == "News") \
            .filter(Network.id.in_(network_ids)) \
            .join(ContentType) \
            .all()
        ads = ContentTrack.query.join(ContentTrack.networks) \
            .filter(ContentTrack.deleted != True) \
            .filter(ContentType.name == "Advertisements") \
            .filter(Network.id.in_(network_ids)) \
            .join(ContentType) \
            .all()
        hosts = Person.query.join(Person.networks).filter(Network.id.in_(network_ids)).all()
        
    podcasts = ContentPodcast.query.all()
    community_contents = {"data": [{"type": "Ads", "category_id": "1"}, {"type": "Announcements", "category_id": "2"},
                                   {"type": "Greetings", "category_id": "3"}]}

    # render the program structure
    action_names = []
    try:
        program_json = json.loads(program.structure)
        for action in program_json:
            if 'name' in action:
                action_names.append(action['name'])
    except JSONDecodeError as e:
        print("error deserializing action names for program")
        print(e)

    program_actions = ",".join(action_names)

    form = ProgramForm(obj=program, program_structure=program_actions, next=request.args.get('next'))
    if form.validate_on_submit():
        form.populate_obj(program)

        db.session.add(program)

        scheduled_programs = ScheduledProgram.query\
                                             .filter_by(program_id=program_id)\
                                             .filter(cast(ScheduledProgram.end, Date) >= datetime.now())\
                                             .all()
        for prg in scheduled_programs:
            prg.updated_at=datetime.now()
            db.session.add(prg)

        db.session.commit()
        flash(_('Program updated.'), 'success')

    return render_template('radio/program.html', program=program, hosts=hosts, news=news, podcasts=podcasts, ads=ads,
                           medias=medias, community_contents=community_contents["data"], form=form, active="Programs")


@radio.route('/program/add/', methods=['GET', 'POST'])
@login_required
def program_add():
    form = ProgramForm(request.form)
    program = None

    # hosts in my network
    if current_user.role_code == ADMIN:
        hosts = Person.query.all()
        news = ContentTrack.query \
            .filter(ContentType.name == "News") \
            .filter(ContentTrack.deleted != True) \
            .join(ContentType) \
            .all()
        ads = ContentTrack.query \
            .filter(ContentType.name == "Advertisements") \
            .filter(ContentTrack.deleted != True) \
            .join(ContentType) \
            .all()
        medias = ContentTrack.query \
            .filter(ContentType.name == "Media") \
            .filter(ContentTrack.deleted != True) \
            .join(ContentType) \
            .all()
    else:
        networks = current_user.networks
        network_ids = [network.id for network in networks]
        medias = ContentTrack.query.join(ContentTrack.networks) \
            .filter(ContentTrack.deleted != True) \
            .filter(ContentType.name == "Media") \
            .filter(Network.id.in_(network_ids)) \
            .join(ContentType) \
            .all()
        news = ContentTrack.query.join(ContentTrack.networks) \
            .filter(ContentTrack.deleted != True) \
            .filter(ContentType.name == "News") \
            .filter(Network.id.in_(network_ids)) \
            .join(ContentType) \
            .all()
        ads = ContentTrack.query.join(ContentTrack.networks) \
            .filter(ContentTrack.deleted != True) \
            .filter(ContentType.name == "Advertisements") \
            .filter(Network.id.in_(network_ids)) \
            .join(ContentType) \
            .all()
        hosts = Person.query.join(Person.networks).filter(Network.id.in_(network_ids)).all()

    podcasts = ContentPodcast.query.all()
    community_contents = {"data": [{"type": "Ads", "category_id": "1"}, {"type": "Announcements", "category_id": "2"},
                                   {"type": "Greetings", "category_id": "3"}]}

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data.pop('program_structure')
        cleaned_data['program_type_id'] = 1
        program = Program(**cleaned_data)  # create new object from data
        program.deleted = False
        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/program.html', program=program, hosts=hosts, news=news, podcasts=podcasts, ads=ads,
                           medias=medias, community_contents=community_contents["data"], form=form, active="Programs")


@radio.route('/program/<int:program_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def program_delete(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()

    program.deleted = True

    try:
        db.session.add(program)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@radio.route('/music_program/', methods=['GET'])
@login_required
def list_music_programs():
    if current_user.role_code == ADMIN:
        music_programs = Program.query.filter(Program.program_type_id == 2).filter(Program.deleted ==  False).all()
    else:
        music_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(
        User.id == current_user.id).filter(Program.program_type_id == 2).filter(Program.deleted ==  False).all()
    return render_template('radio/music_programs.html', music_programs=music_programs, active='Music programs')


@radio.route('/music_program/add/', methods=['GET', 'POST'])
@login_required
def music_program_add():
    form = ProgramForm(request.form)
    program = None

    if current_user.role_code == ADMIN:
        playlists = ContentMusicPlaylist.query.join(Station).filter(ContentMusicPlaylist.deleted != True).all()  # Playlist->Station->Network->user
        streams = ContentStream.query.join(User, Network.networkusers).filter(
            User.id == current_user.id).all()  # created by -> user -> Network
    else:
        # Playlists and streams in my network
        playlists = ContentMusicPlaylist.query.join(Station).join(Network).join(User, Network.networkusers).filter(ContentMusicPlaylist.deleted != True).all()  # Playlist->Station->Network->user
        streams = ContentStream.query.join(User, Network.networkusers).filter(
            User.id == current_user.id).all()  # created by -> user -> Network

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data.pop('program_structure')
        cleaned_data['program_type_id'] = 2
        program = Program(**cleaned_data)  # create new object from data
        program.deleted = False
        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/music_program.html', program=program, playlists=playlists, streams=streams, form=form, active='Music programs')


@radio.route('/music_program/<int:music_program_id>', methods=['GET', 'POST'])
@login_required
def music_program_definition(music_program_id):
    music_program = Program.query.filter_by(id=music_program_id).first_or_404()

    if current_user.role_code == ADMIN:
        playlists = ContentMusicPlaylist.query.join(Station).join(Network).join(User, Network.networkusers).all() #Playlist->Station->Network->user
        streams = ContentStream.query.join(User, Network.networkusers).all() # created by -> user -> Network
    else:
        # TODO: Filter these by network
        playlists = ContentMusicPlaylist.query.join(Station).join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all() #Playlist->Station->Network->user
        streams = ContentStream.query.join(User, Network.networkusers).filter(User.id == current_user.id).all() # created by -> user -> Network

    # render the program structure
    action_names = []
    try:
        program_json = json.loads(music_program.structure)
        for action in program_json:
            if 'name' in action:
                action_names.append(action['name'])
    except ValueError:
        pass
    program_actions = ",".join(action_names)

    form = ProgramForm(obj=music_program, program_structure=program_actions, next=request.args.get('next'))
    if form.validate_on_submit():
        form.populate_obj(music_program)

        scheduled_programs = db.session.query(ScheduledProgram).filter(ScheduledProgram.program_id == music_program_id).filter(ScheduledProgram.end >= datetime.now()).all()
        for prg in scheduled_programs:
            prg.updated_at=datetime.utcnow() #.replace(tzinfo=timezone('UTC'))
            db.session.add(prg)

        db.session.add(music_program)
        db.session.commit()
        flash(_('Music Program updated.'), 'success')

    return render_template('radio/music_program.html', music_program=music_program, playlists=playlists,
                           streams=streams, form=form, active='Music programs')


@radio.route('/music_program/<int:music_program_id>/delete', methods=['GET'])
@login_required
@csrf.exempt
def music_program_delete(music_program_id):
    music_program = Program.query.filter_by(id=music_program_id).first_or_404()

    music_program.deleted = True

    try:
        db.session.add(music_program)
        db.session.commit()
    except:
        return '{"result": "failed" }'

    return '{"result": "ok" }'


@radio.route('/people/', methods=['GET'])
@login_required
def people():
    people = Person.query.all()
    return render_template('radio/people.html', people=people, active='people')


@radio.route('/people/<int:person_id>', methods=['GET', 'POST'])
def person_definition(person_id):
    person = Person.query.filter_by(id=person_id).first_or_404()
    form = PersonForm(obj=person, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(person)

        db.session.add(person)
        db.session.commit()
        flash(_('Person updated.'), 'success')

    return render_template('radio/person.html', person=person, form=form)


@radio.route('/people/add/', methods=['GET', 'POST'])
@login_required
def person_add():
    form = PersonForm(request.form)
    person = None

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        person = Person(**cleaned_data)  # create new object from data

        db.session.add(person)
        db.session.commit()
        flash(_('Person added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/person.html', person=person, form=form)


@radio.route('/location/add/ajax/', methods=['POST'])
@login_required
@returns_json
def location_add_ajax():
    data = json.loads(request.data)
    # handle floats individually
    float_values = ['latitude', 'longitude']
    for field in float_values:
        try:
            data[field] = float(data[field])
        except ValueError:
            response = {'status': 'error', 'errors': {field: _('Invalid ') + field}, 'status_code': 400}
            return response

    form = LocationForm(None, **data)  # use this format to avoid multidict-type issue
    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        location = Location(**cleaned_data)  # create new object from data
        db.session.add(location)
        db.session.commit()
        response = {'status': 'success', 'result': {'id': location.id, 'string': unicode(location)}, 'status_code': 200}
    elif request.method == "POST":
        # convert the error dictionary to something serializable
        response = {'status': 'error', 'errors': error_dict(form.errors), 'status_code': 400}
    return response


@radio.route('/block/', methods=['GET'])
def list_scheduled_blocks():
    scheduled_blocks = ScheduledBlock.query.all()
    # TODO, display only those that are scheduled on stations the user can view

    return render_template('radio/scheduled_blocks.html', scheduled_blocks=scheduled_blocks, active='blocks')


@radio.route('/block/<int:block_id>', methods=['GET', 'POST'])
def scheduled_block(block_id):
    block = ScheduledBlock.query.filter_by(id=block_id).first_or_404()
    form = BlockForm(obj=block, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(block)
        db.session.add(block)
        db.session.commit()
        flash(_('Block updated.'), 'success')

    return render_template('radio/scheduled_block.html', scheduled_block=block, form=form)


@radio.route('/block/add/', methods=['GET', 'POST'])
@login_required
def scheduled_block_add():
    form = BlockForm(request.form)
    block = None

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        block = ScheduledBlock(**cleaned_data)  # create new object from data

        db.session.add(block)
        db.session.commit()
        flash(_('Block added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/scheduled_block.html', block=block, form=form)


def send_scheduling_event(message):
    try:
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.connect((DefaultConfig.SCHEDULE_EVENTS_SERVER_IP, DefaultConfig.SCHEDULE_EVENTS_SERVER_PORT))
        sck.send(message)
        # sck.recv(1024)
        sck.close()
    except IOError:  # Socket errors, maybe service is not running
        return


@radio.route('/scheduleprogram/add/ajax/', methods=['POST'])
@login_required
@csrf.exempt
@returns_json
def schedule_program_add_ajax():
    data = json.loads(request.data)

    if 'program' not in data:
        return {'status': 'error', 'errors': 'program required', 'status_code': 200}
    if 'station' not in data:
        return {'status': 'error', 'errors': 'station required', 'status_code': 200}

    # lookup objects from ids
    # fk_errors = fk_lookup_form_data({'program':Program,'station':Station}, data)
    # if fk_errors:
    #    return fk_errors

    # Fix this. use form elements

    program = Program.query.filter(Program.id == data['program']).first()
    station = Station.query.filter(Station.id == data['station']).first()
    scheduled_program = ScheduledProgram()
    scheduled_program.station_id = data['station']
    scheduled_program.program_id = data['program']
    scheduled_program.start = dateutil.parser.parse(data['start'])
    scheduled_program.end = scheduled_program.start + program.duration
    scheduled_program.deleted = False

    db.session.add(scheduled_program)
    db.session.commit()

    # TODO: Add a send event for addition
    send_scheduling_event(json.dumps({"action": "add", "id": scheduled_program.id, "station": int(data['station'])}))

    return {'status': data, 'result': 1, 'status_code': 200}
    # return {'status':'success','result':{'id':scheduled_program.id},'status_code':200}


@radio.route('/scheduleprogram/delete_series/<_id>/', methods=['POST'])
@login_required
def delete_series(_id):
    station_id = request.args.get('station_id')

    station = Station.query.filter_by(id=station_id).first_or_404()

    utc_dt = datetime.now(pytz.utc)
    # apply time shift and put it in UTC time
    utc_shifted = utc_dt.astimezone(pytz.timezone(station.timezone)).strftime('%Y-%m-%d %H:%M:%S')

    scheduled_programs = ScheduledProgram.query.filter(ScheduledProgram.series_id == _id).filter(ScheduledProgram.start > utc_shifted).all()

    for s in scheduled_programs:
        s.deleted = True
        db.session.add(s)
        db.session.commit()
        send_scheduling_event(
            json.dumps({"action": "delete", "id": s.id, "station": s.station_id}))
    return ""


@radio.route('/scheduleprogram/delete/<int:_id>/', methods=['POST'])
@login_required
def delete_program(_id):
    scheduled_program = ScheduledProgram.query.filter(ScheduledProgram.id == _id).first()

    scheduled_program.deleted = True
    db.session.add(scheduled_program)
    db.session.commit()
    # TODO: Add a delete event send
    send_scheduling_event(
        json.dumps({"action": "delete", "id": scheduled_program.id, "station": scheduled_program.station_id}))
    return ""


@radio.route('/scheduleprogram/edit/ajax/', methods=['POST'])
@login_required
@csrf.exempt
@returns_json
def schedule_program_edit_ajax():

    data = json.loads(request.data)

    if 'scheduledprogram' not in data:
        return {'status': 'error', 'errors': 'scheduledprogram required', 'status_code': 400}

    scheduled_program = db.session.query(ScheduledProgram).get(data['scheduledprogram'])
    scheduled_program.start = arrow.get(data['start']).datetime
    scheduled_program.end = arrow.get(data['end']).datetime
    scheduled_program.deleted = False

    db.session.add(scheduled_program)
    db.session.flush()
    db.session.commit()

    # TODO: Add an edit event broadcast (stn, progid, actionTypeId)
    send_scheduling_event(
        json.dumps({"action": "update", "id": scheduled_program.id, "station": scheduled_program.station_id}))

    return {'status': 'success', 'result': {'id': scheduled_program.id}, 'status_code': 200}


@radio.route('/scheduleprogram/add/recurring_ajax/', methods=['POST'])
@login_required
@csrf.exempt
@returns_json
def schedule_recurring_program_ajax():
    """Schedule a recurring program"""
    data = json.loads(request.data)

    # ensure specified foreign key ids are valid
    # fk_errors = fk_lookup_form_data({'program':Program,'station':Station}, data)
    # if fk_errors:
    #   return fk_errors

    form = ScheduleProgramForm(None, **data)

    try:
        air_time = datetime.strptime(form.data['air_time'], '%H:%M').time()
    except ValueError:
        response = {'status': 'error', 'errors': {'air_time': 'Invalid time'}, 'status_code': 400}
        return response

    # if form.validate_on_submit():
    # save refs to form objects
    program = Program.query.filter(Program.id == form.data['program']).first()
    series_id = time.time()

    # fix for some broken recurrence rules
    if 'DTSTART=' in form.data['recurrence']:
        dtstart = re.search('DTSTART=([0-9]*T[0-9]*Z)', form.data['recurrence']).group(1)
        clean_rrule = re.sub(r'.DTSTART=[0-9]*T[0-9]*Z', '', form.data['recurrence'])
        if 'UNTIL=' in form.data['recurrence']:
            # "count" together with  "until" is deprecated as of datetime v2.7.5
            clean_rrule = re.sub(r'.COUNT=', '', clean_rrule)
    else:
        clean_rrule = form.data['recurrence']
        dtstart = str(datetime.now())

    # parse recurrence rule
    r = rrule.rrulestr(clean_rrule, dtstart=dateutil.parser.parse(dtstart))
    for instance in r[:365]:  # TODO: dynamically determine instance limit
        scheduled_program = ScheduledProgram()
        scheduled_program.station_id = data['station']
        scheduled_program.program_id = data['program']
        scheduled_program.series_id = series_id
        scheduled_program.deleted = False
        scheduled_program.start = datetime.combine(instance, air_time)  # combine instance day and air_time time
        scheduled_program.end = scheduled_program.start + program.duration
        db.session.add(scheduled_program)
    db.session.commit()

    # TODO: Add a send event for addition
    send_scheduling_event(json.dumps({"action": "add", "id": scheduled_program.id, "station": int(data['station'])}))
    response = {'status': 'success', 'result': {}, 'status_code': 200}
    # elif request.method == "POST":
    if form.errors:
        response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response


@radio.route('/station/<int:station_id>/scheduledprograms_color_feature.json', methods=['GET', 'POST'])
@returns_flat_json
def scheduled_programs_color_feature_json(station_id):
    if not ('start' in request.args and 'end' in request.args):
        return {'status': 'error', 'errors': 'scheduledprograms.json requires start and end', 'status_code': 400}

    start = request.args.get('start')
    end = request.args.get('end')
    
    sql = text('select * from scheduled_program_view where start >= :start and _end <= :end and station_id = :station_id;')
    sql = sql.bindparams(start=start, end=end, station_id=station_id)
    scheduled_programs = db.engine.execute(sql)   

    station = Station.query.filter_by(id=station_id).first_or_404()
    station_timezone = station.timezone
    
    resp = []
    for s in scheduled_programs:
        movable = datetime.now(pytz.timezone(station_timezone)) < s.start
        utc_dt = datetime.now(pytz.utc)
        # apply time shift and put it in UTC time
        utc_shifted = utc_dt.astimezone(pytz.timezone(station_timezone)).strftime('%Y-%m-%d %H:%M:%S')
        d = {'title': s.name,
            'start': s.start.isoformat(),
            'end': s._end.isoformat(),
            'id': s.id,
            'series_id': s.series_id,
            'color': s.color,
            'movable': movable,
            'now_timezone_utc_shifted': utc_shifted,
            }
    
        resp.append(d)
    return resp


@radio.route('/station/<int:station_id>/scheduledprograms.json', methods=['GET', 'POST'])
@returns_flat_json
def scheduled_programs_json(station_id):
    if not ('start' in request.args and 'end' in request.args):
        return {'status': 'error', 'errors': 'scheduledprograms.json requires start and end', 'status_code': 400}
    
    start = dateutil.parser.parse(request.args.get('start'))
    end = dateutil.parser.parse(request.args.get('end'))
    scheduled_programs = ScheduledProgram.query.filter_by(station_id=station_id) \
        .filter(ScheduledProgram.start >= start) \
        .filter(ScheduledProgram.end <= end) \
        .filter(ScheduledProgram.deleted != True)

    resp = []
    for s in scheduled_programs:

        movable = datetime.now(pytz.timezone(s.station.timezone)) < s.start
        utc_dt = datetime.now(pytz.utc)
        # apply time shift and put it in UTC time
        utc_shifted = utc_dt.astimezone(pytz.timezone(s.station.timezone)).strftime('%Y-%m-%d %H:%M:%S')
        d = {'title': s.program.name,
            'now_timezone_utc_shifted': utc_shifted,
            'start': s.start.isoformat(),
            'end': s.end.isoformat(),
            'id': s.id,
            'status': s.status,
            'series_id': s.series_id,
            'station_id': s.station.id,
            'movable': movable,
            'program_type_id': s.program.program_type_id}
    
        resp.append(d)
    return resp


@radio.route('/station/<int:station_id>/scheduledblocks.json', methods=['GET'])
@returns_flat_json
def scheduled_block_json(station_id):
    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station_id)

    if not ('start' in request.args and 'end' in request.args):
        return {'status': 'error', 'errors': 'scheduledblocks.json requires start and end', 'status_code': 400}

    # TODO: fullcalendar updates based on these params
    start = dateutil.parser.parse(request.args.get('start'))
    end = dateutil.parser.parse(request.args.get('end'))

    resp = []
    for block in scheduled_blocks:
        r = rrule.rrulestr(block.recurrence)
        for instance in r.between(start, end):
            d = {'title': block.name,
                 'start': datetime.combine(instance, block.start_time),
                 'end': datetime.combine(instance, block.end_time),
                 'id': block.id,
                 'isBackground': True,  # the magic flag that tells full calendar to render as block
                 }
            resp.append(d)
    return resp


@radio.route('/station/<int:station_id>/log', methods=['GET'])
@login_required
def station_logs(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    keys = []

    return render_template('radio/log.html',
                           station=station,
                           events_map=events_action_display_map, active='Stations'
    )


@radio.route('/schedule/', methods=['GET'])
@login_required
def schedule():
    # TODO, if user is authorized to view only one station, redirect them there
    stations = Station.get_stations(current_user)
    # stations = Station.query.order_by('name').all()

    return render_template('radio/schedules.html',
                           stations=stations, active='Schedule')


@radio.route('/schedule/<int:station_id>/', methods=['GET'], defaults={'color': None})
@radio.route('/schedule/<int:station_id>/<color>', methods=['GET'])
@login_required
def schedule_station(station_id, color):
    station = Station.query.filter_by(id=station_id).first_or_404()

    # TODO: move this logic to an ajax call, like scheduled_block_json
    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station.id)
    block_list = []
    for block in scheduled_blocks:
        r = rrule.rrulestr(block.recurrence)
        for instance in r[:30]:  # TODO: dynamically determine instance limit from calendar view
            d = {'title': block.name,
                 'start': datetime.combine(instance, block.start_time),
                 'end': datetime.combine(instance, block.end_time)}
            block_list.append(d)

    form = ScheduleProgramForm()

    if current_user.role_code == ADMIN:
        all_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(Program.deleted == False).all()
    else:
        all_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(
        User.id == current_user.id).filter(Program.deleted == False).all()
    # TODO: filter by language?

    return render_template('radio/schedule.html',
                           form=form, station=station, block_list=block_list, addable_programs=all_programs,
                           active='Schedule', color_view='false' if color=="false" else 'true')
