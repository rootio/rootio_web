from ofs.local import PTOFS

o = PTOFS()
bucket_id = "foo" #o.claim_bucket("foo")
print bucket_id

result = o.put_stream(bucket_id, "foo3.txt", "hello there Mclovin!")
print result

for item in o.list_labels(bucket_id):
    print item
