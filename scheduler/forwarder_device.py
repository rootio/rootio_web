import zmq

def main():

    try:
        context = zmq.Context(1)
        # Socket facing clients
        frontend = context.socket(zmq.SUB)
        frontend.bind("tcp://127.0.0.1:55777")
        
        frontend.setsockopt(zmq.SUBSCRIBE, "")
    except Exception, e:
        print e
        print "bringing down 55666 device"
    try:    
        # Socket facing services
        backend = context.socket(zmq.PUB)
        backend.bind("tcp://127.0.0.1:55778")

        zmq.device(zmq.FORWARDER, frontend, backend)
    except Exception, e:
        print e
        print "bringing down 55665 device"
    finally:
        pass
        frontend.close()
        backend.close()
        context.term()

if __name__ == "__main__":
    main()

