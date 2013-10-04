"""
Intercepting incoming sms messages in freeswitch, and firing off an http request.
Currently will take:   
Event-Date-Timestamp,from,to,from_number, and body

Currently in /usr/local/freeswitch/scripts/handle_chat.py with a symbolic link from /usr/lib/python2.7/dist-packages/handle_chat.py
Invoked by a python action in the chatplan
"""
import sys
import freeswitch
import requests,json
telephony_server_ip   = "http://176.58.125.166/~csik/p/sms_server/in"   
#telephony_server_port = "80"

def chat(message, args):
    freeswitch.consoleLog("info", "SMS in ------------------------------------------>\n")
    freeswitch.consoleLog("info", message.getBody())  
    EDT =  message.getHeader("Event-Date-Timestamp")
    fr = message.getHeader("from")
    to = message.getHeader("to")
    body = message.getBody()
    from_number = body.split('\n')[0]
    body = body.split('\n')[1]             #this may not be necessary, and may break if there is no associated number
    payload={
                'Event-Date-Timestamp'  :EDT,
                'from'                  :fr,
                'to'                    :to,
                'from_number'           :from_number,
                'body'                  :body,
            }            
    data = json.dumps(payload)         
    r = requests.get(telephony_server_ip, params = payload)
    if not r.status_code==200:
        freeswitch.consoleLog("info","Problem sending....")  
        freeswitch.consoleLog("info", str(r.status_code)+'\n')
        freeswitch.consoleLog("info", str(r.text)+'\n')
        freeswitch.consoleLog("info", str(r.url)+'\n')
             
     
"""
from the freeswitch cli:
2013-10-03 23:23:30.639916 [INFO] switch_cpp.cpp:1275 1000@176.58.125.1662013-10-03 23:23:30.639916 [INFO] switch_cpp.cpp:1275 1100@176.58.125.1662013-10-03 23:23:30.639916 [INFO] switch_cpp.cpp:1275 'Event-Name: MESSAGE
Core-UUID: f56ab67c-2bd4-11e3-80f7-691144afea21
FreeSWITCH-Hostname: plato
FreeSWITCH-Switchname: plato
FreeSWITCH-IPv4: 176.58.125.166
FreeSWITCH-IPv6: 2a01%3A7e00%3A%3Af03c%3A91ff%3Afe69%3Aeb33
Event-Date-Local: 2013-10-03%2023%3A23%3A30
Event-Date-GMT: Thu,%2003%20Oct%202013%2023%3A23%3A30%20GMT
Event-Date-Timestamp: 1380842610639916
Event-Calling-File: sofia_presence.c
Event-Calling-Function: sofia_presence_handle_sip_i_message
Event-Calling-Line-Number: 4537
Event-Sequence: 38978
login: sip%3Amod_sofia%40176.58.125.166%3A5060
proto: sip
to_proto: sip
from: 1000%40176.58.125.166
from_user: 1000
from_host: 176.58.125.166
to_user: 1100
to_host: 176.58.125.166
from_sip_ip: 172.248.114.178
from_sip_port: 5060
to: 1100%40176.58.125.166
subject: SIMPLE%20MESSAGE
context: public
type: text/plain
from_full: %22sim1%22%20%3Csip%3A1000%40176.58.125.166%3E%3Btag%3D91807839
sip_profile: internal
dest_proto: sip
max_forwards: 70
Content-Length: 23

+16176424223
Hjdjdjrjr
'2013-10-03 23:23:30.639916 [INFO] switch_cpp.cpp:1275 _________________________________________
2013-10-03 23:23:30.639916 [INFO] switch_cpp.cpp:1275 +16176424223
Hjdjdjrjr


"""