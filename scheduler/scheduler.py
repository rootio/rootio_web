
import sys
from apscheduler.scheduler import Scheduler
import zmq
import json
from switch import switch
from logme import setup

# necessary to understand schedule messages
import datetime
#from dateutil.tz import tzlocal
#from datetime import tzinfo
#import psycopg2

import isodate
from env import read_env
logging = setup()

class MessageScheduler(object):
    def __init__(self, jobstore, url):
        config = read_env('config.cfg')
        self._scheduler = Scheduler(daemonic=True)
        config_scheduler = {
                    'apscheduler.jobstores.file.class': 'apscheduler.jobstores%s' % jobstore, 
                    'apscheduler.jobstores.file.url':  url
                 }
        self._scheduler.configure(config_scheduler)

        #Open a publishing socket to the forwarder to pass messages out
        self.broadcast_socket = zmq.Context().socket(zmq.PUB)
        self.broadcast_socket.connect(config['ZMQ_FORWARDER_SUCKS_IN'])

    def start_ap_daemon(self):
        logging.info("scheduler start")
        self._scheduler.start()

    def shutdown(self):
        logging.info("scheduler shutdown")
        self._scheduler.shutdown()

    def schedule(self, topic, msg):
        """ Takes incoming message, massages it, and dispatches to appropriate function.  """
        logging.debug("schedule received {}: {}".format(topic,msg))

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
                    self.schedule_message(topic, msg, msg_time)
                    break
                if case('update'):
                    self.reschedule_message(msg_id, topic, msg, msg_time)
                    break
                if case('delete'):
                    self.cancel_message(msg_id)
                    break
        else:
            self.schedule_message(topic, msg, msg_time)

    def send_to_station(self, topic, msg):
        """ Send a message on to rootio_telephony """
        logging.debug("fwd %s: %s" % (topic, msg))
        self._station_daemon_stream.send_json([topic, msg])

    def schedule_message(self, topic, message, send_at):
        logging.info("schedule message %s:%s at %s" % (topic, message, send_at))
        #create lambda for scheduler to call at execution time
        #and add it
        try:
            job = self._scheduler.add_date_job(self.send_to_station, send_at, args=(topic, message))
            logging.debug("scheduled job_id", job.id)
        except ValueError,e:
            logging.error(e)

    def cancel_message(self, message_id):
        logging.info("cancel message_id %s" % message_id)
        # apscheduler.unschedule_job works by comparing apscheduler.job objects
        # we don't have a whole job, just the id, message_id == job.id
        # so do it manually

        self._scheduler._jobstores_lock.acquire()
        try:
            for alias, jobstore in self._scheduler._jobstores.iteritems():
                for job in list(jobstore.jobs):
                    if job.id == message_id:
                        self._remove_job(job, alias, jobstore)
                    return
        finally:
            self._scheduler._jobstores_lock.release()

        raise KeyError('Message id "%s" is not scheduled in any job store' % message_id)

    def reschedule_message(self, message_id, topic, message, send_at):
        logging.info("reschedule message_id %s" % message_id)
        self.cancel_message(message_id)
        self.schedule_message(topic, message, send_at)

    def start_listener(self):
        " Connects to forwarder_device, runs forever. Launch in separate process. "
        config = read_env('config.cfg')

        logging.debug("Scheduler listener start")
        try:
            self.socket = zmq.Context().socket(zmq.SUB)
            self.socket.setsockopt(zmq.SUBSCRIBE, "scheduler")
            self.socket.connect(config['ZMQ_FORWARDER_SPITS_OUT'])
        except Exception, e:
            print e
            print "bringing down port {} device".format(port)
            self.socket.close()

        self.running = True
	    logging.debug("About to enter listener loop")
        while self.running:
            try:
                message = self.socket.recv_multipart()
                logging.info("Scheduler received %s" % (msg))
		        topic = message[0]
                # Is this the right place to load json?  Should always be jsondat
		        msg_string = message[1]
                try:
                    msg = json.loads(msg_string)
                    msg = tidy_message(msg)
                    logging.debug('got json msg %s' % msg)
                except ValueError:
                    logging.debug('got string msg %s' % msg_string)
                    msg = msg_string
                except TypeError:
                    logging.error('could not parse json %s' % msg_string)
                    msg = msg_string

                # Topic should only ever be "scheduler"
		        logging.info("topic = {}, message = {}".format(topic, msg))
		        self.schedule(topic, msg)
            except Exception, e:
                logging.debug("Stopping scheduler listener: {} - {}".format(Exception, e))
                self.socket.close()
	            logging.debug("Stopping scheduler listener -- this should only print once at termination")
    
    def tidy_message(self, msg)
        """ 
        Tidy message by turning all isoformat date times back into datetimes.
        Could also use somethng like regex here:
        http://my.safaribooksonline.com/book/programming/regular-expressions/9780596802837/4dot-validation-and-formatting/id2983571
        """

        for key, value in msg.items():
            for key, value in j.items():
                try:
                    j[key] = isodate.parse_datetime(value)
                except:
                    pass
        return msg

    def shutdown(self):
        logging.info("broker shutdown")
        self.running = False



