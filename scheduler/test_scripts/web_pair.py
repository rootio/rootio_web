# test ipc pair, acts as rootio_web

import zmq
import time
import random

ADDRESS = "ipc:///tmp/zmq.sock"
PATTERN = "PAIR"

context = zmq.Context()
socket = context.socket(getattr(zmq,PATTERN))
socket.connect(ADDRESS)
print "connect on %s as %s" % (ADDRESS, PATTERN)

# Ensure subscriber connection has time to complete
time.sleep(1)

fake_messages = {
    # 'zmq': [{'status':'startup'},
    #         {'status':'shutdown'}
    #     ],
    'scheduler': [
            { 'msg': 'hi' },
            { 'msg': 'hey' },
            { 'msg': 'hello' },
        ],
    # 'station': [
    #         { 'msg': 'howdy' },
    #         { 'msg': 'sup' },
    #         { 'msg': 'greetings' },
    #     ],
    # 'emergency': [
    #         { 'msg': 'run!' },
    #     ]
    }

while True:
    try:
        topic = random.choice(fake_messages.keys())
        msg = random.choice(fake_messages[topic])
        print "%s: %s" % (topic, msg)
        socket.send_json((topic, msg))
        time.sleep(1)

    except KeyboardInterrupt:
        print "goodbye"
        break