import sys
import zmq

port = "55778"
# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)
print "Collecting updates from server..."
socket.connect ("tcp://localhost:%s" % port)
topicfilter = ""
socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
for update_nbr in range(1000):
    s = socket.recv()
    print s
    print type(s)
#    topic, message = s[0]
#    print topic
#    print message
    # topic, messagedata = string.split()
    # print topic, messagedata
