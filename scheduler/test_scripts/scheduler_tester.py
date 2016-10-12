import zmq
import random
import sys
import time
import datetime
import dateutil
from dateutil.tz import *


port = "55777"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect("tcp://localhost:%s" % port)

topic = 'scheduler'
start = datetime.datetime.now(tzutc()).replace(microsecond=0) + datetime.timedelta(seconds = 15)
start = datetime.datetime.isoformat(start)
msg = """{"operation": "update", "start_time": "%s", "station_id": 8, "program_id": 5, "obj_id": 451}""" % start
multipart = [topic, msg]
time.sleep(.1)
print multipart
print socket.send_multipart(multipart)
