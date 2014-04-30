import zmq
import datetime

ADDRESS = "ipc:///tmp/zmq.sock"
#ADDRESS = "tcp://127.0.0.1:5556"
PATTERN = "SUB"

context = zmq.Context()
subscriber = context.socket(getattr(zmq,PATTERN))
subscriber.bind(ADDRESS)
print "listening to %s as %s" % (ADDRESS, PATTERN)

subscriber.setsockopt(zmq.SUBSCRIBE, '') #subscribe to all
while True:
    try:
        topic, message = subscriber.recv_json()
        print "%s -- %s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, message)
    except KeyboardInterrupt:
        print "goodbye"
        break