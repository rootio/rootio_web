from pathlib import Path
from datetime import datetime, timedelta
import json
import flask
import pytz
from .user.models import User
from .radio.models import Network, Station, Program, ScheduledProgram
from .telephony.models import PhoneNumber, Gateway
from .telephony.constants import MOBILE
from .content.models import ContentTrack, ContentUploads

app = flask.current_app
MEDIA_PREFIX = Path(app.config['MEDIA_PREFIX'])

PHONE_NUMBER = '1007'
GATEWAY_NAME = 'Internal 4000'
NETWORK_NAME = "Testy network"
STATION_NAME = "Testy sounds"
PROGRAM_NAME = "BBC Africa Today"
PROGRAM_DURATION = 40

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

    TRACK_NAME = 'testdata-bbc-track'
    track = ContentTrack.query.filter_by(name=TRACK_NAME)
    if track is None:
        track = ContentTrack(
            name=TRACK_NAME,
        )
        db.session.add(track)

    UPLOAD_NAME = 'testdata-bbc-upload'
    upload = ContentUploads.query.filter_by(name=UPLOAD_NAME).first()
    if upload is None:
        upload = ContentUploads(
            name=UPLOAD_NAME,
            order=1,
        )
        db.session.add(upload)

    program = Program.query.filter_by(name=PROGRAM_NAME).first()
    if program is None:
        media_action = {
            'type': 'Media',
            'track_id': upload.track_id,
            'start_time': '00:00:01',
            'duration': PROGRAM_DURATION,
        }
        program = Program(
            name=PROGRAM_NAME,
            structure=json.dumps([media_action], indent=2),
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
