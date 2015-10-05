import json


json_string = '{ "Outcall": { "argument":"0774536649", "start_time":"00:00:10", "is_streamed": true, "duration": 120, "warning_time": 110 }, "Jingle": { "argument":"/home/amour/jingle.mp3", "start_time":"00:00:02", "is_streamed": true, "duration": 30 }, "Outcall": { "argument":"0774536649", "start_time":"00:00:10", "is_streamed": true, "duration": 120, "warning_time": 110 }, "Interlude": { "argument":"2", "start_time":"00:02:10", "is_streamed": true, "duration": 120 }, "Outcall": { "argument":"0774536649", "start_time":"00:04:10", "is_streamed": true, "duration": 120, "warning_time": 110 } }'
data = json.loads(json_string)
for j in data:
    print j

