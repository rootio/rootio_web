# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, request, jsonify, abort, make_response
from flask.ext.login import login_user, current_user, logout_user

from .utils import parse_datetime

from ..extensions import db, rest, csrf

from ..user import User
from ..radio import Station, Person, Program, ScheduledProgram, Episode, Recording, StationAnalytic
from ..radio.forms import StationAnalyticForm
from ..telephony import PhoneNumber, Call, Message
from ..onair import OnAirProgram

from ..decorators import returns_json, api_key_or_auth_required, restless_preprocessors, restless_postprocessors

#the web login api
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated():
        return jsonify(flag='success')

    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        user, authenticated = User.authenticate(username, password)
        if user and authenticated:
            if login_user(user, remember='y'):
                return jsonify(flag='success')

    current_app.logger.debug('login failed, username: %s.' % username)
    return jsonify(flag='fail', msg='Sorry, try again.')


@api.route('/logout')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return jsonify(flag='success', msg='Logged out.')


#the restless api
#needs to be called after app instantiation
#preprocessor requires logged in user or api key
def restless_routes():
    rest.create_api(Person, collection_name='person', methods=['GET'],
        preprocessors=restless_preprocessors,
        postprocessors=restless_postprocessors)
    rest.create_api(User, collection_name='user', methods=['GET'],
        exclude_columns=['_password'],
        preprocessors=restless_preprocessors)

    rest.create_api(Station, collection_name='station', methods=['GET'],
        exclude_columns=['owner','api_key','scheduled_programs','analytics','blocks'],
        preprocessors=restless_preprocessors,
        postprocessors=restless_postprocessors)
    rest.create_api(Program, collection_name='program', methods=['GET'],
        exclude_columns=['scheduled_programs'],
        preprocessors=restless_preprocessors)

    rest.create_api(ScheduledProgram, collection_name='scheduledprogram', methods=['GET'],
	exclude_columns=['station'],
        preprocessors=restless_preprocessors,
	postprocessors=restless_postprocessors)

    rest.create_api(Episode, collection_name='episode', methods=['GET'],
        exclude_columns=[],
       preprocessors=restless_preprocessors)
    rest.create_api(Recording, collection_name='recording', methods=['GET'],
        exclude_columns=[],
        preprocessors=restless_preprocessors)

    rest.create_api(PhoneNumber, collection_name='phonenumber', methods=['GET'],
        exclude_columns=[],
        preprocessors=restless_preprocessors)
    rest.create_api(Call, collection_name='call', methods=['GET'],
        exclude_columns=[],
        preprocessors=restless_preprocessors)
    rest.create_api(Message, collection_name='message', methods=['GET'],
        exclude_columns=[],
        preprocessors=restless_preprocessors)

#need routes for:
    #phone to update station schedule?

