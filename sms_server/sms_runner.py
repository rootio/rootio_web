# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 4:16:15 PM$"

import sys
#sys.path.append('/home/amour/RootIO_Web_Old/'
from rootio.config import *
from rootio.radio.models import Station
from rootio.radiostation.call_handler import CallHandler
from rootio.radiostation.radio_station import RadioStation
from rootio.radiostation.daemon.daemoner import Daemon
from sms_server import SMSServer
from datetime import datetime
import threading
import logging
from logging.handlers import TimedRotatingFileHandler 

class SMSRunner(Daemon):

    def run(self):
        app_logger = logging.getLogger('sms_server')
        hdlr = TimedRotatingFileHandler('/var/log/rootio/smsserver.log',when='midnight',interval=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        app_logger.addHandler(hdlr)
        app_logger.setLevel(logging.DEBUG)

        sms_server = SMSServer(app_logger)
        sms_server.run()
        print "================ SMS service started at {0} ==============".format(datetime.utcnow())



if __name__ == "__main__":
    sms_daemon = SMSRunner("/tmp/sms_runner.pid")
    if(len(sys.argv) == 2):
        if sys.argv[1] == "start":
            sms_daemon.start()
        elif sys.argv[1] == "stop":
            sms_daemon.stop()
        elif sys.argv[1] == "restart": 
            sms_daemon.restart()
        else:
            print "Wrong arguments supplied. Usage: sms_runner start|stop|restart"
    else:
        print "Wrong number of arguments supplied. Usage: sms_runner start|stop|restart"         
         
