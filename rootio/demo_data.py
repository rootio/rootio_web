from .user.models import User
from .radio.models import Station
from .telephony.models import PhoneNumber
from .telephony.constants import MOBILE

PHONE_NUMBER = '1007'
STATION_NAME = "Testy sounds"

def setup(db):
    admin = User.query.get(1)

    phone = PhoneNumber.query.filter_by(number=PHONE_NUMBER).first()
    if phone is None:
        phone = PhoneNumber(
            number=PHONE_NUMBER,
            number_type=MOBILE,
        )
        db.session.add(phone)

    station = Station.query.filter_by(name=STATION_NAME).first()
    if station is None:
        station = Station(
            name=STATION_NAME,
            about="This is a station used only for test purposes",
            frequency='103.8',
            timezone='Africa/Abidjan',
            owner=admin,
            transmitter_phone=phone,
            client_update_frequency=30,
            analytic_update_frequency=30,
            broadcast_ip='230.255.255.257',
        )
        db.session.add(station)

    db.session.commit()
