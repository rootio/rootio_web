from ofs.local import PTOFS
import time
from datetime import datetime, timedelta
import json

class CommunityMedia:
    __bucket_keeper = None
    __bucket_id = None #o.claim_bucket("foo")
    __bucket_label = None

    __station_id = None

    def __init__(self, bucket_label, station_id):
        self.__station_id = station_id
        self.__bucket_label = bucket_label
        self.__bucket_keeper = PTOFS(storage_dir = "/home/amour/media/gdrive/Community Media/data") #current using pairtree with file system
        self.__bucket_id = "{0}_{1}".format(self.__station_id, self.__bucket_label)
        print "bucket id s " + self.__bucket_id 
        
    def add_news_file(self, news_file_location, extra_json):
        result = self.__bucket_keeper.put_stream(self.__bucket_id, news_file_location, extra_json)
        print result

    def get_media_files(self):
        media_files = []
        for label in self.__bucket_keeper.list_labels(self.__bucket_id):
            metadata_json = self.__bucket_keeper.get_metadata(self.__bucket_id, label)
            #metadata_json = json.loads(metadata)
            if self.__is_valid(metadata_json["_creation_date"], metadata_json["validity"]):
                file_url = self.__bucket_keeper.get_url(self.__bucket_id, label)
                media_files.append(self.__sanitize_url(file_url))
        return media_files 

    def __is_valid(self, creation_date, validity):
        sanitized_time = creation_date.replace('T', ' ')
        creation_time = datetime.strptime(sanitized_time, '%Y-%m-%d %H:%M:%S')
        #creation_time = time.mktime(creation_time_tuple) 
        time_delta = timedelta(days=int(validity))
        now = datetime.utcnow()
        return (time_delta + creation_time) > now
   
    def __sanitize_url(self, url): 
        parts = url.split("://")
        return parts[len(parts) - 1]     
