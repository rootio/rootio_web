import json
import re

class USSDHandler:

    def __init__(self, commands, server):
        self.__ussd_commands = commands
        self.__server = server
        self.__responses = []
        self.__reqid = self.__server.register_for_goip_message(self);

    def process_request(self, server_info):
        if len(self.__ussd_commands) > 0: #we still have commands to run
            cmd = self.__ussd_commands.pop()
            self.__server.logger.info("[USSD Handler] USSD {0} {1} {2}".format(self.__reqid, server_info['password'], cmd))
            self.__server.send_to_goip("USSD {0} {1} {2}".format(self.__reqid, server_info['password'], cmd),server_info['sck'], server_info['addr'])
        else:
            self.__is_exited = True
            server_info['cli'].send(str(self.__responses))
            self.__server.deregister_for_goip_message(self, str(self.__reqid))
            server_info['cli'].close()
   
    def notify_goip_message(self, message, server_info):
        self.__responses.append(message)
        self.__reqid = self.__reqid #+ 1
        self.process_request(server_info)

        
        
