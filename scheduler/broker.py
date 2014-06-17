import zmq
from switch import switch
from datetime import datetime, timedelta
import json
import logging

MESSAGE_QUEUE_PORT_TELEPHONY = "55666"

from multiprocessing import Process
from zmq.eventloop import ioloop, zmqstream
ioloop.install()

class MessageBroker(object):
    def __init__(self, msg_scheduler):
        " Set up and bind sockets "
        
        # IPC pair socket to rootio_web
        self._web_pair_sock = zmq.Context().socket(zmq.PAIR)
        self._web_pair_sock.bind("ipc:///tmp/zmq.sock")
        self._web_pair_stream = zmqstream.ZMQStream(self._web_pair_sock)

        # TCP publisher socket to station daemons
        self._station_daemon_pub = zmq.Context().socket(zmq.PUB)
        self._station_daemon_pub.bind("tcp://127.0.0.1:5556")
        self._station_daemon_stream = zmqstream.ZMQStream(self._station_daemon_pub)

        # Subscribe to stream from rootio_telephony -- calls, messages, etc. 
        # then relay them to station daemons
        self._telephony_sock = zmq.Context().socket(zmq.SUB)
        self._telephony_sock.connect ("tcp://localhost:%s" % MESSAGE_QUEUE_PORT_TELEPHONY)
        self._telephony_stream = zmqstream.ZMQStream(self._telephony_sock)

        #set bidirectional links
        self._msg_scheduler = msg_scheduler
        self._msg_scheduler._broker = self


    def forward(self, topic, msg):
        " Send a message on to rootio_telephony "
        logging.debug("fwd %s: %s" % (topic, msg))
        self._station_daemon_stream.send_json([topic, msg])


    def schedule(self, topic, msg):
        logging.debug("schedule",topic,msg)

        if 'msg_id' in msg:
            msg_id = msg.pop('msg_id')

        if 'start_time' in msg:
            if 'window' in msg:
                msg_time = msg['start_time'] - timedelta(seconds=msg['window'])
            else:
                msg_time = msg['start_time']
        else:
            offset = timedelta(seconds=10)
            #needs to be a little bit in the future, so scheduler can run it
            msg_time = datetime.now() + offset

        if 'operation' in msg:
            for case in switch(msg['operation']):
                if case('insert'):
                    self._msg_scheduler.schedule_message(topic, msg, msg_time)
                    break
                if case('update'):
                    self._msg_scheduler.reschedule_message(msg_id, topic, msg, msg_time)
                    break
                if case('delete'):
                    self._msg_scheduler.cancel_message(msg_id)
                    break
        else:
            self._msg_scheduler.schedule_message(topic, msg, msg_time)

    def parse(self, topic, msg_string):
        logging.debug("parse %s: %s" % (topic, msg_string))

        try:
            msg = json.loads(msg_string)
            logging.debug('got json msg %s' % msg)
        except ValueError:
            logging.debug('got string msg %s' % msg_string)
            msg = msg_string
        except TypeError:
            logging.error('could not parse json %s' % msg_string)
            msg = msg_string

        for case in switch(topic):
            if case("scheduler"):
                self.schedule(topic, msg)
                break
            if case("zmq"):
                #startup message, drop it
                break
            if case(): # default
                self.forward(topic, msg)
                break

    def start(self):
        " Run forever. Launch in separate process. "
        logging.debug("broker start")

        #ioloop method
        self._web_pair_stream.on_recv(self.parse)
        self._telephony_stream.on_recv(self.forward)

        self.running = True
        while self.running:
            pass
        ioloop.IOLoop.instance().stop()
        # single threaded method
        #while self.running:
        #    topic, message = self._web_pair.recv_json()
        #    logging.info("recv %s: %s" % (topic, message))
        #    self.parse(topic, message)


    def shutdown(self):
        logging.info("broker shutdown")
        self.running = False
        ioloop.IOLoop.instance().stop()
