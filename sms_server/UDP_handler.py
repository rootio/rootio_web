import SocketServer
from default_handler import DefaultHandler

class UDPHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        data = self.request[0].strip()
        #sck = self.request[1]
        print "{0} said:\n{1}".format(self.client_address[0], data)
        default_handler = DefaultHandler()
        default_handler.handle(data, self) 
