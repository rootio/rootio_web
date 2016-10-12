import zmq
import time
import random

ADDRESS = "ipc:///tmp/zmq.sock"
PATTERN = "PUB"

context = zmq.Context()
socket = context.socket(getattr(zmq,PATTERN))
socket.connect(ADDRESS)
print "publish on %s as %s" % (ADDRESS, PATTERN)

# Ensure subscriber connection has time to complete
time.sleep(1)

messages = ['hi', 'hello', 'how are you?']

while True:
    try:
        topic = random.randint(0,3)
        msg = random.choice(messages)
        print "%s: %s" % (topic, msg)
        socket.send_json((topic, msg))
        time.sleep(1)

    except KeyboardInterrupt:
        print "goodbye"
        break