#non CRUD-routes
#protect with decorator
@api.route('/station/<int:station_id>/current_program', methods=['GET'])
@api_key_or_auth_required
@returns_json
def current_program(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    return station.current_program()


@api.route('/station/<int:station_id>/on_air', methods=['GET'])
@api_key_or_auth_required
@returns_json
def on_air(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    current_program = station.current_program()
    if current_program:
        return current_program.onairprogram
    else:
        message = jsonify(flag='error', msg='No OnAirProgram set for station')
        abort(make_response(message, 500)) 


@api.route('/station/<int:station_id>/next_program', methods=['GET'])
@api_key_or_auth_required
@returns_json
def next_program(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    return station.next_program()


@api.route('/station/<int:station_id>/current_block', methods=['GET'])
@api_key_or_auth_required
@returns_json
def current_block(station_id):
    station = Station.query.filter_by(id=station_id).first_or_404()
    return station.current_block()


@api.route('/station/<int:station_id>/schedule', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_schedule(station_id):
    """API method to get a station's schedule.
    Parameters:
        start: ISO datetime
        end: ISO datetime
        all: if truthy, then ignores start and end constraints"""
    station = Station.query.filter_by(id=station_id).first_or_404()
    start = parse_datetime(request.args.get('start'))
    end = parse_datetime(request.args.get('end'))
    #TODO, investigate the proper ordering of these clauses for query speed
    if request.args.get('all'):
        return ScheduledProgram.query.filter_by(station_id=station.id)
    elif start and end:
        return ScheduledProgram.between(start,end).filter_by(station_id=station.id)
    elif start:
        return ScheduledProgram.after(start).filter_by(station_id=station.id)
    elif end:
        return ScheduledProgram.before(end).filter_by(station_id=station.id)
     else:
        message = jsonify(flag='error', msg="Need to specify parameters 'start' or 'end' as ISO datetime or all=1")
        abort(make_response(message, 400)) 


@api.route('/station/<int:station_id>/programs', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_programs(station_id):
    """API method to get all programs currently scheduled on the station"""
    station = Station.query.filter_by(id=station_id).first_or_404()
    programs = station.scheduled_programs
    
    if request.args.get('updated_since'):
        try:
            updated_since = parse_datetime(request.args.get('updated_since'))
            return programs.filter(ScheduledProgram.updated_at>updated_since)

        except (ValueError, TypeError):
            message = jsonify(flag='error', msg="Programs Unable to parse updated_since parameter. Must be ISO datetime format")
            abort(make_response(message, 400))
    else:
        return programs.all()


@api.route('/station/<int:station_id>/phone_numbers', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_phone_numbers(station_id):
    """API method to get all phone numbers currently linked to a station"""
    station = Station.query.filter_by(id=station_id).first_or_404()

    #TODO, query the whitelisted_phones m2m
    #until then, just the two predefined
    r = {'cloud':station.cloud_phone.raw_number,'transmitter':station.transmitter_phone.raw_number}
    return r


@csrf.exempt
@api.route('/station/<int:station_id>/analytics', methods=['GET', 'POST'])
@api_key_or_auth_required
@returns_json
def station_analytics(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()
    form = StationAnalyticForm(request.form, csrf_enabled=False)

    if form.validate_on_submit():
        analytic = StationAnalytic(**form.data) #create new object from data
        analytic.station = station

        db.session.add(analytic)
        db.session.commit()
        return {'message':'success'}
    elif request.method == "POST":
        message = jsonify(flag='error', msg="Unable to parse station analytic form. Errors: %s" % form.errors)
        abort(make_response(message, 400))    
    else:
        #return just most recent analytic?
        # or allow filtering by datetime?
        analytics_list = StationAnalytic.query.filter(station_id=station.id).all()
        return analytics_list



@api.route('/station/<int:station_id>/scheduled_programs', methods=['GET'])
@api_key_or_auth_required
@returns_json
def scheduled_programs:(station_id):
    """API method to get all scheduled programs  currently linked to this station"""
  
   # station = Station.query.filter_by(id=station_id).first_or_404()  
    #test = station.scheduled_programs
    scheduleprogs = ScheduledProgram.query.filter_by(ScheduledProgram.station_id=station_id)
    if request.args.get('updated_since'):
        try:
           # updated_s = parse_datetime(request.args.get('updated_since')
	    message = jsonify(flag='error', msg="Scheduled programs Unable to parse station analytic form.")
            return message
        except (ValueError, TypeError):
            message = jsonify(flag='error', msg="ScheduledPrograms Unable to parse updated_since parameter. Must be ISO datetime format")
            abort(make_response(message, 400))
    else:
	r= {'created_at':station.scheduled_programs.created_at,'program_id':station.scheduled_programs.program.id}
	return r
     



@api.route('/program/<int:program_id>/episodes', methods=['GET'])
@api_key_or_auth_required
@returns_json
def program_episodes(program_id):
    """API method to get all episodes currently available for a program"""
    program = Program.query.filter_by(id=program_id).first_or_404()
    episodes = program.episodes

    if request.args.get('updated_since'):
        try:
            updated_since = parse_datetime(request.args.get('updated_since'))
            return episodes.filter(Episode.updated_at>updated_since)
        except (ValueError, TypeError):
            message = jsonify(flag='error', msg="Unable to parse updated_since parameter. Must be ISO datetime format")
            abort(make_response(message, 400)) 
    else:
        return episodes.all()

