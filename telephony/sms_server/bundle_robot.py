import socket

from rootio.config import DefaultConfig
from rootio_mailer.rootio_mail_message import RootIOMailMessage

ip = DefaultConfig.SMS_SERVER_IP
port = DefaultConfig.SMS_SERVER_PORT
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
    """
    This is an example of how to interact with the SMS server
    This script simply executes a series of USSD steps to purchase a voice bundle for all lines in a GoIP
    In this example, one dials *134*1*2#, and get a menu from which they select '1' (Orange Telecom, Uganda)"
    """

    msg = RootIOMailMessage()
    msg.add_to_address('jude19love@gmail.com')
    msg.set_subject('Bundle Purchase for the GoIPs')
    for line in range(1, 9):
        resp = talk_to_goip(
            '{{"transaction_type":"USSD", "line":"{0}", "transactions": ["1", "*134*1*2#"]}}'.format(line))
        msg.append_to_body(resp)
    msg.append_to_body('\nRootIO')
    msg.send_message()
