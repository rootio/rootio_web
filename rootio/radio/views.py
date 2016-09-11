# -*- coding: utf-8 -*-
from __future__ import print_function
import string
import random
import os
import re

from datetime import datetime, timedelta
import sys

import time
import dateutil.rrule, dateutil.parser

from flask import g, current_app, Blueprint, render_template, request, flash, Response, json, url_for
from flask.ext.login import login_required, current_user
from crontab import CronTab
from flask.ext.babel import gettext as _
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import redirect
from ..telephony import Message
from .models import Station, Program, ScheduledBlock, ScheduledProgram, Location, Person, StationhasBots, Language, ProgramType, MediaFiles
from .forms import StationForm, ProgramForm, BlockForm, LocationForm, ScheduleProgramForm, PersonForm, AddBotForm, MediaForm

from ..decorators import returns_json, returns_flat_json
from ..utils import error_dict, fk_lookup_form_data, allowed_audio_file, ALLOWED_AUDIO_EXTENSIONS
from ..extensions import db
from ..utils_bot import add_cron, send_mail, removeCron

from werkzeug import secure_filename

import mutagen
from ..messenger import messages

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
    stations = Station.query.order_by('name').all()
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
"""
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
"""

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

    stations = Station.query.order_by('name').all()

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

@radio.route('/bots/', methods=['GET'])
def list_bots():
    """
    Presents a list with all the bots that have been created and the radios where they\'re working
    :return:
    """
    stations = Station.query.all()
    return render_template('radio/bots.html', stations=stations)

@radio.route('/bots/add/', methods=['GET', 'POST'])
@login_required
def new_bot_add():
    """
        Renders the form to insert a new bot in the database.
        Add cronJobs if the state bot is active
    """
    form = AddBotForm(request.form)
    bot = None
    type = "add"

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        cleaned_data.pop('submit', None)  # remove submit field from list
        bot = StationhasBots(**cleaned_data)  # create new object from data
        try:
            bot = add_cron(bot,type)
            db.session.add(bot)
            db.session.commit()
            flash(_('Bot added.'), 'success')
        except Exception as e:
            removeCron(bot, CronTab(user=True))
            db.session.rollback()
            db.session.flush()
            print (str(e))
            send_mail("Error happened while you're adding a bot", str(e))
            flash(_('Error Bot Not Added.'), 'error')

    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/bot.html', bot=bot, form=form)

@radio.route('/bot/<int:radio_id>/<int:function_id>', methods=['GET', 'POST'])
@login_required
def bot_edit(radio_id, function_id):

    bot = StationhasBots.query.filter_by(fk_radio_station_id=radio_id, fk_bot_function_id=function_id).first_or_404()
    form = AddBotForm(obj=bot, next=request.args.get('next'))
    type = "edit"
    if form.validate_on_submit():
        form.populate_obj(bot)
        try:
            bot = add_cron(bot, type)
            db.session.add(bot)
            db.session.commit()
            flash(_('Bot updated.'), 'success')
        except Exception as e:
            removeCron(bot,CronTab(user=True))
            db.session.rollback()
            db.session.flush()
            print(str(e))
            send_mail("Error happened editig the bot", str(e))
            flash(_('Error Bot Not Updated.'), 'error')


    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/bot.html', bot=bot, form=form)

@radio.route('/media', methods=['GET', 'POST'])
@login_required
def media_files():
    media = MediaFiles.query.all()
    return render_template('radio/media.html', media=media)

@radio.route('/media/add', methods=['GET', 'POST'])
@login_required
def media_add():
    form = MediaForm(request.form)
    media = None

    if form.validate_on_submit():
        cleaned_data = form.data  # make a copy
        upload_file = request.files[form.path.name]
        if upload_file and allowed_audio_file(upload_file.filename):
            data = upload_file.read()
            path_file = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_file.filename)
            open(path_file, 'w').write(data)
            filename, file_extension = os.path.splitext(path_file)
            if file_extension == '.wav':
                import wave
                import contextlib
                with contextlib.closing(wave.open(path_file, 'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    duration = unicode(timedelta(seconds=frames / float(rate)))
            else:
                audio = mutagen.File(path_file)
                duration = unicode(timedelta(seconds=audio.info.length))
            cleaned_data.pop('submit', None)  # remove submit field from list
            cleaned_data['path'] = path_file
            cleaned_data['duration'] = duration
            media = MediaFiles(**cleaned_data)  # create new object from data

            db.session.add(media)
            db.session.commit()
            flash(_('Media File added.'), 'success')
        else:
            flash("Please upload files with extensions: %s" % "/".join(ALLOWED_AUDIO_EXTENSIONS), 'error')
    elif request.method == "POST":
        flash(_('Validation error'), 'error')

    return render_template('radio/mediaform.html', media=media, form=form)

@radio.route('/media/<int:media_id>', methods=['GET', 'POST'])
@login_required
def media_edit(media_id):
    media = MediaFiles.query.filter_by(id=media_id).first_or_404()
    form = MediaForm(obj=media, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(media)
        upload_file = request.files[form.path.name]
        if upload_file and allowed_audio_file(upload_file.filename):
            data = upload_file.read()
            path_file = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_file.filename)
            open(path_file, 'w').write(data)
            filename, file_extension = os.path.splitext(path_file)
            if file_extension == '.wav':
                import wave
                import contextlib
                with contextlib.closing(wave.open(path_file, 'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    duration = unicode(timedelta(seconds=frames / float(rate)))
            else:
                audio = mutagen.File(path_file)
                duration = unicode(timedelta(seconds=audio.info.length))
            media.path = path_file
            media.duration = duration
            db.session.add(media)
            db.session.commit()
            flash(_('Media File updated.'), 'success')
        else:
            flash("Please upload files with extensions: %s" % "/".join(ALLOWED_AUDIO_EXTENSIONS), 'error')

    return render_template('radio/mediaform.html', media=media, form=form)

@radio.route('/media/list', methods=['GET', 'POST'])
@login_required
def media_list():
    media = dict()
    for m in MediaFiles.query.all():
        media[m.id] = {'media_id': m.id, 'name': m.name, 'description': m.description, 'path': m.path,
                          'language': unicode(m.language), 'type': m.type,
                          'duration': m.duration}
    return json.jsonify(media)

@radio.route('/media/find', methods=['GET', 'POST'])
@login_required
def media_find():
    try:
        media = MediaFiles.query.filter_by(path=request.form['path'])
        return media[0].name
    except:
        media = MediaFiles.query.filter_by(path=request.form['path[]'])
        return media[0].name

@radio.route('/sms/', methods=['GET', 'POST'])
@login_required
def list_sms():
    messages = dict()
    for m in Message.query.all():
        messages[m.id] = {'message_id':m.id,'message_uuid':m.message_uuid,'sendtime':m.sendtime,
                         'text': m.text,'from_phonenumber_id':m.from_phonenumber_id,
                         'to_phonenumber_id':m.to_phonenumber_id,'onairprogram_id': m.onairprogram_id}
    return json.jsonify(messages)

@radio.route('/program/<int:program_id>', methods=['GET', 'POST'])
def program(program_id):
    program = Program.query.filter_by(id=program_id).first_or_404()
    form = ProgramForm(obj=program, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(program)
        program.duration = request.form['est_time']
        program.description = request.form['description']

        db.session.add(program)
        db.session.commit()
        flash(_('Program updated.'), 'success')

    return render_template('radio/program.html', program=program, form=form)