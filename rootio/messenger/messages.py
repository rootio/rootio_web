from decorators import sends_json

@sends_json
def test_message(topic, msg):
    #passthrough for message tester
    return (topic, msg)

@sends_json
def schedule_program(operation,obj_id, program_id, station_id, start_time, updated=False):
    """ Tells the scheduler to start program_id on station_id at start_time
     If operation is 'delete', scheduler will remove existing job
     If operation is 'update', scheduler will remove and re-add job
    """
    topic = "scheduler"
    msg = {'msg_id':obj_id,
	   'operation': operation,
           'program_id': program_id,
           'station_id': station_id,
           'start_time': start_time}
    return (topic, msg)

@sends_json
def station_update_fields(station_id, fields):
    """ Tells the telephony_server to update the client about new station fields """
    topic = "station.%d" % station_id
    msg = {'operation': 'update',
           'fields': fields}
    return (topic, msg)
