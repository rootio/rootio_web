from UDP_handler import UDPHandler
from TCP_handler import TCPHandler
import SocketServer

if __name__ == "__main__":

    HOST, PORT = "192.168.2.104", 1234
    server = SocketServer.UDPServer((HOST,PORT), UDPHandler())
    #server = SocketServer.TCPServer((HOST,PORT), TCPHandler)
    server.serve_forever()    
