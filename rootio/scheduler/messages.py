from flask import current_app

def start_program(messenger, program, station):
    #send message to the correct station
    topic = "station.%d" % station
    msg = {'program': program}

    messenger.send_multipart([b"%s" % topic, b"%s" % msg])