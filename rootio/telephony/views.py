from flask import g, Blueprint, render_template, request, flash, Response, json
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext as _

from .models import PhoneNumber, Message, Call, Gateway
from .forms import PhoneNumberForm

from ..utils import error_dict
from ..decorators import returns_json
from ..extensions import db


telephony = Blueprint('telephony', __name__, url_prefix='/telephony')

@telephony.route('/', methods=['GET'])
def index():
    #Fix this: Re-write this using ORM
    summary_query = 'select radio_station.name "station", count(telephony_message) "messages", count(telephony_call) "calls", count(radio_incominggateway) "incoming_gateways", count(radio_outgoinggateway) "outgoing_gateways" from radio_station left outer join telephony_message on radio_station.id = telephony_message.id left outer join telephony_call on radio_station.id = telephony_call.station_id left outer join radio_incominggateway on radio_station.id = radio_incominggateway.station_id left outer join radio_outgoinggateway on radio_station.id = radio_outgoinggateway.station_id join radio_network on radio_station.network_id = radio_network.id join radio_networkusers on radio_network.id = radio_networkusers.network_id join user_user on radio_networkusers.user_id = user_user.id group by "station"'
    station_summary = db.session.execute(summary_query)
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


@telephony.route('/calls/', methods=['GET'])
def calls():
    recent_calls = Call.query.all()
    #todo, paginate?

    return render_template('telephony/calls.html', active='calls', calls=recent_calls)

@telephony.route('/messages/', methods=['GET'])
def messages():
    recent_messages = Message.query.all()
    #todo, paginate?

    return render_template('telephony/messages.html', active='messages', messages=recent_messages)

@telephony.route('/gateways/', methods=['GET'])
def gateways():
    #Fix this: Why cant these be imported at beginning of script???
    from ..user.models import User
    from ..radio.models import Station, Network 
    #incoming gateways associated to stations in my networks
    incoming_gateways = Gateway.query.with_entities(Gateway, Station.name).join(Gateway.stations_using_for_incoming).join(Network).join(User,Network.networkusers).filter(User.id==current_user.id).all() 
    outgoing_gateways = Gateway.query.with_entities(Gateway, Station.name).join(Gateway.stations_using_for_outgoing).join(Network).join(User,Network.networkusers).filter(User.id==current_user.id).all()
    q = outgoing_gateways[0][1]

    return render_template('telephony/gateways.html', active='gateways', incoming_gateways=incoming_gateways, outgoing_gateways=outgoing_gateways, q=q)
