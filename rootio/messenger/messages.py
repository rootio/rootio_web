from decorators import sends_json

@sends_json
def test_message(topic, msg):
    #passthrough for message tester
    return (topic, msg)

@sends_json
def schedule_program_start(program_id, station_id, start_time):
    #tells the scheduler to start program_id on station_id at start_time
    topic = "scheduler"
    msg = {'program_id': program_id,
           'station_id': station_id,
           'start_time': start_time}
    return (topic, msg)