# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Nov 19, 2014 4:16:15 PM$"

import os
import sys

sys.path.append('/usr/local/rootio_web/')

from rootio.config import DefaultConfig, BaseConfig
from rootio.radio.models import Station #Even though intellij warns unused, do not remove this import. or you will get weird random errors
from rss_agent import RSSAgent
from datetime import datetime

import logging
from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler


class RSSRunner():

    def __init__(self, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.logger = logging.getLogger('rss_downloader')
        self.run()

    def run(self):
        self.__prepare_logging()

        rss_server = RSSAgent(self.logger)
        rss_server.run()
        print "================ RSS runner service started at {0} ==============".format(datetime.utcnow())

    def __prepare_logging(self):
        log_folder = DefaultConfig.LOG_FOLDER
        file_hdlr = TimedRotatingFileHandler(os.path.join(log_folder, 'rssdownloader.log'), when='midnight', interval=1)
        stream_hdlr = StreamHandler(stream=sys.stdout)

        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_hdlr.setFormatter(formatter)
        stream_hdlr.setFormatter(formatter)

        self.logger.addHandler(file_hdlr)
        self.logger.addHandler(stream_hdlr)

        self.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    rss_daemon = RSSRunner()
