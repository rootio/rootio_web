import zmq
import datetime
import random

port = "5556"
pattern = "SUB"

context = zmq.Context()
subscriber = context.socket(getattr(zmq,pattern))
subscriber.connect("tcp://localhost:%s" % port)
print "subscribe on %s as %s" % (port, pattern)

subscriber.setsockopt(zmq.SUBSCRIBE, "") #subscribe to all
while True:
    try:
        topic, data = subscriber.recv_multipart()
        print "%s -- %s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, data)
    except KeyboardInterrupt:
        print "goodbye"
        break