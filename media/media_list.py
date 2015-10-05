from community_media import CommunityMedia
for station_id in ["10","11","12","13"]:
        for bucket_id in ["1","2"]:
            try:
                comm = CommunityMedia(bucket_id,station_id)
                items = comm.get_media_files()
                print items
            except Exception, ex:
                print str(ex)
