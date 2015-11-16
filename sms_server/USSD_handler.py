import json
import re

class USSDHandler:

    def __init__(self, request_id, commands, request_handler):
        self.__request_id = request_id
        self.__ussd_requests = json.loads(ussd_requests)
        self.__request_handler = request_handler
        self.__responses = []
        self.__reqid = 1;

    def __run_USSD_commands(self):
        if len(self.__ussd_transaction.commands) > 0: #we still have commands to run
            self.__request_handler.request[0].sendto("USSD {0} {1} {2}\n".format(self.__reqid, self.__ussd_transaction.password, self.__ussd_transaction.commands.pop())
            self.__reqid = self.__reqid + 1
        else:
            self.__request_handler.finalize_session(request_id, responses)
            self.__exit_ussd_session()

    def __exit_ussd_session(self):
        self.__request_handler.request[0].sendto("USSDEXIT {0} {1}\n".format(self.__reqid, self.__ussd_transaction.password))       

    def __handle(self, message, request_handler):
        self.__responses.insert(message)
        self.__run_USSD_commands()
        
        
