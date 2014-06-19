
import sys
from apscheduler.scheduler import Scheduler
import zmq
import logging

class MessageScheduler(object):
    def __init__(self, jobstore, url):
        self._scheduler = Scheduler(daemonic=True)

        config = {'apscheduler.jobstores.file.class': 'apscheduler.jobstores%s' % jobstore,
                   'apscheduler.jobstores.file.url':  url}      
        self._scheduler.configure(config)

    def start_ap_daemon(self):
        logging.info("scheduler start")
        self._scheduler.start()

    def shutdown(self):
        logging.info("scheduler shutdown")
        self._scheduler.shutdown()

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

    def schedule_message(self, topic, message, send_at):
        logging.info("schedule message %s:%s at %s" % (topic, message, send_at))

        #create lambda for scheduler to call at execution time

        #and add it
        try:
            job = self._scheduler.add_date_job(self._broker.forward, send_at, args=(topic, message))
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

    def start_listener(self, port = "55778"):
        " Connects to forwarder_device, runs forever. Launch in separate process. "

        logging.debug("Scheduler listener start")
        try:
            self.socket = zmq.Context().socket(zmq.SUB)
            self.socket.setsockopt(zmq.SUBSCRIBE, "scheduler")
            self.socket.connect ("tcp://localhost:%s" % port)
        except Exception, e:
            print e
            print "bringing down port {} device".format(port)
            self.socket.close()

        self.running = True
	logging.debug("About to enter listener loop")
        while self.running:
            try:
                msg = self.socket.recv()
                logging.info("Scheduler received %s" % (msg ))
		#self.schedule(topic, message)
            except Exception, e:
                logging.debug("Stopping scheduler listener")
        self.socket.close()
	logging.debug("Stopping scheduler listener")

    def shutdown(self):
        logging.info("broker shutdown")
        self.running = False



