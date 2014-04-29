from flask import Blueprint, render_template, request, current_app, Response
from ..decorators import returns_json

import json

scheduler = Blueprint('scheduler', __name__, url_prefix='/scheduler')

@scheduler.route('/message_test/', methods=['GET'])
def message_test():
    return render_template('scheduler/message_test.html')

@scheduler.route('/message_test_ajax/', methods=['POST'])
@returns_json
def message_test_ajax():
    data_list = json.loads(request.data)
    data = {}
    for d in data_list:
        data[d['name']] = d['value']
    #decode form...

    try:
        msg = data.get('message').__str__()
        topic = data.get('topic').__str__()
        current_app.messenger.send_multipart([b"%s" % topic, b"%s" % msg])
        return {'status_code':200,'topic':topic,'message':msg}
    except Exception,e:
        return {'status_code':400, 'errors':str(e)}

@scheduler.route('/jobs/', methods=['GET'])
def jobs():
    jobs = current_app.scheduler.get_jobs()
    return render_template('scheduler/jobs.html', jobs=jobs)
