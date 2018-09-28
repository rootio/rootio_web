import socket

from rootio.config import DefaultConfig

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


if __name__ == '__main__':
    """
        This is an example of how to interact with the SMS server
        This script simply executes a series of USSD steps to check for credit on all lines in an 8 SIM GoIP
        In this example, the USSD code for checking credit on this telecom network (Orange Uganda) is *131#"
        """
    for line in range(1, 9):
        talk_to_goip('{{"transaction_type":"USSD", "line":"{0}", "transactions": ["*131#"]}}'.format(line))
