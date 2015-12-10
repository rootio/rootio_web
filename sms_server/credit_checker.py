import socket
import datetime

ip = '127.0.0.1'
port = 1230
buffer_size = 1024

def talk_to_goip(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (ip, port)
    s.connect(addr)
    s.send(message)
    data = s.recv(buffer_size)
    s.close()
    print data

if __name__ == '__main__':
    for line in range(1,9):
        talk_to_goip('{{"transaction_type":"USSD", "line":"{0}", "transactions": ["*131#"]}}'.format(line))

