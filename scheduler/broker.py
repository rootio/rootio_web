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
        " Set up and bind sockets now happens in the listeners "
        
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
    def process_message(self, msg):
       print "Processing ... %s" % msg

    def listener(self, port_sub):
        # Subscribe to stream from rootio_telephony -- calls, messages, etc. 
        # then relay them to station daemons
       context = zmq.Context()
       socket_sub = context.socket(zmq.SUB)
       socket_sub.connect ("tcp://localhost:%s" % port_sub)
       socket_sub.setsockopt(zmq.SUBSCRIBE, "")
       stream_sub = zmqstream.ZMQStream(socket_sub)
       stream_sub.on_recv(self.process_message)
       print "Connected to publisher with port %s" % port_sub
       ioloop.IOLoop.instance().start()
       print "Worker has stopped processing messages."

    def listener2(self, port_sub="55665"):
        context = zmq.Context()
        socket_sub = context.socket(zmq.PAIR)
        socket_sub.connect("ipc:///tmp/zmq.sock")
        stream_sub = zmqstream.ZMQStream(socket_sub)
        stream_sub.on_recv(self.process_message)
        print "Connected to publisher with port %s" % port_sub
        ioloop.IOLoop.instance().start()
        print "Worker has stopped processing messages."

    def shutdown(self):
        logging.info("broker shutdown")
        self.running = False
        ioloop.IOLoop.instance().stop()
