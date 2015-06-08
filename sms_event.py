from ESL import *
    
con = ESLconnection("127.0.0.1", "8021", "ClueCon")
event = ESLevent("CUSTOM", "SMS::SEND_MESSAGE")
event.addHeader("to", "1003@192.168.2.104")
event.addHeader("from", "1000@192.168.2.104")
event.addHeader("dest_proto", "sip")
event.addBody("0794451574\nmessage contents")
con.sendEvent(event)
