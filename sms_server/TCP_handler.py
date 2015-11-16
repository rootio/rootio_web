import SocketServer

class TCPHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        data = self.request.recv(1024).strip()
        sck = self.request
        sck.sendall("You said {0}".format(data))
        sck.close()
    
    def __run_commands(self):
        pass    
