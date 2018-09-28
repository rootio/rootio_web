import json
import re
import socket
import threading

from rootio.config import DefaultConfig

from USSD_handler import USSDHandler
from default_handler import DefaultHandler


class SMSServer:

    def __init__(self, logger):
        self.__logger = logger
        self.__port = DefaultConfig.SMS_PORT
        self.__host = DefaultConfig.SMS_SERVER_IP
        self.__goip_listeners = dict()
        self.__backlog = 0
        self.__default_handler = DefaultHandler(self)
        self.__server_info = dict()
        self.__prepare_server_info()
        self.__goip_request_id = 0

    def __prepare_server_info(self):
        for i in range(1, 8, 1):
            self.__server_info[str(i)] = {'password': 'user' + str(i), 'port': DefaultConfig.GOIP_SMS_SERVER_PORT,
                                          'addr': DefaultConfig.GOIP_SMS_SERVER_IP, 'sck': None}

    def run(self):
        t = threading.Thread(target=self.__listen_for_tcp, args=())
        t.daemon = True
        t.start()

        for server_id in self.__server_info:
            thr = threading.Thread(target=self.__listen_to_goip, args=(server_id,))
            thr.daemon = True
            thr.start()

        while True:
            # chill
            pass

    def __listen_for_tcp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.__host, self.__port))
        s.listen(self.__backlog)
        self.__logger.info("Started TCP listener on port {0}".format(self.__port))

        while 1:
            cli, adr = s.accept()
            thrd = threading.Thread(target=self.__handle_tcp_connection, args=(cli,))
            thrd.daemon = True
            thrd.start()

    def __handle_tcp_connection(self, cli):
        data = cli.recv(1024)
        self.__logger.info("Received data from client: {0}".format(data))
        json_data = json.loads(data)
        response = self.__process_request(json_data, cli)
        self.__logger.info("Response sent to client: {0}".format(response))

    def send_to_goip(self, data, sck, addr):
        sck.sendto(data, addr)
        self.__logger.info("Sending command to GoIP: {0}".format(data))

    def __listen_to_goip(self, server_id):
        # handle incoming messages from goip
        self.__server_info[server_id]['sck'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_addr = ('', self.__server_info[server_id]['port'])
        self.__server_info[server_id]['sck'].bind(udp_addr)
        while True:
            data, addr = self.__server_info[server_id]['sck'].recvfrom(1024)
            print "addr is {0}".format(addr)
            self.__logger.info("Received data from GoIP: {0}".format(data))
            self.__server_info[server_id]['addr'] = addr
            self.__handle_goip_message(data, self.__server_info[server_id])

    def register_for_goip_message(self, handler):
        self.__goip_request_id = self.__goip_request_id - 1  # 0 offset
        self.__goip_listeners[str(self.__goip_request_id)] = handler
        self.__logger.info("{0} Registered for goip messages with id {1}".format(handler, self.__goip_request_id))
        return self.__goip_request_id

    def deregister_for_goip_message(self, handler, request_id):
        del self.__goip_listeners[request_id]
        self.__logger.info("{0} Removed for goip messages with id {1}".format(handler, request_id))

    def __handle_goip_message(self, data, server_info):
        # split message
        data_parts = re.split(':|;| ', data)
        # if id in listeners, invoke listener's notify goip_message
        print self.__goip_listeners
        if len(data_parts) >= 1 and data_parts[1] in self.__goip_listeners:
            self.__goip_listeners[data_parts[1]].notify_goip_message(data, server_info)
        else:  # send to default handler
            self.__default_handler.notify_goip_message(data, server_info)

    def __process_request(self, json_data, cli):
        if json_data['transaction_type'] == 'USSD':  # we are trying to do a USSD transaction
            self.__logger.info("Handling USSD transaction: {0}".format(json_data))
            ussd_handler = USSDHandler(json_data['transactions'], self)
            self.__server_info[json_data['line']]['cli'] = cli
            return ussd_handler.process_request(self.__server_info[json_data['line']])
