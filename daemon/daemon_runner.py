#!/usr/bin/python
from daemoner import Daemon
import sys, time

class DaemonRunner(Daemon):
    
    def run(self):
        while True:
            time.sleep(6)
            print "sleeping for 6 seconds"


if __name__ == "__main__":
    daemon = DaemonRunner("/tmp/daemonrunner.pid")
    if(len(sys.argv) >= 2):
        if sys.argv[1] == "start":
            daemon.start()
        elif sys.argv[1] == "stop":
            daemon.stop()
        elif sys.argv[1] == "restart":
            daemon.restart()
        else:
            print "Uknown option. specify one of start|stop|restart"
         
