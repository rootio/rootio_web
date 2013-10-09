# -*- coding: utf-8 -*-

import os

from flask import g, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user

from .models import Station, Program, Content, Location
from .forms import StationForm, ProgramForm, LocationForm, SchedulingForm

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
        station = Station(**cleaned_data) #create new object from data

        db.session.add(station)
        db.session.commit()
        flash('Station added.', 'success') 
    elif request.method == "POST":
        print "form.errors",form.errors
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


@radio.route('/schedule/', methods=['GET','POST'])
def schedule():
    form = SchedulingForm()

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        
        print form.data
        #create new ScheduledContent objects

        
        db.session.add(program)
        db.session.commit()
        flash('Schedule updated.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('radio/schedule.html', form=form, active='schedule')


@radio.route('/station/schedule.json', methods=['GET'])
@returns_json
def schedule_json():
    from datetime import datetime, timedelta, time
    now = datetime.now()
    today = datetime.today().date()
    tonight = datetime.combine(today,time(22,0,0))
    dummy_list = [
        {'title':'next hour','start':datetime.now(),'end':datetime.now() + timedelta(hours=1)},
        {'title':'late night','start':tonight,'end':tonight + timedelta(hours=4)}
    ]
    schedule_list = dummy_list
    return schedule_list