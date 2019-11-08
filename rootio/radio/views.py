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
from simplejson.scanner import JSONDecodeError
from sqlalchemy import Date, cast

import dateutil.parser
from dateutil import rrule
from flask import Blueprint, render_template, request, flash, json, abort
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user
from pytz import timezone
import arrow

from .forms import StationForm, NetworkForm, ProgramForm, BlockForm, LocationForm, \
    ScheduleProgramForm, PersonForm
from .models import Station, Program, ScheduledBlock, ScheduledProgram, Location, Person, Network, StationEvent
from ..config import DefaultConfig
from ..content.models import ContentMusicPlaylist, ContentTrack, ContentPodcast, ContentStream
from .models import ContentType
from ..decorators import returns_json, returns_flat_json
from ..extensions import db, csrf
from ..user.models import User, RootioUser
from ..utils import error_dict, fk_lookup_form_data, format_log_line, events_action_display_map
from rootio.user import ADMIN
from sqlalchemy import text

radio = Blueprint('radio', __name__, url_prefix='/radio')


@radio.route('/', methods=['GET'])
@login_required
def index():
    # get all the user's networks and their stations
    if current_user.role_code == ADMIN:
        networks = Network.query.outerjoin(Station).join(User, Network.networkusers).all()
    else:
        networks = Network.query.outerjoin(Station).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('radio/index.html', networks=networks, userid=current_user.id, now=datetime.now)


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
    return render_template('radio/stations.html', stations=stations, active='stations')


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

    return render_template('radio/station.html', station=station, defaultConfig=DefaultConfig, form=form)


@radio.route('/station/add/', methods=['GET', 'POST'])
@login_required
def station_add():
    form = StationForm(request.form)
    station = None

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data.pop('phone_inline', None)  # and also inline forms
        cleaned_data.pop('location_inline', None)
        station = Station(**cleaned_data)  # create new object from data

        db.session.add(station)
        db.session.commit()
        flash(_('Station added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/station.html', station=station, defaultConfig=DefaultConfig, form=form)


@radio.route('/program/', methods=['GET'])
@login_required
def programs():
    if current_user.role_code == ADMIN:
        programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(Program.program_type_id != 2).all()
    else:
        programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(
        User.id == current_user.id).filter(Program.program_type_id != 2).all()
    return render_template('radio/programs.html', programs=programs, active='programs')


@radio.route('/program/<int:program_id>', methods=['GET', 'POST'])
@login_required
def program_definition(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()
    # form = ProgramForm(obj=program, program_structure="test", next=request.args.get('next'))

    # hosts in my network
    if current_user.role_code == ADMIN:
        hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers).all()
    else:
        hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers).filter(
        User.id == current_user.id).all()
    news = ContentTrack.query.join(ContentType).filter(ContentType.name == "News").all()
    ads = ContentTrack.query.join(ContentType).filter(ContentType.name == "Advertisements").all()

    if current_user.role_code == ADMIN:
        medias = ContentTrack.query.join(User, Network.networkusers)\
        .join(ContentTrack, ContentType)\
        .filter(ContentType.name == "Media")\
        .filter(ContentTrack.deleted != True)\
        .all()
    else:
        networks = current_user.networks
        network_ids = [network.id for network in networks]
        medias = ContentTrack.query.join(ContentTrack.networks).filter(ContentTrack.deleted != True).filter(Network.id.in_(network_ids)).all()
        
    podcasts = ContentPodcast.query.all()
    community_contents = {"data": [{"type": "Ads", "category_id": "1"}, {"type": "Announcements", "category_id": "2"},
                                   {"type": "Greetings", "category_id": "3"}]}

    # render the program structure
    action_names = []
    program_json = json.loads(program.structure)
    for action in program_json:
        action_names.append(action['name'])

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
                           medias=medias, community_contents=community_contents["data"], form=form)


@radio.route('/program/add/', methods=['GET', 'POST'])
@login_required
def program_add():
    form = ProgramForm(request.form)
    program = None

    if current_user.role_code == ADMIN:
         # hosts in my network
        hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers)\
                                                        .all()
        news = ContentTrack.query.join(User, Network.networkusers)\
                                .join(ContentTrack, ContentType)\
                                .filter(ContentType.name == "News")\
                                .filter(ContentTrack.deleted != True)\
                                .all()
        ads = ContentTrack.query.join(User, Network.networkusers)\
                                .join(ContentTrack, ContentType)\
                                .filter(ContentType.name == "Advertisements")\
                                .filter(ContentTrack.deleted != True)\
                                .all()
        
        medias = ContentTrack.query.join(User, Network.networkusers)\
                                .join(ContentTrack, ContentType)\
                                .filter(ContentType.name == "Media")\
                                .filter(ContentTrack.deleted != True)\
                                .all()


        podcasts = ContentPodcast.query.join(User, Network.networkusers)\
                                    .all()
    else:
        # hosts in my network
        hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers)\
                                                        .filter(User.id == current_user.id)\
                                                        .all()
        news = ContentTrack.query.join(User, Network.networkusers)\
                                .filter(User.id == current_user.id)\
                                .join(ContentTrack, ContentType)\
                                .filter(ContentType.name == "News")\
                                .filter(ContentTrack.deleted != True)\
                                .all()
        ads = ContentTrack.query.join(User, Network.networkusers)\
                                .filter(User.id == current_user.id)\
                                .join(ContentTrack, ContentType)\
                                .filter(ContentType.name == "Advertisements")\
                                .filter(ContentTrack.deleted != True)\
                                .all()
        
        networks = current_user.networks
        network_ids = [network.id for network in networks]
        medias = ContentTrack.query.join(ContentTrack.networks).filter(ContentTrack.deleted != True).filter(Network.id.in_(network_ids)).all()

        podcasts = ContentPodcast.query.join(User, Network.networkusers)\
                                    .filter(User.id == current_user.id)\
                                    .all()
    community_contents = {"data": [{"type": "Ads", "category_id": "1"}, {"type": "Announcements", "category_id": "2"},
                                   {"type": "Greetings", "category_id": "3"}]}

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        cleaned_data.pop('program_structure')
        cleaned_data['program_type_id'] = 1
        program = Program(**cleaned_data)  # create new object from data

        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/program.html', program=program, hosts=hosts, news=news, podcasts=podcasts, ads=ads,
                           medias=medias, community_contents=community_contents["data"], form=form)


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
        music_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(Program.program_type_id == 2).all()
    else:
        music_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(
        User.id == current_user.id).filter(Program.program_type_id == 2).all()
    return render_template('radio/music_programs.html', music_programs=music_programs, active='programs')


