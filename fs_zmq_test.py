# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="HP Envy"
__date__ ="$Dec 20, 2014 2:07:37 PM$"

import zmq
 

if __name__ == "__main__":
    print "Hello World"
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://192.168.2.103:5556")
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
 
    for count in range (100):
        string = subscriber.recv()
        print string
