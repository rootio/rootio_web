import json
from datetime import datetime, timedelta

import isodate
import zmq
from apscheduler.scheduler import Scheduler

from env import read_env
from logme import setup


class MessageScheduler(object):
    def __init__(self, jobstore, url):
        self.socket = zmq.Context().socket(zmq.SUB)
        self.logger = setup(__name__)
        self.logger.debug("Creating MessageScheduler")
        self.logger.debug("id = {}".format(id(self)))
        config = read_env('config.cfg')
        self._scheduler = Scheduler(daemonic=True)
        config_scheduler = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores%s' % jobstore,
                            'apscheduler.jobstores.file.url': url}
        self._scheduler.configure(config_scheduler)

        # Open a publishing socket to the forwarder to pass messages out
        self.broadcast_socket = zmq.Context().socket(zmq.PUB)
        self.broadcast_socket.connect(config['ZMQ_FORWARDER_SUCKS_IN'])

    def start_ap_daemon(self):
        self.logger.info("scheduler start")
        setup("apscheduler.scheduler")
        self._scheduler.start()

    def shutdown(self):
        self.logger.info("scheduler shutdown")
        self._scheduler.shutdown()

    def schedule(self, topic, msg):
        """ Takes incoming message, massages it, and dispatches
            to appropriate function.
        """
        self.logger.debug("schedule received {}: {}".format(topic, msg))

        if 'obj_id' in msg:
            obj_id = msg.pop('obj_id')

        if 'start_time' in msg:
            if 'window' in msg:
                msg_time = msg['start_time'] - timedelta(seconds=msg['window'])
            else:
                msg_time = msg['start_time']
        else:
            offset = timedelta(seconds=10)
            # needs to be a little bit in the future, so scheduler can run it
            msg_time = datetime.now() + offset

        if 'operation' in msg:
            if msg['operation'] == 'insert':
                self.schedule_message(topic, msg, msg_time, obj_id)
            elif msg['operation'] == 'update':
                self.reschedule_message(obj_id, topic, msg, msg_time)
            elif msg['operation'] == 'delete':
                self.cancel_message(obj_id)
            else:
                self.logger.debug("Scheduler has been sent unknown database signal operation.")
        else:
            self.schedule_message(topic, msg, msg_time)

    def send_to_station(self, topic, msg):
        """ Send a message on to rootio_telephony """
        topic = "station.{}.db".format(msg['station_id'])
        # reserialize any datetime elements for zmq -- unpack again at ts
        for key, value in msg.items():
            if isinstance(value, datetime):
                msg[key] = isodate.datetime_isoformat(value)
        msg = json.dumps(msg)
        self.logger.debug("fwd %s: %s" % (topic, msg))
        self.broadcast_socket.send_multipart((topic, msg))

    def schedule_message(self, topic, message, send_at, obj_id):
        self.logger.info("schedule message %s:%s at %s" % (topic, message, send_at))
        # create lambda for scheduler to call at execution time
        # and add it
        message['obj_id'] = obj_id
        try:
            job = self._scheduler.add_date_job(self.send_to_station,
                                               send_at,
                                               args=(topic, message),
                                               name=obj_id)
            self.logger.debug("scheduled job: {}".format(job))
            self.logger.debug("scheduled job_name: {}".format(job.name))
        except ValueError, e:
            self.logger.error(e)

    def cancel_message(self, obj_id):
        self.logger.info("cancel job for scheduled program id %s" % obj_id)
        # apscheduler.unschedule_job works by comparing apscheduler.job objects
        # we don't have a whole job, just the id, obj_id == job.name
        # NOTE: will cancel all messages, may have implications for stations

        try:
            for job in self._scheduler.get_jobs():
                if job.name == obj_id:
                    self._scheduler.unschedule_job(job)
        except Exception, e:
            self.logger.debug("Scheduler cancel_message error {} - {}".format(Exception, e))
            raise KeyError('Message id "%s" is not scheduled in any job store' % obj_id)

    def reschedule_message(self, obj_id, topic, message, send_at):
        self.logger.info("reschedule message_id %s" % obj_id)
        self.cancel_message(obj_id)
        self.schedule_message(topic, message, send_at, obj_id)

    def start_listener(self):
        """ Connects to forwarder_device, runs forever. Launch in
            separate process.
        """

        config = read_env('config.cfg')

        self.logger.debug("Scheduler listener start")
        try:
            self.socket.setsockopt(zmq.SUBSCRIBE, "scheduler")
            self.socket.connect(config['ZMQ_FORWARDER_SPITS_OUT'])
        except Exception, e:
            print e
            print "bringing down port {} device".format(port)
            self.socket.close()

        self.running = True
        self.logger.debug("About to enter listener loop")
        while self.running:
            try:
                message = self.socket.recv_multipart()
                self.logger.info("Scheduler received %s" % (message))
                topic = message[0]
                # Is this the right place to load json?  Should always be json
                msg_string = message[1]
                try:
                    msg = json.loads(msg_string)
                    msg = self.tidy_message(msg)
                    self.logger.debug('got json msg %s' % msg)
                except ValueError:
                    self.logger.debug('got string msg %s' % msg_string)
                    msg = msg_string
                except TypeError:
                    self.logger.error('could not parse json %s' % msg_string)
                    msg = msg_string

                # Topic should only ever be "scheduler"
                self.logger.info("topic = {}, message = {}".format(topic, msg))
                self.schedule(topic, msg)
            except Exception, e:
                self.running = False
                self.logger.debug("Stopping scheduler listener: {} - {}".format(Exception, e))
                self.socket.close()
                self.logger.debug("Stopping scheduler listener -- this should only print once at termination")

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
        self.logger.info("broker shutdown")
        self.running = False
