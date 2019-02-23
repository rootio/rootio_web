import threading
from time import sleep

from rootio.config import DefaultConfig
from rootio.content.models import ContentPodcast
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rss_downloader import RSSDownloader


class RSSAgent:
    def __init__(self, logger):
        self.__logger = logger

    def __get_podcast_tracks(self):
        session = None
        try:
            engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
            session = sessionmaker(bind=engine)()
            return session.query(ContentPodcast).all()
        except Exception as e:
            print e
            return []
        finally:
            try:
                if session is not None:
                    session.close()
            except: # some other error
                pass  # log this

    def run(self):
        while True:
            self.__logger.info("Checking for new podcasts")
            for podcast_track in self.__get_podcast_tracks():
                pd = RSSDownloader(podcast_track.id)
                thr = threading.Thread(target=pd.download)
                thr.daemon = True
                thr.start()
            sleep(300)  # 5 minutes
