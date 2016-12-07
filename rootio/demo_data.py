from pathlib import Path
from datetime import datetime, timedelta
import json
import pytz
from .user.models import User
from .radio.models import Network, Station, Program, ScheduledProgram
from .telephony.models import PhoneNumber, Gateway
from .telephony.constants import MOBILE
from .content.models import ContentTrack, ContentUploads

from .config import DefaultConfig
DEMO_MEDIA_PREFIX = Path(DefaultConfig.DEMO_MEDIA_PREFIX)

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
        db.session.flush()

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
        db.session.flush()

    network = Network.query.filter_by(name=NETWORK_NAME).first()
    if network is None:
        network = Network(
            name=NETWORK_NAME,
            #networkusers=[admin],
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
        db.session.flush()

    TRACK_NAME = 'testdata-bbc-track'
    track = ContentTrack.query.filter_by(name=TRACK_NAME)
    if track is None:
        track = ContentTrack(
            name=TRACK_NAME,
        )
        db.session.add(track)
        db.session.flush()

    UPLOAD_NAME = 'testdata-bbc-upload'
    upload = ContentUploads.query.filter_by(name=UPLOAD_NAME).first()
    if upload is None:
        upload = ContentUploads(
            name=UPLOAD_NAME,
            order=1,
        )
        db.session.add(upload)
        db.session.flush()

    program = Program.query.filter_by(name=PROGRAM_NAME).first()
    if program is None:
        media_action = {
            'type': 'Media',
            'track_id': upload.track_id,
            'start_time': '00:00:01',
            'duration': PROGRAM_DURATION,
        }
        structure = [media_action]

        program = Program(
            name=PROGRAM_NAME,
            duration=timedelta(minutes=PROGRAM_DURATION),
            structure=json.dumps(structure, indent=2),
        )
        db.session.add(program)
        db.session.flush()

    if schedule:
        now = pytz.utc.localize(datetime.utcnow())
        start = now + timedelta(seconds=schedule)

        scheduled_program = ScheduledProgram(
            station_id=station.id,
            program=program,
            start=start,
            end=start + timedelta(minutes=PROGRAM_DURATION),
            deleted=False,
        )
        db.session.add(scheduled_program)
        db.session.flush()

    db.session.commit()
