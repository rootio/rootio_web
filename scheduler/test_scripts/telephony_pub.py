#test publisher to telephony

import zmq
import datetime, time

ADDRESS = "tcp://127.0.0.1:5556"
PATTERN = "PUB"

context = zmq.Context()
socket = context.socket(getattr(zmq,PATTERN))
socket.bind(ADDRESS)
print "bind on %s as %s" % (ADDRESS, PATTERN)

while True:
    try:
        topic, message = ['topic','message']
        socket.send_json((topic, message))
        print "%s -- %s: %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, message)
        time.sleep(1)
    except KeyboardInterrupt:
        print "goodbye"
        break