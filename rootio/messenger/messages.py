from decorators import sends_json

@sends_json
def test_message(topic, msg):
    #passthrough for message tester
    return (topic, msg)

@sends_json
def start_program(program, station):
    #send message to the correct station
    topic = "station.%d" % station
    msg = {'program': program}
    return (topic, msg)