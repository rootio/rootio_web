import re

class DefaultHandler:

    def __init__(self, server):
        self.__server = server

    def notify_goip_message(self, message, server_info):
        print "in def handler, addr is {0}".format(server_info['addr'])
        message_parts = re.split(':|;| ',message)
        print message_parts
        if message_parts[0] == 'req': #registration request
            self.__server.send_to_goip("reg:{0};status:200".format(message_parts[1]), server_info['sck'], server_info['addr'])
            self.__server.logger.info("[Default Handler] reg:{0};status:200".format(message_parts[1]))  
        else:
            self.__server.send_to_goip("{0} {1} {2}".format(message_parts[0], message_parts[1], 'OK'), server_info['sck'], server_info['addr'])
            self.__server.logger.info("[Default Handler] {0} {1} {2}".format(message_parts[0], message_parts[1], 'OK'))
