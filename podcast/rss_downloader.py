import urllib
from datetime import datetime, timedelta
from time import mktime

import feedparser
from rootio.config import *
from rootio.content.models import ContentPodcast, ContentPodcastDownload
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker


class RSSDownloader:

    def __init__(self, podcast_id):
        self.__podcast_id = podcast_id
        self.__db = self.__get_db_connection()
        self.__get_podcast()

    def download(self):
        base_date = self.__get_last_publish_date()
        podcast_list = self.__get_podcast_list(base_date)
        self.__download_podcasts(podcast_list)

    def __get_db_connection(self):
        engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
        return sessionmaker(bind=engine)()

    def __get_podcast(self):
        self.__podcast = self.__db.query(ContentPodcast).filter(ContentPodcast.id == self.__podcast_id).first()

    def __get_last_publish_date(self):
        last_podcast = self.__db.query(ContentPodcastDownload).filter(
            ContentPodcastDownload.podcast_id == self.__podcast.id).order_by(
            desc(ContentPodcastDownload.date_created)).first()
        if last_podcast is not None:
            return last_podcast.date_created
        else:  # default to last 1 week, in case of weeklies
            return datetime.utcnow() + timedelta(days=-7)

    def __get_podcast_list(self, base_date):
        podcasts = []
        rss_feed = feedparser.parse(self.__podcast.uri)
        for entry in rss_feed.entries:
            if datetime.fromtimestamp(mktime(entry.published_parsed)) > base_date.replace(tzinfo=None):
                podcasts.append(entry)
        return podcasts

    def __download_podcasts(self, podcasts):
        for podcast in podcasts:
            if not os.path.exists(os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast.id))):
                os.makedirs(os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast.id)))
            for link in podcast.links:
                if link.type == u'audio/mpeg':
                    urllib.urlretrieve(link.href,
                                       os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast.id),
                                                    podcast.title[0:50] + ".mp3"))
                    self.__log_podcast_download(podcast.title, podcast.itunes_duration, podcast.title[0:50] + ".mp3",
                                                podcast.summary,
                                                datetime.fromtimestamp(mktime(podcast.published_parsed)))

    def __log_podcast_download(self, title, duration, file_name, summary, date_created):
        podcast_download = ContentPodcastDownload()
        podcast_download.name = title
        podcast_download.podcast_id = self.__podcast.id
        podcast_download.duration = duration
        podcast_download.file_name = file_name
        podcast_download.summary = summary
        podcast_download.date_created = date_created

        self.__db._model_changes = {}
        self.__db.add(podcast_download)
        self.__db.commit()
