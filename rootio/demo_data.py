from pathlib import Path
from datetime import datetime, timedelta
import json
import pytz
from .user.models import User, RootioUser
from .radio.models import Location, Network, Station, Program, ScheduledProgram
from .radio.models import ContentType, ProgramType
from .telephony.models import PhoneNumber, Gateway
from .telephony.constants import MOBILE
from .content.models import ContentTrack, ContentUploads

from .config import DefaultConfig

TRANSMITTER_PHONE_NUMBER = '1007'
CLOUD_PHONE_NUMBER = '1006'
GATEWAY_NAME = 'Internal 4000'
NETWORK_NAME = "Testy network"
LOCATION_NAME = "Testy location"
STATION_NAME = "Testy sounds"
PROGRAM_NAME = "BBC Africa Today"
PROGRAM_DURATION = 40

def setup(db, schedule):
    admin = User.query.get(1)
    rootio_admin = RootioUser.query.get(admin.id)

    transmitter_phone = (PhoneNumber.query
        .filter_by(number=TRANSMITTER_PHONE_NUMBER).first())
    if transmitter_phone is None:
        transmitter_phone = PhoneNumber(
            number=TRANSMITTER_PHONE_NUMBER,
            number_type=MOBILE,
        )
        db.session.add(transmitter_phone)
        db.session.flush()
    print transmitter_phone

    cloud_phone = (PhoneNumber.query
        .filter_by(number=CLOUD_PHONE_NUMBER).first())
    if cloud_phone is None:
        cloud_phone = PhoneNumber(
            number=CLOUD_PHONE_NUMBER,
            number_type=MOBILE,
        )
        db.session.add(cloud_phone)
        db.session.flush()
    print cloud_phone

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
    print gateway

    network = Network.query.filter_by(name=NETWORK_NAME).first()
    if network is None:
        network = Network(
            name=NETWORK_NAME,
            networkusers=[rootio_admin],
        )
        db.session.add(network)
        db.session.flush()
    print network

    location = Location.query.filter_by(name=LOCATION_NAME).first()
    if location is None:
        location = Location(
            name=LOCATION_NAME,
        )
        db.session.add(location)
        db.session.flush()
    print location

    station = Station.query.filter_by(name=STATION_NAME).first()
    if station is None:
        station = Station(
            name=STATION_NAME,
            about="This is a station used only for test purposes",
            frequency='103.8',
            network=network,
            timezone='Africa/Abidjan',
            owner=admin,
            #transmitter_phone=transmitter_phone,
            #cloud_phone=cloud_phone,
            client_update_frequency=30,
            analytic_update_frequency=30,
            broadcast_ip='230.255.255.257',
            outgoing_gateways=[gateway],
            location=location,
            api_key='TESTAPIKEY',
        )
        db.session.add(station)
        db.session.flush()
    print station

    TRACK_NAME = 'testdata-bbc-track'
    track = ContentTrack.query.filter_by(name=TRACK_NAME).first()
    if track is None:
        track = ContentTrack(
            name=TRACK_NAME,
        )
        db.session.add(track)
        db.session.flush()
    print track

    UPLOAD_NAME = 'testdata-bbc-upload'
    upload = ContentUploads.query.filter_by(name=UPLOAD_NAME).first()
    if upload is None:
        upload = ContentUploads(
            name=UPLOAD_NAME,
            order=1,
        )
        db.session.add(upload)
        db.session.flush()
    print upload

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
    print program

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
        print scheduled_program

    content_type_media = ContentType.query.filter_by(name='Media').first()
    if content_type_media is None:
        content_type_media = ContentType(
            name='Media',
            description='',
        )
        db.session.add(content_type_media)
        db.session.flush()
    print content_type_media

    content_type_news = ContentType.query.filter_by(name='News').first()
    if content_type_news is None:
        content_type_news = ContentType(
            name='News',
            description='',
        )
        db.session.add(content_type_news)
        db.session.flush()
    print content_type_news

    program_type_talkshow = ProgramType.query.filter_by(name='Talk Show').first()
    if program_type_talkshow is None:
        program_type_talkshow = ContentType(
            name='Talk Show',
            description='',
            definition='',
            phone_functions='',
        )
        db.session.add(program_type_talkshow)
        db.session.flush()
    print program_type_talkshow

    db.session.commit()
