from ofs.local import PTOFS


class News:
    __bucket_keeper = None
    __bucket_id = None #o.claim_bucket("foo")
    __bucket_label = None

    result = o.put_stream(bucket_id, "foo3.txt", "hello there Mclovin!")
    print result

    for item in o.list_labels(bucket_id):
        print itemi
 
    

    __station_id = None

    def __init__(self, bucket_label, station_id):
        self.__station_id = station_id
        self.__bucket_label = bucket_label
        self.__bucket_keeper = PTOFS() #current using pairtree with file system
        self.__bucket_id = "{0}_{1}".format({self.__bucket_label, self.__station_id})
        
        
    def add_news_file(self, news_file_location, extra_json):
        result = self.__bucket_keeper.put_stream(self.__bucket_id, news_file_location, extra_json)
        print result

    def get_news_files(self):
        return self.__bucket_keeper.list(self.__bucket_id)

    def get_latest_news_file(self):
        pass
    
    
