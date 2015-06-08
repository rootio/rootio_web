from ofs.local import PTOFS

o = PTOFS(storage_dir = "/home/amour/media/gdrive/Community Media/data")
bucket_id = "11_1" #o.claim_bucket("foo")
print bucket_id

#result = o.put_stream(bucket_id, "foo3.txt", "hello there Mclovin!")
#print result

for item in o.list_labels(bucket_id):
    print item
