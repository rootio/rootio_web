# -*- coding: utf-8 -*-

import os
from datetime import datetime
import time
import dateutil.rrule, dateutil.parser

from flask import g, current_app, Blueprint, render_template, request, flash, Response, json, session, redirect, url_for
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _

from .models import Station, Program, ScheduledBlock, ScheduledProgram, Location, Person, Network
from .forms import StationForm, ProgramForm, BlockForm, LocationForm, ScheduleProgramForm, PersonForm

from ..decorators import returns_json, returns_flat_json
from ..utils import error_dict, fk_lookup_form_data
from ..extensions import db

from ..messenger import messages

radio = Blueprint('radio', __name__, url_prefix='/radio')

@radio.route('/', methods=['GET'])
@login_required
def index():
    stations = db.session.query(Station).filter(Station.owner_id == current_user.id)
    return render_template('radio/index.html', stations=stations.all())


@radio.route('/emergency/', methods=['GET'])
@login_required
def emergency():
    stations = Station.query.all()
    #demo, override station statuses
    for s in stations:
        s.status = "on"

    #end demo
    return render_template('radio/emergency.html',stations=stations)


@radio.route('/station/', methods=['GET'])
@login_required
def stations():
    #Todo Filter Station under networks this user administers **Query Confusion**
    stations = Station.query.filter_by(owner_id=current_user.id).order_by('name').all()
    if len(stations) == 1:
        return redirect(url_for('station', station_id=stations[0].id))
    return render_template('radio/stations.html', stations=stations, active='stations')


@radio.route('/station/<int:station_id>', methods=['GET', 'POST'])
@login_required
def station(station_id):
    station = Station.query.filter_by(id=station_id, owner_id=current_user.id).first_or_404()
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
@login_required
def programs():
    programs = Program.query.all()
    return render_template('radio/programs.html', programs=programs, active='programs')


@radio.route('/program/<int:program_id>', methods=['GET', 'POST'])
@login_required
def program(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()
    form = ProgramForm(obj=program, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(program)

        db.session.add(program)
        db.session.commit()
        flash(_('Program updated.'), 'success')

    return render_template('radio/program.html', program=program, form=form)


@radio.route('/program/add/', methods=['GET', 'POST'])
@login_required
def program_add():
    form = ProgramForm(request.form)
    program = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        program = Program(**cleaned_data) #create new object from data
        
        db.session.add(program)
        db.session.commit()
        flash(_('Program added.'), 'success') 
    elif request.method == "POST":
        flash(_('Validation error'),'error')

    return render_template('radio/program.html', program=program, form=form)

@radio.route('/people/', methods=['GET'])
@login_required
def people():
    people = Person.query.all()
    return render_template('radio/people.html', people=people, active='people')


@radio.route('/people/<int:person_id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def scheduled_blocks():
    scheduled_blocks = ScheduledBlock.query.all()
    #TODO, display only those that are scheduled on stations the user can view

    return render_template('radio/scheduled_blocks.html', scheduled_blocks=scheduled_blocks, active='blocks')


@radio.route('/block/<int:block_id>', methods=['GET', 'POST'])
@login_required
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
    fk_errors = fk_lookup_form_data({'program':Program,'station':Station}, data)
    if fk_errors:
        return fk_errors

    program = data['program']
    scheduled_program = ScheduledProgram(program=data['program'], station=data['station'])
    scheduled_program.start = dateutil.parser.parse(data['start'])
    scheduled_program.end = scheduled_program.start + program.duration

    db.session.add(scheduled_program)
    db.session.commit()
    
    return {'status':'success','result':{'id':scheduled_program.id},'status_code':200}


@radio.route('/scheduleprogram/delete/<int:_id>/', methods=['POST'])
@login_required
def delete_program(_id):
    _program = ScheduledProgram.query.get(_id)
    db.session.delete(_program)
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
    fk_errors = fk_lookup_form_data({'program':Program,'station':Station}, data)
    if fk_errors:
        return fk_errors

    form = ScheduleProgramForm(None, **data)

    try:
        air_time = datetime.strptime(form.data['air_time'],'%H:%M').time()
    except ValueError:
        response = {'status':'error','errors':{'air_time':'Invalid time'},'status_code':400}
        return response

    if form.validate_on_submit():
        #save refs to form objects
        program = form.data['program']
        station = form.data['station']

        #parse recurrence rule
        r = dateutil.rrule.rrulestr(form.data['recurrence'])
        for instance in r[:10]: #TODO: dynamically determine instance limit
            scheduled_program = ScheduledProgram(program=program, station=station)
            scheduled_program.start = datetime.combine(instance,air_time) #combine instance day and air_time time
            scheduled_program.end = scheduled_program.start + program.duration
            
            db.session.add(scheduled_program)

        db.session.commit()
        
        response = {'status':'success','result':{},'status_code':200}
    elif request.method == "POST":
        response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response


@radio.route('/station/<int:station_id>/scheduledprograms.json', methods=['GET'])
@returns_flat_json
@login_required
def scheduled_programs_json(station_id):
    if request.args.get('start') and request.args.get('end'):
        start = dateutil.parser.parse(request.args.get('start'))
        end = dateutil.parser.parse(request.args.get('end'))
        scheduled_programs = ScheduledProgram.query.filter_by(station_id=station_id)
        #TODO: filter by start > start, end < end
    else:
        scheduled_programs = ScheduledProgram.query.filter_by(station_id=station_id)
    resp = []
    for s in scheduled_programs:
        d = {'title':s.program.name,
            'start':s.start.isoformat(),
            'end':s.end.isoformat(),
            'id':s.id}
        resp.append(d)
    return resp


@radio.route('/station/<int:station_id>/scheduledblocks.json', methods=['GET'])
@returns_flat_json
@login_required
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
@login_required
def schedule():
    #Todo Filter Station under networks this user administers **Query Confusion**
    stations = Station.query.filter_by(owner_id=current_user.id).order_by('name').all()
    if len(stations) == 1:
        return redirect(url_for('schedule_station', station_id=stations[0].id))
    return render_template('radio/schedules.html',
        stations=stations, active='schedule')

@radio.route('/schedule/<int:station_id>/', methods=['GET'])
@login_required
def schedule_station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()

    #TODO: move this logic to an ajax call, like scheduled_block_json
    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station.id)
    block_list = []
    for block in scheduled_blocks:
        r = dateutil.rrule.rrulestr(block.recurrence)
        for instance in r[:10]: #TODO: dynamically determine instance limit from calendar view
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
