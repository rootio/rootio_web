# -*- coding: utf-8 -*-

import os

from flask import Blueprint, render_template, request
from flask.ext.login import login_required, current_user

from .models import Station, Program, Episode
from .forms import StationForm

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
        station = Station(**cleaned_data) #create new object from data

        db.session.add(station)
        db.session.commit()
        flash('Station added.', 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('radio/station.html', station=station, form=form)