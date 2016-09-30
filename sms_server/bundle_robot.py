import socket
import datetime
from rootio_mailer.rootio_mail_message import RootIOMailMessage

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
    return data

if __name__ == '__main__':
    msg = RootIOMailMessage()
    msg.add_to_address('jude19love@gmail.com')
    msg.add_to_address('choowilly@gmail.com')
    msg.set_subject('Bundle Purchase for the GoIPs')
    for line in range(1,9):
        resp = talk_to_goip('{{"transaction_type":"USSD", "line":"{0}", "transactions": ["1", "*134*1*2#"]}}'.format(line))
        msg.append_to_body(resp)
    msg.append_to_body('\nRootIO')
    msg.send_message()

