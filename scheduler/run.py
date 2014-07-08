import atexit
import argparse

from env import read_env
from scheduler import MessageScheduler

from  multiprocessing import Process

from logme import setup
logger = setup()

def run():
    config = read_env('config.cfg')
    
    scheduler = MessageScheduler(config['jobstore'],config['url'])
    
    # start APscheduler daemon in own thread
    scheduler.start_ap_daemon()

    # shut scheduler threads cleanly at exit
    atexit.register(lambda: scheduler.shutdown())

    logger.info("About to launch scheduler listener")
    # start listener for new schedule events from anywhere
    try:
        scheduler.start_listener()
    except KeyboardInterrupt:
        scheduler.shutdown()
    except Exception, e:
	   logger.debug("exception in scheculer start_listener():{}".format(e))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RootIO Scheduled Message Broker')
    parser.add_argument('--log', action='store', help='log level', default='debug')
    args = parser.parse_args()

    try:
        run()
    finally:
        pass
