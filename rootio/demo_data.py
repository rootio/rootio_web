from pathlib import Path
from datetime import datetime, timedelta
import json
import flask
import pytz
from .user.models import User
from .radio.models import Network, Station, Program, ScheduledProgram
from .telephony.models import PhoneNumber, Gateway
from .telephony.constants import MOBILE

app = flask.current_app
MEDIA_PREFIX = Path(app.config['MEDIA_PREFIX'])

PHONE_NUMBER = '1007'
GATEWAY_NAME = 'Internal 4000'
NETWORK_NAME = "Testy network"
STATION_NAME = "Testy sounds"
PROGRAM_NAME = "BBC Africa Today"
PROGRAM_DURATION = 40
PROGRAM_DESCRIPTION = {
    'Media': [
        {
            'argument': [str(MEDIA_PREFIX / 'bbc/latest_africa.mp3')],
            'start_time': '00:00:01',
            'duration': PROGRAM_DURATION,
            'is_streamed': True,
            'hangup_on_complete': True,
        },
    ],
}

def setup(db, schedule):
    admin = User.query.get(1)

    phone = PhoneNumber.query.filter_by(number=PHONE_NUMBER).first()
    if phone is None:
        phone = PhoneNumber(
            number=PHONE_NUMBER,
            number_type=MOBILE,
        )
        db.session.add(phone)

    gateway = Gateway.query.filter_by(name=GATEWAY_NAME).first()
    if gateway is None:
        gateway = Gateway(
            name=GATEWAY_NAME,
            number_top=4000,
            number_bottom=4000,
            gateway_prefix='',
            sofia_string='user',
            extra_string='bridge_early_media=true,hangup_after_bridge=true,'
                'origination_caller_id_number=4000',
            is_goip=False,
        )
        db.session.add(gateway)

    network = Network.query.filter_by(name=NETWORK_NAME).first()
    if network is None:
        network = Network(
            name=NETWORK_NAME,
        )

    station = Station.query.filter_by(name=STATION_NAME).first()
    if station is None:
        station = Station(
            name=STATION_NAME,
            about="This is a station used only for test purposes",
            frequency='103.8',
            network=network,
            timezone='Africa/Abidjan',
            owner=admin,
            transmitter_phone=phone,
            client_update_frequency=30,
            analytic_update_frequency=30,
            broadcast_ip='230.255.255.257',
            outgoing_gateways=[gateway],
        )
        db.session.add(station)

    program = Program.query.filter_by(name=PROGRAM_NAME).first()
    if program is None:
        program = Program(
            name=PROGRAM_NAME,
            description=json.dumps(PROGRAM_DESCRIPTION, indent=2),
            duration=timedelta(minutes=PROGRAM_DURATION),
        )
        db.session.add(program)

    if schedule:
        station.scheduled_programs.delete()
        now = pytz.utc.localize(datetime.utcnow())
        start = now + timedelta(seconds=schedule)
        scheduled_program = ScheduledProgram(
            station=station,
            program=program,
            start=start,
            end=start + timedelta(minutes=PROGRAM_DURATION),
            deleted=False,
        )
        db.session.add(scheduled_program)

    db.session.commit()
