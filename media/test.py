import json

media_stop_info = { "Event-Subclass": "sofia::register", "Event-Name": "CUSTOM", "Core-UUID": "d57816be-555f-11e5-9308-df8c1586076c", "FreeSWITCH-Hostname": "precise64", "FreeSWITCH-Switchname": "precise64", "FreeSWITCH-IPv4": "192.168.2.104", "FreeSWITCH-IPv6": "::1", "Event-Date-Local": "2015-09-30 17:03:47", "Event-Date-GMT": "Wed, 30 Sep 2015 17:03:47 GMT", "Event-Date-Timestamp": "1443632627290327", "Event-Calling-File": "sofia_reg.c", "Event-Calling-Function": "sofia_reg_handle_register_token", "Event-Calling-Line-Number": "1927", "Event-Sequence": "4136226", "profile-name": "internal", "from-user": "1002", "from-host": "192.168.2.104", "presence-hosts": "192.168.2.104,192.168.2.104", "contact": "\"Aber Community FM\" <sip:1002@192.168.2.105:5060>", "call-id": "658522070@192.168.2.105", "rpid": "unknown", "status": "Registered(UDP)", "expires": "60", "to-user": "1002", "to-host": "192.168.2.104", "network-ip": "192.168.2.105", "network-port": "5060", "username": "1002", "realm": "192.168.2.104", "user-agent": "dble" }

#media_stop_json = json.loads(media_stop_info)

#print media_stop_info['cow']

cows = ["anna","jess","hink;ey"]
#print cows [jude -7]
print "he is crazy {0}".format("jude")
