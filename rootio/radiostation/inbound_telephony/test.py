from ofs.local import PTOFS

o = PTOFS(storage_dir = "/home/amour/data")
bucket_id ="1_advertisments"# "1_advertisments" #o.claim_bucket("foo")
print bucket_id

#result = o.put_stream(bucket_id, "foo3.wav", open("/home/amour/20150316104826_0774712133.wav"), params={"validity" : 5})
#print result

for item in o.list_labels(bucket_id):
    print item
    t = o.get_metadata(bucket_id, item)
    print t
