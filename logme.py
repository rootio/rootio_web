
import logging

def setup():
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
    
        # create a file handler
        handler = logging.FileHandler('logs/program.log', mode='a')
        handler.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
    
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

