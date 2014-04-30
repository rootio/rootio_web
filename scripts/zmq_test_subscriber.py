import zmq
import datetime

ADDRESS = "ipc:///tmp/zmq.sock"
PATTERN = "SUB"

context = zmq.Context()
subscriber = context.socket(getattr(zmq,PATTERN))
subscriber.bind(ADDRESS)
print "listening to %s as %s" % (ADDRESS, PATTERN)

subscriber.setsockopt(zmq.SUBSCRIBE, '1') #subscribe to all
while True:
    try:
        topic, data = subscriber.recv_multipart()
        print "%s -- %s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, data)
    except KeyboardInterrupt:
        print "goodbye"
        break