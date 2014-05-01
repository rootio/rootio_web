import zmq
from switch import switch
from datetime import datetime, timedelta

# from zmq.eventloop import ioloop, zmqstream
# ioloop.install()

class MessageBroker(object):
    def __init__(self, msg_scheduler):
        " Set up and bind sockets "
        
        # IPC pair socket to rootio_web
        self._web_pair = zmq.Context().socket(zmq.PAIR)
        self._web_pair.bind("ipc:///tmp/zmq.sock")
        #self._web_pair = zmqstream.ZMQStream(self._web_pair)

        # TCP publisher socket to rootio_telephony
        self._telephony_pub = zmq.Context().socket(zmq.PUB)
        self._telephony_pub.bind("tcp://127.0.0.1:5556")
        #self._telephony_pub = zmqstream.ZMQStream(self._telephony_pub)

        #set bidirectional links
        self._msg_scheduler = msg_scheduler
        self._msg_scheduler._broker = self


    def forward(self, topic, msg):
        " Send a message on to rootio_telephony "
        print "fwd %s: %s" % (topic, msg)
        self._telephony_pub.send_json([topic, msg])


    def schedule(self, topic, msg):
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

    def parse(self, topic, msg):
        print "parse %s: %s" % (topic, msg)

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
        print "broker start"

        # ioloop method
        # self._web_pair.on_recv(self.parse)
        self.running = True
        # single threaded method
        while self.running:
            topic, message = self._web_pair.recv_json()
            print "recv %s: %s" % (topic, message)
            self.parse(topic, message)


    def shutdown(self):
        print "broker shutdown"
        self.running = False
        # ioloop.IOLoop.instance().stop()
