# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
import time
from pytz import timezone
import dateutil.rrule, dateutil.parser
from sqlalchemy import select

from flask import g, current_app, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _

from ..user.models import User, RootioUser
from ..user import auth
from ..content.models import ContentMusicPlaylist, ContentTrack, ContentType, ContentPodcast
from .models import Station, Program, ScheduledBlock, ScheduledProgram, Location, Person, Network
from .forms import StationForm, StationTelephonyForm,NetworkForm, ProgramForm, BlockForm, LocationForm, ScheduleProgramForm, PersonForm

from ..decorators import returns_json, returns_flat_json
from ..utils import error_dict, fk_lookup_form_data
from ..extensions import db

from ..messenger import messages

radio = Blueprint('radio', __name__, url_prefix='/radio')

@radio.route('/', methods=['GET'])
def index():
    #get the stations in networks that I am associated with
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('radio/index.html',stations=stations, userid=current_user.id)


@radio.route('/emergency/', methods=['GET'])
def emergency():
    stations = Station.query.all()
    #demo, override station statuses
    for s in stations:
        s.status = "on"

    #end demo
    return render_template('radio/emergency.html',stations=stations)


@radio.route('/network/add/', methods=['GET', 'POST'])
@login_required
def network_add():
    if not auth.can_admin():
        auth.deny()

    form = NetworkForm(request.form)

    if form.validate_on_submit():
        form_data = form.data #copy it to remove items, it is immutable
        form_data.pop('submit', None)
        network = Network(**form_data) #create new object from data

        #Associate creator with network - Fix this to use current_user, instead of querying new instance
        user = RootioUser.query.filter(RootioUser.id==current_user.id).first()
        network.networkusers.append(user)

        #Save the Network
        db.session.add(network)
        db.session.commit()
        flash(_('Network Created.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/network.html', program=program, form=form)

@radio.route('/station/', methods=['GET'])
def stations():
    stations = auth.edit_stations().all()
    return render_template('radio/stations.html', stations=stations, active='stations')


@radio.route('/station/<int:station_id>', methods=['GET', 'POST'])
def station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    if not auth.can_edit_station(station):
        auth.deny()

    form = StationForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Station updated.'), 'success')

    return render_template('radio/station.html', station=station, form=form)


@radio.route('/station/add/', methods=['GET', 'POST'])
@login_required
def station_add():
    form = StationForm(request.form)
    station = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        cleaned_data.pop('phone_inline',None) #and also inline forms
        cleaned_data.pop('location_inline',None)
        station = Station(**cleaned_data) #create new object from data

        db.session.add(station)
        db.session.commit()
        flash(_('Station added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/station.html', station=station, form=form)


@radio.route('/program/', methods=['GET'])
def programs():
    programs = Program.query.filter(Program.program_type_id!=2).all()
    return render_template('radio/programs.html', programs=programs, active='programs')


@radio.route('/program/<int:program_id>', methods=['GET', 'POST'])
def program(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()
    #form = ProgramForm(obj=program, program_structure="test", next=request.args.get('next'))

    #hosts in my network
    hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    news = ContentTrack.query.join(ContentType).filter(ContentType.name=="News").all()
    ads = ContentTrack.query.join(ContentType).filter(ContentType.name=="Advertisements").all()
    medias = ContentTrack.query.join(ContentType).filter(ContentType.name=="Media").all()
    podcasts = ContentPodcast.query.all()
    community_contents = {"data":[{"type":"Ads", "category_id":"1"},{"type":"Announcements", "category_id":"2"},{"type":"Greetings", "category_id":"3"}]}
    
    #render the program structure
    action_names = []
    program_json = json.loads(program.structure)
    for action in program_json:
        action_names.append(action['name'])

    program_actions = ",".join(action_names)
    
    form = ProgramForm(obj=program, program_structure=program_actions, next=request.args.get('next')) 
    if form.validate_on_submit():
        form.populate_obj(program)

        db.session.add(program)
        db.session.commit()
        flash(_('Program updated.'), 'success')

    return render_template('radio/program.html', program=program, hosts=hosts,news=news,podcasts=podcasts, ads=ads, medias=medias, community_contents=community_contents["data"],form=form)


@radio.route('/program/add/', methods=['GET', 'POST'])
@login_required
def program_add():
    form = ProgramForm(request.form)
    program = None
    
    #hosts in my network
    hosts = Person.query.join(Person, Network.people).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    news = ContentTrack.query.join(ContentType).filter(ContentType.name=="News").all()
    ads = ContentTrack.query.join(ContentType).filter(ContentType.name=="Advertisements").all()
    medias = ContentTrack.query.join(ContentType).filter(ContentType.name=="Media").all()
    podcasts = ContentPodcast.query.all()
    community_contents = {"data":[{"type":"Ads", "category_id":"1"},{"type":"Announcements", "category_id":"2"},{"type":"Greetings", "category_id":"3"}]}

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        cleaned_data.pop('program_structure')
        cleaned_data['program_type_id'] = 1
        program = Program(**cleaned_data) #create new object from data
        
        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/program.html', program=program,hosts=hosts,news=news,podcasts=podcasts, ads=ads, medias=medias, community_contents=community_contents["data"], form=form)

@radio.route('/music_program/', methods=['GET'])
def music_programs():
    music_programs = Program.query.filter(Program.program_type_id==2).all()
    return render_template('radio/music_programs.html', music_programs=music_programs, active='programs')

@radio.route('/music_program/add/', methods=['GET', 'POST'])
@login_required
def music_program_add():
    form = ProgramForm(request.form)
    program = None

    #hosts in my network
    playlists = ContentMusicPlaylist.query.all()

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        cleaned_data.pop('program_structure')
        cleaned_data['program_type_id'] = 2
        program = Program(**cleaned_data) #create new object from data

        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success')
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/music_program.html', program=program, playlists=playlists, form=form)

@radio.route('/music_program/<int:music_program_id>', methods=['GET', 'POST'])
def music_program(music_program_id):
    music_program = Program.query.filter_by(id=music_program_id).first_or_404()

    community_contents = {"data":[{"type":"Ads", "category_id":"1"},{"type":"Announcements", "category_id":"2"},{"type":"Greetings", "category_id":"3"}]}
    
    playlists = ContentMusicPlaylist.query.all()
    #render the program structure
    action_names = []
    try:
        program_json = json.loads(music_program.structure)
        for action in program_json:
            action_names.append(action['name'])
    except Exception:
        pass
    program_actions = ",".join(action_names)

    form = ProgramForm(obj=music_program, program_structure=program_actions, next=request.args.get('next'))
    if form.validate_on_submit():
        form.populate_obj(music_program)

        db.session.add(music_program)
        db.session.commit()
        flash(_('Music Program updated.'), 'success')

    return render_template('radio/music_program.html', music_program=music_program, playlists=playlists, form=form)


@radio.route('/people/', methods=['GET'])
def people():
    people = Person.query.all()
    return render_template('radio/people.html', people=people, active='people')


@radio.route('/people/<int:person_id>', methods=['GET', 'POST'])
def person(person_id):
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
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        person = Person(**cleaned_data) #create new object from data
        
        db.session.add(person)
        db.session.commit()
        flash(_('Person added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/person.html', person=person, form=form)


@radio.route('/location/add/ajax/', methods=['POST'])
@login_required
@returns_json
def location_add_ajax():
    data = json.loads(request.data)
    #handle floats individually
    float_vals = ['latitude','longitude']
    for field in float_vals:
        try:
            data[field] = float(data[field])
        except ValueError:
            response = {'status':'error','errors':{field:_('Invalid ')+field},'status_code':400}
            return response

    form = LocationForm(None, **data) #use this format to avoid multidict-type issue
    location = None
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        location = Location(**cleaned_data) #create new object from data
        db.session.add(location)
        db.session.commit()
        response = {'status':'success','result':{'id':location.id,'string':unicode(location)},'status_code':200}
    elif request.method == "POST":
        #convert the error dictionary to something serializable
        response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response


@radio.route('/block/', methods=['GET'])
def scheduled_blocks():
    scheduled_blocks = ScheduledBlock.query.all()
    #TODO, display only those that are scheduled on stations the user can view

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
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        block = ScheduledBlock(**cleaned_data) #create new object from data

        db.session.add(block)
        db.session.commit()
        flash(_('Block added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/scheduled_block.html', block=block, form=form)


@radio.route('/scheduleprogram/add/ajax/', methods=['POST'])
@login_required
@returns_json
def schedule_program_add_ajax():
    data = json.loads(request.data)

    if not 'program' in data:
        return {'status':'error','errors':'program required','status_code':400}
    if not 'station' in data:
        return {'status':'error','errors':'station required','status_code':400}

    #lookup objects from ids
    #fk_errors = fk_lookup_form_data({'program':Program,'station':Station}, data)
    #if fk_errors:
    #    return fk_errors

    #Fix this. use form elements

    program = Program.query.filter(Program.id==data['program']).first()
    station = Station.query.filter(Station.id==data['station']).first()
    scheduled_program = ScheduledProgram()
    scheduled_program.station_id = data['station']
    scheduled_program.program_id = data['program']
    scheduled_program.start = timezone(station.timezone).localize(dateutil.parser.parse(data['start']).replace(tzinfo=None)) #Otherwise everything assumes UTC
    scheduled_program.end = scheduled_program.start + program.duration
    scheduled_program.deleted = False

    db.session.add(scheduled_program)
    db.session.commit()
   
    return {'status':data,'result':1,'status_code':200} 
    #return {'status':'success','result':{'id':scheduled_program.id},'status_code':200}



@radio.route('/scheduleprogram/delete/<int:_id>/', methods=['POST'])
@login_required
def delete_program(_id):
    _program = ScheduledProgram.query.filter(ScheduledProgram.id==_id).first()
    _program.deleted = True
    db.session.add(_program)
    db.session.commit()
    return ""


@radio.route('/scheduleprogram/edit/ajax/', methods=['POST'])
@login_required
@returns_json
def schedule_program_edit_ajax():
    data = json.loads(request.data)

    if not 'scheduledprogram' in data:
        return {'status':'error','errors':'scheduledprogram required','status_code':400}

    #lookup objects from ids
    fk_errors = fk_lookup_form_data({'scheduledprogram':ScheduledProgram}, data)
    if fk_errors:
        return fk_errors

    scheduled_program = data['scheduledprogram']
    scheduled_program.start = dateutil.parser.parse(data['start'])
    program = scheduled_program.program
    scheduled_program.end = scheduled_program.start + program.duration
    scheduled_program.deleted = False

    db.session.add(scheduled_program)
    db.session.commit()

    return {'status':'success','result':{'id':scheduled_program.id},'status_code':200}


@radio.route('/scheduleprogram/add/recurring_ajax/', methods=['POST'])
@login_required
@returns_json
def schedule_recurring_program_ajax():
    "Schedule a recurring program"
    data = json.loads(request.data)

    #ensure specified foreign key ids are valid
    #fk_errors = fk_lookup_form_data({'program':Program,'station':Station}, data)
    #if fk_errors:
     #   return fk_errors

    form = ScheduleProgramForm(None, **data)

    try:
        air_time = datetime.strptime(form.data['air_time'],'%H:%M').time()
    except ValueError:
        response = {'status':'error','errors':{'air_time':'Invalid time'},'status_code':400}
        return response

    #if form.validate_on_submit():
    #save refs to form objects
    program = Program.query.filter(Program.id==form.data['program']).first()
    station = Station.query.filter(Station.id==form.data['station']).first()

    #parse recurrence rule
    r = dateutil.rrule.rrulestr(form.data['recurrence'])
    for instance in r[:30]: #TODO: dynamically determine instance limit
        scheduled_program = ScheduledProgram(program=program, station=station)
        scheduled_program.start = datetime.combine(instance,air_time) #combine instance day and air_time time
        scheduled_program.end = scheduled_program.start + program.duration
        scheduled_program.deleted = False
        db.session.add(scheduled_program)
    db.session.commit()
        
    response = {'status':'success','result':{},'status_code':200}
    #elif request.method == "POST":
    #response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response


@radio.route('/station/<int:station_id>/scheduledprograms.json', methods=['GET', 'POST'])
@returns_flat_json
def scheduled_programs_json(station_id):
    if not ('start' in request.args and 'end' in request.args):
        return {'status':'error','errors':'scheduledprograms.json requires start and end','status_code':400}
    start = dateutil.parser.parse(request.args.get('start'))
    end = dateutil.parser.parse(request.args.get('end'))
    scheduled_programs = ScheduledProgram.query.filter_by(station_id=station_id)\
                                                   .filter(ScheduledProgram.start >= start)\
                                                   .filter(ScheduledProgram.end <= end)\
                                                   .filter(ScheduledProgram.deleted == False)
    resp = []
    for s in scheduled_programs:
        d = {'title':s.program.name,
            'start':s.start.isoformat(),
            'end':s.end.isoformat(),
            'id':s.id,
            'program_type_id':s.program.program_type_id,
            'status':s.status}
        resp.append(d)
    return resp


@radio.route('/station/<int:station_id>/scheduledblocks.json', methods=['GET'])
@returns_flat_json
def scheduled_block_json(station_id):
    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station_id)

    if not ('start' in request.args and 'end' in request.args):
        return {'status':'error','errors':'scheduledblocks.json requires start and end','status_code':400}

    #TODO: fullcalendar updates based on these params
    start = dateutil.parser.parse(request.args.get('start'))
    end = dateutil.parser.parse(request.args.get('end'))

    resp = []
    for block in scheduled_blocks:
        r = dateutil.rrule.rrulestr(block.recurrence)
        for instance in r.between(start,end):
            d = {'title':block.name,
                'start':datetime.combine(instance,block.start_time),
                'end':datetime.combine(instance,block.end_time),
                'id':block.id,
                'isBackground':True, #the magic flag that tells full calendar to render as block
            }
            resp.append(d)
    return resp


@radio.route('/schedule/', methods=['GET'])
def schedule():
    #TODO, if user is authorized to view only one station, redirect them there
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    #stations = Station.query.order_by('name').all()

    return render_template('radio/schedules.html',
        stations=stations, active='schedule')

@radio.route('/schedule/<int:station_id>/', methods=['GET'])
def schedule_station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()

    #TODO: move this logic to an ajax call, like scheduled_block_json
    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station.id)
    block_list = []
    for block in scheduled_blocks:
        r = dateutil.rrule.rrulestr(block.recurrence)
        for instance in r[:30]: #TODO: dynamically determine instance limit from calendar view
            d = {'title':block.name,
                'start':datetime.combine(instance,block.start_time),
                'end':datetime.combine(instance,block.end_time)}
            block_list.append(d)

    form = ScheduleProgramForm()

    all_programs = Program.query.all()
    #TODO: filter by language?

    return render_template('radio/schedule.html',
        form=form, station=station, block_list=block_list, addable_programs=all_programs,
        active='schedule')



@radio.route('/telephony/', methods=['GET', 'POST'])
def telephony():
    stations = auth.edit_stations().all()
    return render_template('radio/stations_telephony.html', stations=stations)



@radio.route('/telephony/<int:station_id>', methods=['GET', 'POST'])
def telephony_station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    if not auth.can_edit_station(station):
        auth.deny()

    form = StationTelephonyForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Station updated.'), 'success')

    return render_template('radio/station_telephony.html', station=station, form=form)


@radio.route('/telephony/add/', methods=['GET', 'POST'])
@login_required
def telephony_add():
    if not auth.can_admin():
        auth.deny()

    form = StationTelephonyForm(request.form)
    station = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        cleaned_data.pop('phone_inline',None) #and also inline forms
        cleaned_data.pop('location_inline',None)
        station = Station(**cleaned_data) #create new object from data

        db.session.add(station)
        db.session.commit()
        flash(_('Station added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/station_telephony.html', station=station, form=form)
