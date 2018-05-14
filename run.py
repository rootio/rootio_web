#!/usr/bin/env python

import logging
import sys
import threading

import flask
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('settings.py')
db = SQLAlchemy(app)

sys.path.append(app.config['ROOTIO_WEB_PATH'])


def run():
    from rootio.radio.models import Station
    import radio_station

    logging.basicConfig()
    logger = logging.getLogger('station_runner')

    radio_station.telephony_server = app

    stations = db.session.query(Station)
    for station in stations.all():
        radio_station = radio_station.RadioStation(station.id, db.session, logger)
        logger.info('launching station : {0}'.format(station.id))
        t = threading.Thread(target=radio_station.run, args=())
        t.start()

    print "radio station telephony service started"


if __name__ == "__main__":
    run()
