import re

class DefaultHandler:

    def handle(self, message, request_handler):
        message_parts = re.split(':|;',message)
        print message_parts
        if message_parts[0] == 'req': #registration request
            request_handler.request[1].sendto("reg:{0};status:200\n".format(message_parts[1]), request_handler.client_address)  
        else:
            request_handler.request[1].sendto("{0} {1} {2}\n".format(message_parts[0], message_parts[1], 'OK'), request_handler.client_address)
