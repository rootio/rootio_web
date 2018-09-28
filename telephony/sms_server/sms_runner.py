import logging
import sys
from logging.handlers import TimedRotatingFileHandler

from rootio.config import *

from telephony.daemon.daemoner import Daemon
from sms_server import SMSServer


class SMSRunner(Daemon):

    def __init__(self):
        self.logger = logging.getLogger('sms_server')
        hdlr = TimedRotatingFileHandler(os.path.join(DefaultConfig.LOG_FOLDER, 'smsserver.log'),
                                        when='midnight', interval=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.DEBUG)

    def run(self):
        sms_server = SMSServer(self.logger)
        sms_server.run()


if __name__ == "__main__":
    sms_daemon = SMSRunner("/tmp/sms_runner.pid")
    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            sms_daemon.start()
            sms_daemon.logger.info("Station service started")
        elif sys.argv[1] == "stop":
            sms_daemon.stop()
            sms_daemon.logger.info("Station service stopped")
        elif sys.argv[1] == "restart":
            sms_daemon.restart()
            sms_daemon.logger.info("Station service restarted")
        else:
            print "Wrong arguments supplied. Usage: sms_runner start|stop|restart"
    else:
        print "Wrong number of arguments supplied. Usage: sms_runner start|stop|restart"
