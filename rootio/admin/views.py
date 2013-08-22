# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request, flash
from flask.ext.login import login_required

from ..extensions import db
from ..decorators import admin_required

from ..user import User
from .forms import UserForm

from ..radio import Station, Program
from ..radio.forms import StationForm

admin = Blueprint('admin', __name__, url_prefix='/admin')


@admin.route('/')
@login_required
@admin_required
def index():
    users = User.query.all()
    return render_template('admin/index.html', users=users, active='index')


@admin.route('/user/')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users, active='users')


@admin.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = UserForm(obj=user, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        flash('User updated.', 'success')

    return render_template('admin/user.html', user=user, form=form)


@admin.route('/station/', methods=['GET'])
@login_required
@admin_required
def stations():
    stations = Station.query.all()
    return render_template('admin/stations.html', stations=stations, active='stations')


@admin.route('/station/<int:station_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def station(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationForm(obj=station, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(station)

        db.session.add(station)
        db.session.commit()
        flash('Station updated.', 'success')

    return render_template('admin/station.html', station=station, form=form)


@admin.route('/station/add/', methods=['GET', 'POST'])
@login_required
@admin_required
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

    return render_template('admin/station.html', station=station, form=form)
