import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from rootio.config import DefaultConfig
from daemon.daemoner import Daemon
from rss_agent import RSSAgent


class RSSRunner(Daemon):

    def __init__(self):
        self.logger = logging.getLogger('rss_downloader')
        hdlr = TimedRotatingFileHandler(os.path.join(DefaultConfig.LOG_FOLDER, 'rss.log'), when='midnight', interval=1)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.DEBUG)

    def run(self):
        rss_server = RSSAgent(self.logger)
        rss_server.run()


if __name__ == "__main__":
    rss_daemon = RSSRunner("/tmp/rss_runner.pid")
    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            rss_daemon.start()
            rss_daemon.logger.info("RSS service started")
        elif sys.argv[1] == "stop":
            rss_daemon.stop()
            rss_daemon.logger.info("RSS service stopped")
        elif sys.argv[1] == "restart":
            rss_daemon.restart()
            rss_daemon.logger.info("RSS service restarted")
        else:
            print "Wrong arguments supplied. Usage: rss_download_runner start|stop|restart"
    else:
        print "Wrong number of arguments supplied. Usage: rss_download_runner start|stop|restart"