@radio.route('/music_program/add/', methods=['GET', 'POST'])
@login_required
def music_program_add():
    form = ProgramForm(request.form)
    program = None

    if current_user.role_code == ADMIN:
        playlists = ContentMusicPlaylist.query.join(Station).join(Network).join(User, Network.networkusers).filter(ContentMusicPlaylist.deleted != True).all()  # Playlist->Station->Network->user
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

        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/music_program.html', program=program, playlists=playlists, streams=streams, form=form)


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
                           streams=streams, form=form)


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
    scheduled_programs = ScheduledProgram.query.filter(ScheduledProgram.series_id == _id).all()

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


@radio.route('/station/<int:station_id>/scheduledprograms.json', methods=['GET', 'POST'])
@returns_flat_json
def scheduled_programs_json(station_id):
    if not ('start' in request.args and 'end' in request.args):
        return {'status': 'error', 'errors': 'scheduledprograms.json requires start and end', 'status_code': 400}
    #start = datetime.strptime(request.args.get('start'), '%Y-%m-%d').resolution
    #end = datetime.strptime(request.args.get('end'), '%Y-%m-%d').resolution

    '''
    start = request.args.get('start')
    end = request.args.get('end')

    sql = text('select * from schedule_program_view where start >= :start and _end <= :end and station_id = :station_id;')
    sql = sql.bindparams(start=start, end=end, station_id=station_id)
    scheduled_programs = db.engine.execute(sql)   
    '''


    start = dateutil.parser.parse(request.args.get('start'))
    end = dateutil.parser.parse(request.args.get('end'))
    scheduled_programs = ScheduledProgram.query.filter_by(station_id=station_id) \
        .filter(ScheduledProgram.start >= start) \
        .filter(ScheduledProgram.end <= end) \
        .filter(ScheduledProgram.deleted != True)


    resp = []
    for s in scheduled_programs:

        
        hasFutureMedia = None
        if s.status is None:
            try:
                # if program hasn't played yet
                hasFutureMedia = False
                program_json = json.loads(s.program.structure)
                for action in program_json:
                    if "type" in action:
                        if action['type'] == "Advertisements":
                            if "track_id" in action and "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break
                        if action['type'] == "Media":
                            if "track_id" in action and "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break
                        if action['type'] == "Community":
                            if "category_id" in action and "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break
                        if action['type'] == "Podcast":
                            if "track_id" in action and "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break

                        if action['type'] == "Music":
                            if "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break

                        if action['type'] == "News":
                            if "track_id" in action and "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break

                        if action['type'] == "Outcall":
                            if "host_id" in action and "start_time" in action and "duration" in action:
                                hasFutureMedia = True
                                break
            except e:
                print(e)
       
        '''
        d = {'title': s.name,
            'start': s.start.isoformat(),
            'end': s._end.isoformat(),
            'id': s.id,
            'series_id': s.series_id,
            'color': s.color}
        #              'future_media': hasFutureMedia}
        '''

        d = {'title': s.program.name,
            'start': s.start.isoformat(),
            'end': s.end.isoformat(),
            'id': s.id,
            'status': s.status,
            'series_id': s.series_id,
            'future_media': hasFutureMedia,
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
                           events_map=events_action_display_map
    )


@radio.route('/schedule/', methods=['GET'])
@login_required
def schedule():
    # TODO, if user is authorized to view only one station, redirect them there
    stations = Station.get_stations(current_user)
    # stations = Station.query.order_by('name').all()

    return render_template('radio/schedules.html',
                           stations=stations, active='schedule')


@radio.route('/schedule/<int:station_id>/', methods=['GET'])
@login_required
def schedule_station(station_id):
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
        all_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).all()
    else:
        all_programs = Program.query.join(Program, Network.programs).join(User, Network.networkusers).filter(
        User.id == current_user.id).all()
    # TODO: filter by language?

    return render_template('radio/schedule.html',
                           form=form, station=station, block_list=block_list, addable_programs=all_programs,
                           active='schedule')
