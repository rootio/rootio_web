# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Blueprint, render_template, request, flash
from flask.ext.babel import gettext as _
from flask.ext.login import login_required, current_user

from ..radio.forms import StationForm, StationTelephonyForm, NetworkForm
from ..radio.models import Station, Network
from ..extensions import db
from ..user.models import User, RootioUser

configuration = Blueprint('configuration', __name__, url_prefix='/configuration')


@configuration.route('/', methods=['GET'])
def index():
    # get all the user's networks and their stations
    networks = Network.query.outerjoin(Station).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('radio/index.html', networks=networks, userid=current_user.id, now=datetime.now)


@configuration.route('/tts/', methods=['GET'])
def tts():
    stations = Station.query.all()
    # demo, override station statuses
    for s in stations:
        s.status = "on"

    # end demo
    return render_template('configuration/tts.html', stations=stations)


@configuration.route('/telephony/', methods=['GET', 'POST'])
def telephony():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    return render_template('configuration/stations_telephony.html', stations=stations)


@configuration.route('/telephony/<int:station_id>', methods=['GET', 'POST'])
def telephony_station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationTelephonyForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash(_('Station updated.'), 'success')

    return render_template('configuration/station_telephony.html', station=station, form=form)


@configuration.route('/telephony/add/', methods=['GET', 'POST'])
@login_required
def telephony_add():
    form = StationTelephonyForm(request.form)
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

    return render_template('configuration/station_telephony.html', station=station, form=form)


@configuration.route('/sip_telephony', methods=['GET', 'POST'])
@login_required
def sip_telephony():
    form = NetworkForm(request.form)
    network = False
    return render_template('configuration/stations_telephony.html', network=network, form=form)


@configuration.route('/audio_levels', methods=['GET'])
def audio_levels():
    stations = Station.query.join(Network).join(User, Network.networkusers).filter(User.id == current_user.id).all()
    # stations = Station.query.join(Network).join(User).filter(User.id == current_user.id).all()
    return render_template('configuration/stations_telephony.html', stations=stations, active='stations')


@configuration.route('/ivr_menu', methods=['GET', 'POST'])
def ivr_menu():

    return render_template('configuration/ivr_menu.html', station=None)


@configuration.route('/synchronization', methods=['GET', 'POST'])
@login_required
def synchronization():
    form = StationForm(request.form)
    station = None
    return render_template('configuration/stations_telephony.html', station=station, form=form)

