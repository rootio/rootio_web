
import logging

def setup(the_name):
    try:
        import logging
        logger = logging.getLogger(the_name)
        logger.setLevel(logging.DEBUG)
    
        # create a file handler
	handler = logging.FileHandler('/home/vagrant/rootio/rootio_web/scheduler/scheduler.log', mode='a')
        handler.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
    
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        ch.setFormatter(formatter)
    
        # add the handlers to the logger
        logger.addHandler(handler)
        logger.addHandler(ch)
        return logger
    except Exception, e:
        logger.error('Failed to open logger', exc_info=True)
        return str(str(Exception) + str(e))

