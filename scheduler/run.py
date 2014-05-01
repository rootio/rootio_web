import atexit

from broker import MessageBroker
from scheduler import MessageScheduler

if __name__ == "__main__":
    
    scheduler = MessageScheduler()
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
