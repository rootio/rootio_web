from rss_downloader import RSSDownloader
import os
from time import sleep
import feedparser
from datetime import datetime, timedelta
from time import mktime
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from rootio.content.models import ContentPodcast, ContentPodcastDownload
from rootio.config import DefaultConfig
import threading 

class RSSAgent:
    def __init__(self, logger):
        self.logger = logger

    def __get_podcast_tracks(self):
        engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
        session = sessionmaker(bind=engine)()
        return session.query(ContentPodcast).all()

    def run(self):
        print("running....")
        while True:
            print "found podcasts " + str(len(self.__get_podcast_tracks()))
            for podcast_track in self.__get_podcast_tracks():
                pd = RSSDownloader(podcast_track.id)
                thr = threading.Thread(target=pd.download)
                thr.daemon = True
                thr.start()
            sleep(300) #5 minutes

