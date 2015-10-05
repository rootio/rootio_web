import os
import sys
import logging

#print os.environ['PYTHONPATH']

logging.basicConfig(filename='/var/log/rootio/test.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

calls = ["0987555","09234902934","2342342342"]

gateways = {"yter":"123123123","sat":"9898989"}

print calls

print gateways

print "Gateways is {0}".format(str(gateways))
logging.info("these are the gateways {0}".format(gateways))
