# -*- coding: utf-8 -*-

import os

from flask import g, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user

from .models import Station, Program, Content
from .forms import StationForm, ProgramForm

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
    #TODO: set form owner from current_user
    #form.owner = g.current_user
    station = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
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

@radio.route('/schedule/', methods=['GET'])
def schedule():
    programs = Program.query.all() #TODO: limit to those not yet scheduled
    return render_template('radio/schedule.html', programs=programs, active='schedule')

@radio.route('/station/schedule.json', methods=['GET'])
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

    #can't use jsonify, because fullcalendar expects an array of event objects
    #create response manually
    return Response(json.dumps(schedule_list),  mimetype='application/json')