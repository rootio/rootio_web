# -*- coding: utf-8 -*-

import os
from datetime import datetime
from dateutil import rrule

from flask import g, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user

from .models import Station, Program, ScheduledBlock, BlockedProgram, ScheduledContent, Location, Person
from .forms import StationForm, ProgramForm, BlockForm, LocationForm, BlockedProgramForm, PersonForm

from ..decorators import returns_json
from ..utils import error_dict
from ..extensions import db

radio = Blueprint('radio', __name__, url_prefix='/radio')

@radio.route('/', methods=['GET'])
def index():
    stations = Station.query.all()
    return render_template('radio/index.html',stations=stations)

@radio.route('/station/', methods=['GET'])
def stations():
    stations = Station.query.all()
    return render_template('radio/stations.html', stations=stations, active='stations')


@radio.route('/station/<int:station_id>', methods=['GET', 'POST'])
def station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash('Station updated.', 'success')

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
        print cleaned_data
        station = Station(**cleaned_data) #create new object from data

        db.session.add(station)
        db.session.commit()
        flash('Station added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('radio/station.html', station=station, form=form)


@radio.route('/program/', methods=['GET'])
def programs():
    programs = Program.query.all()
    return render_template('radio/programs.html', programs=programs, active='programs')


@radio.route('/program/<int:program_id>', methods=['GET', 'POST'])
def program(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()
    form = ProgramForm(obj=program, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(program)

        db.session.add(program)
        db.session.commit()
        flash('Program updated.', 'success')

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
        flash('Program added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('radio/program.html', program=program, form=form)

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
        flash('Person updated.', 'success')

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
        flash('Person added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('radio/person.html', person=person, form=form)


@radio.route('/location/add/inline/', methods=['POST'])
@login_required
@returns_json
def location_add_inline():
    data = json.loads(request.data)
    #handle floats individually
    float_vals = ['latitude','longitude']
    for field in float_vals:
        try:
            data[field] = float(data[field])
        except ValueError:
            response = {'status':'error','errors':{field:'Invalid '+field},'status_code':400}
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
    return render_template('radio/scheduled_blocks.html', scheduled_blocks=scheduled_blocks, active='blocks')


@radio.route('/block/<int:block_id>', methods=['GET', 'POST'])
def scheduled_block(block_id):
    block = ScheduledBlock.query.filter_by(id=block_id).first_or_404()
    form = BlockForm(obj=block, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(block)
        db.session.add(block)
        db.session.commit()
        flash('Block updated.', 'success')

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
        print cleaned_data
        db.session.add(block)
        db.session.commit()
        flash('Block added.', 'success') 
    elif request.method == "POST":
        print "form.errors",form.errors
        print form.data
        flash('Validation error','error')

    return render_template('radio/scheduled_block.html', program=program, form=form)


@radio.route('/blockedprogram/add/inline/', methods=['POST'])
@login_required
@returns_json
def blocked_program_inline():
    data = json.loads(request.data)
    
    form = BlockedProgramForm(None, **data)
    print "*** form",form.data
    #lookup fk's manually?

    blocked_program = None
    if form.validate_on_submit():
    #    cleaned_data = form.data #make a copy
    #    cleaned_data.pop('submit',None) #remove submit field from list
        blocked_program = BlockedProgram(**cleaned_data) #create new object from data
        db.session.add(blocked_program)
        db.session.commit()
        response = {'status':'success','result':{'id':blocked_program.id,'string':unicode(blocked_program)},'status_code':200}
    elif request.method == "POST":
        response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response


@radio.route('/station/<int:station_id>/scheduledcontent.json', methods=['GET'])
@returns_json
def scheduled_content_json(station_id):
    scheduled_content = ScheduledContent.query.filter_by(station_id=station_id)
    resp = []
    for s in scheduled_content:
        print s
    return resp


@radio.route('/station/<int:station_id>/scheduledblocks.json', methods=['GET'])
@returns_json
def scheduled_block_json(station_id):
    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station_id)
    start = request.args.get('start')
    end = request.args.get('end')
    #TODO: hook fullcalendar updates into these params

    resp = []
    for block in scheduled_blocks:
        r = rrule.rrulestr(block.recurrence)
        for instance in r.between(start,end):
            d = {'title':block.name,
                'start':datetime.combine(instance,block.start_time),
                'end':datetime.combine(instance,block.end_time)}
            resp.append(d)
    return resp


@radio.route('/schedule/', methods=['GET'])
def schedule():
    #todo, make this deal with multiple stations
    #station = Station.query.filter_by(id=station_id).first_or_404()

    #hack, hardcode for now
    station = Station.query.get(1)

    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station.id)
    block_list = []
    for block in scheduled_blocks:
        r = rrule.rrulestr(block.recurrence)
        for instance in r[:10]: #TODO: dynamically determine instance limit from calendar view
            d = {'title':block.name,
                'start':datetime.combine(instance,block.start_time),
                'end':datetime.combine(instance,block.end_time)}
            block_list.append(d)

    form = BlockedProgramForm()
    return render_template('radio/schedule.html',
        form=form, station=station, block_list=block_list,
        active='schedule')
