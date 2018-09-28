#test subscriber for telephony

import zmq
import datetime

ADDRESS = "tcp://127.0.0.1:5556"
PATTERN = "SUB"

context = zmq.Context()
socket = context.socket(getattr(zmq,PATTERN))
socket.connect(ADDRESS)
print "connect to %s as %s" % (ADDRESS, PATTERN)

socket.setsockopt(zmq.SUBSCRIBE, '')

while True:
    try:
        topic, message = socket.recv_json()
        print "%s -- %s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, message)
    except KeyboardInterrupt:
        print "goodbye"
        break