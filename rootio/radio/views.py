# -*- coding: utf-8 -*-

import os
from datetime import datetime
import time
from dateutil import rrule

from flask import g, current_app, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _

from .models import Station, Program, ScheduledBlock, ScheduledProgram, Location, Person
from .forms import StationForm, ProgramForm, BlockForm, LocationForm, ScheduleProgramForm, PersonForm

from ..decorators import returns_json
from ..utils import error_dict
from ..extensions import db

radio = Blueprint('radio', __name__, url_prefix='/radio')

@radio.route('/', methods=['GET'])
def index():
    stations = Station.query.all()
    return render_template('radio/index.html',stations=stations)

@radio.route('/emergency/', methods=['GET'])
def emergency():
    stations = Station.query.all()
    #demo, override station statuses
    for s in stations:
        s.status = "on"

    #end demo
    return render_template('radio/emergency.html',stations=stations)

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


@radio.route('/scheduleprogram/add/inline/', methods=['POST'])
@login_required
@returns_json
def schedule_program_inline():
    data = json.loads(request.data)
    
    form = ScheduleProgramForm(None, **data)
    current_app.logger.debug( "*** form",form.data)
    #lookup fk's manually?

    scheduled_episode = None
    if form.validate_on_submit():
    #    cleaned_data = form.data #make a copy
    #    cleaned_data.pop('submit',None) #remove submit field from list
        scheduled_episode = ScheduledEpisode(**cleaned_data) #create new object from data
        db.session.add(scheduled_episode)
        db.session.commit()
        response = {'status':'success','result':{'id':scheduled_episode.id,'string':unicode(scheduled_episode)},'status_code':200}
    elif request.method == "POST":
        response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response


@radio.route('/station/<int:station_id>/scheduledepisodes.json', methods=['GET'])
@returns_json
def scheduled_episodes_json(station_id):
    scheduled_episodes = ScheduledEpisode.query.filter_by(station_id=station_id)
    resp = []
    for s in scheduled_episodes:
        current_app.logger.debug(s)
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
    #TODO, if user is authorized to view only one station, redirect them there

    stations = Station.query.all()
    return render_template('radio/schedules.html',
        stations=stations, active='schedule')

@radio.route('/schedule/<int:station_id>/', methods=['GET'])
def schedule_station(station_id):
    station = Station.query.get(station_id)

    scheduled_blocks = ScheduledBlock.query.filter_by(station_id=station.id)
    block_list = []
    for block in scheduled_blocks:
        r = rrule.rrulestr(block.recurrence)
        for instance in r[:10]: #TODO: dynamically determine instance limit from calendar view
            d = {'title':block.name,
                'start':datetime.combine(instance,block.start_time),
                'end':datetime.combine(instance,block.end_time)}
            block_list.append(d)

    form = ScheduleProgramForm()
    return render_template('radio/schedule.html',
        form=form, station=station, block_list=block_list,
        active='schedule')
