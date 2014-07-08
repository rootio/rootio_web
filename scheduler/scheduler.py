
import sys
from apscheduler.scheduler import Scheduler
import zmq
import json
from switch import switch
from logme import setup

# necessary to understand schedule messages
#from dateutil.tz import tzlocal
from datetime import datetime, tzinfo, timedelta
#import psycopg2

import isodate
from env import read_env
logger = setup()


class MessageScheduler(object):
    def __init__(self, jobstore, url):
        logger.debug("Creating MessageScheduler")
        config = read_env('config.cfg')
        self._scheduler = Scheduler(daemonic=True)
        config_scheduler = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores%s' % jobstore,
                            'apscheduler.jobstores.file.url':  url}
        self._scheduler.configure(config_scheduler)

        #Open a publishing socket to the forwarder to pass messages out
        self.broadcast_socket = zmq.Context().socket(zmq.PUB)
        self.broadcast_socket.connect(config['ZMQ_FORWARDER_SUCKS_IN'])

    def start_ap_daemon(self):
        logger.info("scheduler start")
        self._scheduler.start()

    def shutdown(self):
        logger.info("scheduler shutdown")
        self._scheduler.shutdown()

    def schedule(self, topic, msg):
        """ Takes incoming message, massages it, and dispatches
            to appropriate function.
        """
        logger.debug("schedule received {}: {}".format(topic, msg))

        if 'obj_id' in msg:
            obj_id = msg.pop('obj_id')

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
                    self.schedule_message(topic, msg, msg_time, obj_id)
                    break
                if case('update'):
                    self.reschedule_message(obj_id, topic, msg, msg_time)
                    break
                if case('delete'):
                    self.cancel_message(obj_id)
                    break
        else:
            self.schedule_message(topic, msg, msg_time)

    def send_to_station(self, topic, msg):
        """ Send a message on to rootio_telephony """
        logger.debug("fwd %s: %s" % (topic, msg))
        self._station_daemon_stream.send_json([topic, msg])

    def schedule_message(self, topic, message, send_at, obj_id):
        logger.info("schedule message %s:%s at %s" % (topic, message, send_at))
        #create lambda for scheduler to call at execution time
        #and add it
        try:
            job = self._scheduler.add_date_job(self.send_to_station,
                                               send_at,
                                               args=(topic, message),
                                               name=obj_id)
            logger.debug("scheduled job: {}".format(job))
            logger.debug("scheduled job_name: {}".format(job.name))
        except ValueError, e:
            logger.error(e)

    def cancel_message(self, obj_id):
        logger.info("cancel job for scheduled program id %s" % obj_id)
        # apscheduler.unschedule_job works by comparing apscheduler.job objects
        # we don't have a whole job, just the id, obj_id == job.name
        # NOTE: will cancel all messages, may have implications for stations

        try:
            for job in self._scheduler.get_jobs():
                for job in self.get_jobs:
                    if job.name == obj_id:
                        self._remove_job(job)
                    return
        except Exception, e:
            logger.debug("Scheduler cancel_message error {} - {}".format(Exception, e))
            raise KeyError('Message id "%s" is not scheduled in any job store' % obj_id)

    def reschedule_message(self, obj_id, topic, message, send_at):
        logger.info("reschedule message_id %s" % obj_id)
        self.cancel_message(obj_id)
        self.schedule_message(topic, message, send_at, obj_id)

    def start_listener(self):
        """ Connects to forwarder_device, runs forever. Launch in
            separate process.
        """

        config = read_env('config.cfg')

        logger.debug("Scheduler listener start")
        try:
            self.socket = zmq.Context().socket(zmq.SUB)
            self.socket.setsockopt(zmq.SUBSCRIBE, "scheduler")
            self.socket.connect(config['ZMQ_FORWARDER_SPITS_OUT'])
        except Exception, e:
            print e
            print "bringing down port {} device".format(port)
            self.socket.close()

        self.running = True
        logger.debug("About to enter listener loop")
        while self.running:
            try:
                message = self.socket.recv_multipart()
                logger.info("Scheduler received %s" % (message))
                topic = message[0]
                # Is this the right place to load json?  Should always be json
                msg_string = message[1]
                try:
                    msg = json.loads(msg_string)
                    msg = self.tidy_message(msg)
                    logger.debug('got json msg %s' % msg)
                except ValueError:
                    logger.debug('got string msg %s' % msg_string)
                    msg = msg_string
                except TypeError:
                    logger.error('could not parse json %s' % msg_string)
                    msg = msg_string

                # Topic should only ever be "scheduler"
                logger.info("topic = {}, message = {}".format(topic, msg))
                self.schedule(topic, msg)
            except Exception, e:
                self.running = False
                logger.debug("Stopping scheduler listener: {} - {}".format(Exception, e))
                self.socket.close()
                logger.debug("Stopping scheduler listener -- this should only print once at termination")

    def tidy_message(self, msg):
        """
        Tidy message by turning all isoformat date times back into datetimes.
        Could also use somethng like regex here:
        http://my.safaribooksonline.com/book/programming/regular-expressions/9780596802837/4dot-validation-and-formatting/id2983571
        """

        for key, value in msg.items():
            try:
                msg[key] = isodate.parse_datetime(value).replace(tzinfo=None)
            except:
                pass
        return msg

    def shutdown(self):
        logger.info("broker shutdown")
        self.running = False
