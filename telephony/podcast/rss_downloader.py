import urllib
from datetime import datetime, timedelta
from time import mktime

import feedparser
from rootio.config import *
from rootio.content.models import ContentPodcast, ContentPodcastDownload
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
import re


class RSSDownloader:

    def __init__(self, podcast_id):
        self.__podcast_id = podcast_id
        self.__db = self.__get_db_connection()
        self.__get_podcast()

    def download(self):
        base_date = self.__get_last_publish_date()
        podcast_list = self.__get_podcast_list(base_date)
        print "found podcasts {0}".format(podcast_list)
        self.__download_podcasts(podcast_list)
        self.__close_db_connection()

    def __get_db_connection(self):
        engine = create_engine(DefaultConfig.SQLALCHEMY_DATABASE_URI)
        return sessionmaker(bind=engine)()

    def __close_db_connection(self):
        try:
            self.__db.close()
        except:
            return

    def __get_podcast(self):
        self.__podcast = self.__db.query(ContentPodcast).filter(ContentPodcast.id == self.__podcast_id).first()

    def __get_last_publish_date(self):
        try:
            last_podcast = self.__db.query(ContentPodcastDownload).filter(
                ContentPodcastDownload.podcast_id == self.__podcast.id).order_by(
                desc(ContentPodcastDownload.date_created)).first()
            if last_podcast is not None:
                return last_podcast.date_created
            else:  # default to last 1 week, in case of weeklies
                return datetime.utcnow() + timedelta(days=-7)
        except Exception as e:
            print e

    def __get_podcast_list(self, base_date):
        podcasts = []
        rss_feed = feedparser.parse(self.__podcast.uri)
        if rss_feed is not None:
            for entry in rss_feed.entries:
                # print entry.title
                try:
                    # Expected formats["Fri, 5 Oct 2018 16:53:00 GMT","Fri, 21 Sep 2018 12:01:00 -0400"]
                    dt_parts = entry.published.split(' ')
                    published_date = datetime.strptime(
                        "{0} {1} {2} {3}".format(dt_parts[1], dt_parts[2], dt_parts[3], dt_parts[4]),
                        "%d %b %Y %H:%M:%S")
                    #Some podcasts entries do not have published_parsed
                    if datetime.fromtimestamp(mktime(entry.published_parsed)) > base_date.replace(tzinfo=None):
                    #f published_date > base_date.replace(tzinfo=None):
                        podcasts.append(entry)
                except Exception as e:
                    print e
                    pass  # continue to the next entry. TODO: introduce logging here
        return podcasts

    def __download_podcasts(self, podcasts):
        try:
            if not os.path.exists(os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast.id))):
                os.makedirs(os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast.id)))
        except Exception as e:
            print e
            return  # path does not exist, could not be created. No point proceeding to download
        for podcast in podcasts:
            for link in podcast.links:
                try:
                    if link.type == u'audio/mpeg':
                        print "downloading podcast {0}".format(link.href)
                        # print "{0} {1} {2}".format(podcast.published, podcast.published_parsed, datetime.fromtimestamp(mktime(podcast.published_parsed)))
                        urllib.urlretrieve(link.href,
                                           os.path.join(DefaultConfig.CONTENT_DIR, 'podcast', str(self.__podcast.id),
                                                        re.sub(r'[^\w\d-]', '_', podcast.title[0:50]) + ".mp3"))
                        self.__log_podcast_download(podcast.title, podcast.itunes_duration,
                                                    re.sub(r'[^\w\d-]', '_', podcast.title[0:50]) + ".mp3",
                                                    podcast.summary,
                                                    datetime.fromtimestamp(mktime(podcast.published_parsed)))
                except Exception as e:  # Download error, DB error
                    print e
                    pass

    def __log_podcast_download(self, title, duration, file_name, summary, date_created):
        podcast_download = ContentPodcastDownload()
        podcast_download.name = title
        podcast_download.podcast_id = self.__podcast.id
        podcast_download.duration = duration
        podcast_download.file_name = file_name
        podcast_download.summary = summary
        podcast_download.date_created = date_created
        podcast_download.date_published = date_created

        try:
            self.__db._model_changes = {}
            self.__db.add(podcast_download)
            self.__db.commit()
        except:
            self.__db.rollback()
