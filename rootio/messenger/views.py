from flask import Blueprint, render_template, request, current_app, Response
from ..decorators import returns_json

from messages import test_message

import json

messenger = Blueprint('messenger', __name__, url_prefix='/messenger')

@messenger.route('/test/', methods=['GET'])
def message_test():
    return render_template('messenger/message_test.html')

@messenger.route('/test_ajax/', methods=['POST'])
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
        test_message(topic, msg)
        return {'status_code':200,'topic':topic,'message':msg}
    except Exception,e:
        import traceback; traceback.print_exc()
        return {'status_code':400, 'errors':str(e)}
