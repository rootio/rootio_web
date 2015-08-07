# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, request, jsonify, abort, make_response, json, Response
from flask.ext.login import login_user, current_user, logout_user

from .utils import parse_datetime

from ..extensions import db, rest, csrf

from ..user import User
from ..radio import Station, Person, Program, ScheduledProgram, Episode, Recording, StationAnalytic, Role, ScheduledBlock
from ..radio.forms import StationAnalyticForm
from ..telephony import PhoneNumber, Call, Message
from ..onair import OnAirProgram

from ..decorators import returns_json, api_key_or_auth_required, restless_preprocessors, restless_postprocessors

from array import array

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


    rest.create_api(OnAirProgram, collection_name='onairprogram', methods=['GET'],
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
        analytics_list = StationAnalytic.query.filter_by(station_id=station.id).all()
        return analytics_list



@api.route('/station/<int:station_id>/scheduled_programs', methods=['GET'])
@api_key_or_auth_required
@returns_json
def scheduled_programs(station_id):
    """API method to get all scheduled programs  currently linked to this station"""
  
    station = Station.query.filter_by(id=station_id).first_or_404()  
    schedule_prog = station.scheduled_programs    
    if request.args.get('updated_since'):
        try:
            updated_since = parse_datetime(request.args.get('updated_since'))
            return schedule_prog.filter(ScheduledProgram.updated_at>updated_since)
        except (ValueError, TypeError):
            message = jsonify(flag='error', msg="Unable to parse updated_since parameter. Must be ISO datetime format")
            abort(make_response(message, 400))
    else:
	return schedule_prog.all()

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


@api.route('/station/<int:station_id>/user', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_user(station_id):
    """API method to get the user information currently linked to a station"""
    station = Station.query.filter_by(id=station_id).first_or_404()
    user = station.owner

    return user

@api.route('/person/<int:person_id>/role', methods=['GET'])
@api_key_or_auth_required
@returns_json
def person_role(person_id):
    """API method to get the role information currently linked to a person"""
    person = Person.query.filter_by(id=person_id).first_or_404()
    role = person.role
    return role


@api.route('/station/<int:station_id>/roles', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_roles(station_id):
    """API method to get the role information currently linked to a station"""
    station = Station.query.filter_by(id=station_id).first_or_404()
    roles = Role.query.filter_by(station_id=station.id)
    print "Station roles = %s" % roles.all()
    return roles.all()


@api.route('/person/<int:person_id>/phonenumber', methods=['GET'])
@api_key_or_auth_required
@returns_json
def person_phone(person_id):
    """API method to get the PhoneNumber currently linked to a person"""
    person = Person.query.filter_by(id=person_id).first_or_404()
    phone = PhoneNumber.query.filter_by(id=person.phone_id).first()
    if phone:
	print "Person %s Phone %s" % (person_id,phone)
        return {"Coutry code: ":phone.countrycode, "Number:  ": phone.number}
    else:
        return {'message': 'Unable to find person phonenumber.'}

@api.route('/episode/<int:episode_id>/message', methods=['GET'])
@api_key_or_auth_required
@returns_json
def episode_message(episode_id):
    """API method to get the message currently linked to an Episode"""
    episode = Episode.query.filter_by(id=episode_id).first_or_404()
    
    if episode:
	onair =  OnAirProgram.query.filter_by(episode_id=episode.id).first_or_404()

	if request.args.get('updated_since'):
		print "date = %s" % request.args.get('updated_since')
        	try:
            		updated_since = parse_datetime(request.args.get('updated_since'))
            		print "Updated: %s" % updated_since
			m = Message.query.filter_by(onairprogram_id=onair.id).filter(Message.updated_at>updated_since)
			print "Messages updated = %s" % m
			return Message.query.filter_by(onairprogram_id=onair.id).filter(Message.updated_at>updated_since)
	       	except (ValueError, TypeError):
            		message = jsonify(flag='error', msg="Unable to parse updated_since parameter %s. Must be ISO datetime format" % request.args.get('updated_since'))
            		abort(make_response(message, 400))
		except Exception, e:
               		message = jsonify(flag='error', msg="Unable to run messages by episode updated_since %s. " % e)
               		abort(make_response(message, 400))
    	elif request.args.get('send_time'):
    		try:
    			send_time = parse_datetime(request.args.get('send_time'))
			print "send: %s" % send_time
			send = Message.query.filter_by(onairprogram_id=onair.id).filter(Message.sendtime>send_time)
			print "Messages send: %s" % send
			return send
    	    	except (ValueError, TypeError):
    	        	message = jsonify(flag='error', msg="Unable to parse sendtime parameter %s. Must be ISO datetime format" % request.args.get('send_time'))
    	        	abort(make_response(message, 400))
		except Exception, e:
                        message = jsonify(flag='error', msg="Unable to run messages by episode send_time %s. " % e)
                        abort(make_response(message, 400))
    	else:
		all_msg = Message.query.filter_by(onairprogram_id=onair.id)
		print "Messages all: %s" % all_msg    
    		return all_msg
    else:
	return  {'message': 'Unable to find episodes.'}


@api.route('/station/<int:station_id>/scheduled_programs/messages', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_messages(station_id):
   """API method to get all messages currently linked to this station"""

   try:
      Men = Message.query.join(OnAirProgram).join(ScheduledProgram).join(Station).filter_by(id=station_id)
      if Men :
         if request.args.get('updated_since'):
            try:
               updated_since = parse_datetime(request.args.get('updated_since'))
               print "Messages updated =  %s" % Men.filter(Message.updated_at>updated_since)
               return Men.filter(Message.updated_at>updated_since)
            except Exception, e:
               message = jsonify(flag='error', msg="Unable to run messages updated_since %s. " % e)
               abort(make_response(message, 400))
         elif request.args.get('sent_time'):
            try:
               sent = parse_datetime(request.args.get('sent_time'))
               print "Messages sent time =  %s" % Men.filter(Message.sendtime>sent)
               return Men.filter(Message.sendtime>sent)
            except Exception, e:
               message = jsonify(flag='error', msg="Unable to run messages sent_time %s. " % e)
               abort(make_response(message, 400))
	 else:
            print "Messages else =  %s" % Men.all()
            return Men.all()
      else:
         print "else no Messages"
         return jsonify(flag='info', msg="No messages for this station.")
   except Exception, e:
      message = jsonify(flag='error', msg="Unable to run messages  %s. " % e)
      abort(make_response(message, 400))


@api.route('/station/<int:station_id>/analytics/delete', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_analytics_delete(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()
  
    analytics_list = StationAnalytic.query.filter_by(station_id=station.id).all()
    
    numberdeleted = 0
    for a in analytics_list:
        db.session.delete(a)
        db.session.commit()
        numberdeleted=numberdeleted+1
        
    return {'deleted':'sucess %s' % numberdeleted}



@api.route('/station/<int:station_id>/analytics/update', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_analytics_update(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()

    analytics = StationAnalytic.query.filter_by(id=3473).first()
    print "Analytics %s" % analytics
    analytics.battery_level = 94
    analytics.cpu_load = 10
    analytics.gps_lat = 10
    analytics.gps_lon = 10
    analytics.gsm_signal = 10
    analytics.memory_utilization = 10
    analytics.storage_usage = 10
    db.session.commit()

    return {'updated':'sucess'}



@api.route('/station/<int:station_id>/analytics/add', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_analytics_add(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()
    cpu = 0.108108
    mem =10.0
    storage = 32.0
    battery= 49.0
    gsm = 15.0
    wifi = True
    lat = 0.0
    longi = 0.0

    print "Save info = %s, %s, %s, %s, %s, %s, %s, %s" % (cpu,mem,storage,battery,gsm,wifi,lat,longi)
    analytic = StationAnalytic(cpu,mem,storage,battery,gsm,wifi,lat,longi) #create new object from data
    analytic.station = station

    db.session.add(analytic)
    db.session.commit()

    return {'updated':'sucess'}



@api.route('/station/<int:station_id>/scheduled_block/delete', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_scheduled_block_delete(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()

    sb_list = ScheduledBlock.query.filter_by(station_id=station.id).all()

    numberdeleted = 0
    for a in sb_list:
        db.session.delete(a)
        db.session.commit()
        numberdeleted=numberdeleted+1

    return {'deleted':'success %s' % numberdeleted}


@api.route('/station/<int:station_id>/scheduled_program/delete', methods=['GET'])
@api_key_or_auth_required
@returns_json
def station_scheduled_program_delete(station_id):
    """API method to get or post analytics for a station"""

    station = Station.query.filter_by(id=station_id).first_or_404()

    sp_list = ScheduledProgram.query.filter_by(station_id=station.id).all()

    numberdeleted = 0
    for a in sp_list:
        db.session.delete(a)
        db.session.commit()
        numberdeleted=numberdeleted+1

    return {'deleted':'success %s' % numberdeleted}



@api.route('/station/<int:station_id>/diagnostics', methods=['POST'])
@api_key_or_auth_required
@returns_json
def station_diagnostics_post(station_id):
    """API method to post analytics for a station"""

    print "Entrou .... %s" % str(request.values)
    print " query = %s" %request.query_string
    station = Station.query.filter_by(id=station_id).first_or_404()
    print ">>>>>>>>>station = %s" % station.id
    if request.method == "POST":
    	try:
            cpu =request.form.get('CPU Utilization')
            mem =request.form.get('Memory Utilization')
            storage =request.form.get('Storage Utilization')
            battery= request.form.get('Battery Level')
            gsm = request.form.get('GSM Strength')

            if float(request.form.get('WiFI Connectivity')) > float(0):
                wifi = True
            else:
                wifi = False

            lat = request.form.get('Latitude')
            longi = request.form.get('Longitude')

            print "Received info POST = %s, %s, %s, %s, %s, %s, %s, %s" % (cpu,mem,storage,battery,gsm,wifi,lat, longi)
            analytic = StationAnalytic(cpu,mem,storage,battery,gsm,wifi,lat,longi) #create new object from data
            analytic.station = station

            db.session.add(analytic)
            db.session.commit()
            return { "success": True}
    	except Exception, e:
            print "Exception: %s" % e
            message = jsonify(flag='error', msg="Exception:  %s. " % e)
            abort(make_response(message, 400))
