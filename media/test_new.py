from community_media import CommunityMedia
from .. import * 


def __report_answered(self, program_action):
       ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
       ESLConnection.events("plain", "CHANNEL_ANSWER")
       e = ESLConnection.recvEvent()
       if e:
           event_json_string = e.serialize('json')
           event_json = json.loads(event_json_string)
           self.__available_calls[event_json['Caller-Destination-Number']] = event_json
           program_action.notify_call_answered(event_json)

def call(self, program_action, to_number, action, argument, time_limit):
       if to_number in self.__available_calls.keys():
           print "to number is " + to_number
           print self.__available_calls
           program_action.notify_call_answered(self.__available_calls[to_number])
       else:
           call_command = 'originate sofia/gateway/goip/{0} &conference("hey")'.format(to_number)
           print call_command
           t = threading.Thread(target=self.__report_answered, args=(program_action,))
           t.daemon = True
           t.start()
           self.__do_ESL_command(call_command)
 def play(self, file_location, call_UUID):
        play_command = 'uuid_displace {1} start {0}'.format(call_UUID, file_location)
        print 'play command is ' + play_command
        return self.__do_ESL_command(play_command)

    def stop_play(self, call_UUID, content_location):
        stop_play_command = 'uuid_displace {0} stop {1}'.format(call_UUID, content_location)
        print stop_play_command
        return self.__do_ESL_command(stop_play_command)

    def speak(self, phrase, call_UUID):
        speak_command = 'speak stuff'
        return self.__do_ESL_command(speak_command)


    def __report_answered(self, program_action):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "CHANNEL_ANSWER")
        e = ESLConnection.recvEvent()
        if e:
            event_json_string = e.serialize('json')
            event_json = json.loads(event_json_string)
            self.__available_calls[event_json['Caller-Destination-Number']] = event_json
            program_action.notify_call_answered(event_json)

    def request_conference(self, call_UUID, conference_UUID):
        break_command = 'break {0}'.format(conference_UUID)#currently al calls are added to conf. is there need to have a call not in conf?
        return self.__do_ESL_command(break_command)

    def handle_dtmf(self):
        ESLConnection = ESLconnection(ESL_SERVER, ESL_PORT,  ESL_AUTHENTICATION)
        ESLConnection.events("plain", "DTMF")
        while 1:
            e = ESLConnection.recvEvent()
            if e:
                print "Got DTMF event"
                event_json_string = e.serialize('json')
                event_json = json.loads(event_json_string)
                self.__incoming_dtmf_recipients[event_json['Caller-Destination-Number']].notify_incoming_dtmf(event_json)

    def listen_for_media_play_stop(self):
        t = threading.Thread(target=self.handle_media_play_stop, args=())
        t.daemon = True
        t.start()

    def listen_for_incoming_calls(self):
               

def loop_media_items(self
comm = CommunityMedia("2","10")
items = comm.get_media_files()
print items
