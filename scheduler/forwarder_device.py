import zmq
from env import read_env

from logme import setup

logger = setup(__name__)


def main():
    try:
        import os
        dr = os.path.dirname(os.path.realpath(__file__))
        config = read_env('{}/config.cfg'.format(dr))
    except IOError:
        config = read_env('config.cfg')
    logger.info("Launching forwarder sucking and spitting")
    # Create the sucking socket
    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind(config['ZMQ_FORWARDER_SUCKS_IN'])
        frontend.setsockopt(zmq.SUBSCRIBE, "")  # subscribe to everything
    except Exception, e:
        logger.debug(str(e))
        logger.debug("Bringing down sucking device")

    # Create the spitting socket, create the forwarder
    try:
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind(config['ZMQ_FORWARDER_SPITS_OUT'])

        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        logger.debug(str(e))
        logger.debug("Bringing down spitting device, no forwarder established")
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()


if __name__ == "__main__":
    main()
