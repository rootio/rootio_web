from flask import g, Blueprint, render_template, request, flash, Response, json, jsonify
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _
import socket
from .models import PhoneNumber, Message, Call, Gateway
from .forms import PhoneNumberForm
#from ..user.models import User
#from rootio.radio.models import Station
from ..utils import error_dict, jquery_dt_paginator
from ..decorators import returns_json
from ..extensions import db
from sqlalchemy import text, or_

telephony = Blueprint('telephony', __name__, url_prefix='/telephony')

@telephony.route('/', methods=['GET'])
def index():
    #Fix this: Re-write this using ORM
    summary_query = 'select radio_station.name "station", (select count(*) from telephony_message where telephony_message.station_id = radio_station.id) "messages", (select count(*) from telephony_call where telephony_call.station_id = radio_station.id) "calls", (select count(*) from radio_incominggateway where radio_incominggateway.station_id = radio_station.id) "incoming_gateways", (select count(*) from radio_outgoinggateway where radio_outgoinggateway.station_id = radio_station.id)  "outgoing_gateways" from radio_station  join radio_network on radio_station.network_id = radio_network.id join radio_networkusers on radio_network.id = radio_networkusers.network_id join user_user on radio_networkusers.user_id = user_user.id where user_user.id = :user_id group by "station", radio_station.id'
    query_params  = {'user_id':current_user.id}
    station_summary = db.session.execute(summary_query, query_params)
    return render_template('telephony/index.html',station_summary=station_summary)


@telephony.route('/phonenumber/', methods=['GET'])
def phonenumbers():
    phonenumbers = PhoneNumber.query.all()
    return render_template('telephony/phonenumbers.html', phonenumbers=phonenumbers, active='phonenumbers')


@telephony.route('/phonenumber/<int:phonenumber_id>', methods=['GET', 'POST'])
def phonenumber(phonenumber_id):
    phonenumber = PhoneNumber.query.filter_by(id=phonenumber_id).first_or_404()
    form = PhoneNumberForm(obj=phonenumber, next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(phonenumber)

        db.session.add(phonenumber)
        db.session.commit()
        flash(_('Phone Number updated.'), 'success')

    return render_template('telephony/phonenumber.html', phonenumber=phonenumber, form=form)


@telephony.route('/phonenumber/add/', methods=['GET', 'POST'])
@login_required
def phonenumber_add():
    form = PhoneNumberForm(request.form)
    phonenumber = None

    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        phonenumber = PhoneNumber(**cleaned_data) #create new object from data

        db.session.add(phonenumber)
        db.session.commit()
        flash(_('Phone Number added.'), 'success') 
    elif request.method == "POST":
        flash('Validation error','error')

    return render_template('telephony/phonenumber.html', phonenumber=phonenumber, form=form)


@telephony.route('/phonenumber/add/ajax/', methods=['POST'])
@login_required
@returns_json
def phonenumber_add_inline():
    data = json.loads(request.data)
    form = PhoneNumberForm(None, **data) #use this format to avoid multidict-type issue
    phonenumber = None
    if form.validate_on_submit():
        cleaned_data = form.data #make a copy
        cleaned_data.pop('submit',None) #remove submit field from list
        phonenumber = PhoneNumber(**cleaned_data) #create new object from data
        db.session.add(phonenumber)
        db.session.commit()
        response = {'status':'success','result':{'id':phonenumber.id,'string':unicode(phonenumber)},'status_code':200}
    elif request.method == "POST":
        #convert the error dictionary to something serializable
        response = {'status':'error','errors':error_dict(form.errors),'status_code':400}
    return response

@telephony.route('/calls/records', methods=['GET'])
#@returns_json
def call_records(**kwargs):
    from ..user.models import User
    from ..radio.models import Station, Network
    cols = [Call.call_uuid, Call.start_time, Call.duration, Call.from_phonenumber, Call.to_phonenumber, Station.name]
    recent_calls = Call.query.with_entities(*cols).join(Station).join(Network).join(User,Network.networkusers).filter(User.id==current_user.id)
    
    records = jquery_dt_paginator.get_records(recent_calls, [Call.call_uuid, Call.from_phonenumber, Call.to_phonenumber, Station.name], request)
    return jsonify(records)

@telephony.route('/calls/', methods=['GET'])
def calls(**kwargs):
    return render_template('telephony/calls.html', active='calls')

@telephony.route('/messages/', methods=['GET'])
def messages():
    return render_template('telephony/messages.html', active='messages')

@telephony.route('/messages/records', methods=['GET'])
def message_records():
    from ..user.models import User
    from ..radio.models import Station, Network
    cols = [Message.sendtime, Message.text, Message.from_phonenumber, Message.to_phonenumber, Station.name]
    recent_messages = Message.query.with_entities(*cols).join(Station).join(Network).join(User,Network.networkusers).filter(User.id==current_user.id)
    
    records = jquery_dt_paginator.get_records(recent_messages, [Message.text, Message.from_phonenumber, Message.to_phonenumber, Station.name], request)
    return jsonify(records)


@telephony.route('/gateways/', methods=['GET'])
def gateways():
    #Fix this: Why cant these be imported at beginning of script???
    from ..user.models import User
    from ..radio.models import Station, Network 
    #incoming gateways associated to stations in my networks
    incoming_gateways = Gateway.query.with_entities(Gateway, Station.name).join(Gateway.stations_using_for_incoming).join(Network).join(User,Network.networkusers).filter(User.id==current_user.id).all() 
    outgoing_gateways = Gateway.query.with_entities(Gateway, Station.name).join(Gateway.stations_using_for_outgoing).join(Network).join(User,Network.networkusers).filter(User.id==current_user.id).all()
    return render_template('telephony/gateways.html', active='gateways', incoming_gateways=incoming_gateways, outgoing_gateways=outgoing_gateways)

def query_sms_server(query_string):
    from ..config import DefaultConfig
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (DefaultConfig.SMS_SERVER_IP, DefaultConfig.SMS_SERVER_PORT)
    s.connect(addr)
    s.send(query_string)
    data = s.recv(1024) #USSD returns ~160 chars
    s.close()
    return data
 
@telephony.route('/check_credit/<int:gateway_id>', methods=['GET'])
@returns_json
def check_credit(gateway_id):
    gw = Gateway.query.filter(Gateway.id==gateway_id).first_or_404()
    query_string ='{"transaction_type":"USSD", "line":"1", "transactions": ["*131#"]}' # '{{"transaction_type":"USSD", "line":"{0}", "transactions": {1}}}'.format(gw.gateway_prefix, gw.number_bottom)
    response = query_sms_server(query_string)
    return response

