import atexit
from env import read_env
from broker import MessageBroker
from scheduler import MessageScheduler

if __name__ == "__main__":
    config = read_env('config.cfg')
    
    scheduler = MessageScheduler(config['jobstore'],config['url'])
    broker = MessageBroker(scheduler)
    
    # start scheduler in own thread
    scheduler.start()

    # shut scheduler threads cleanly at exit
    atexit.register(lambda: scheduler.shutdown())

    # start message broker ioloop
    try:
        broker.start()
    except KeyboardInterrupt:
        broker.shutdown()
