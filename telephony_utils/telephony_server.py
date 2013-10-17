
from flask import Flask, request, render_template
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import utils

import sys, os
import datetime
import requests

import plivohelper
         
                 
from functools import wraps 

show_host = "+16176424223"

from yapsy.PluginManager import PluginManager
import logging

telephony_server = Flask("ResponseServer")
telephony_server.debug = True


logging.basicConfig(level=logging.DEBUG)
GOIP_server = '127.0.0.1' #'172.248.114.178'
telephony_ip = 'http://176.58.125.166'

telephony_server = Flask("ResponseServer")
telephony_server.debug = True

from rootio.extensions import db #expection symlink of rootio in own directory
telephony_server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NLPog1986@localhost'
db = SQLAlchemy(telephony_server)
from rootio.telephony.models import *
from rootio.radio.models import *


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
                          
@telephony_server.errorhandler(404)
def page_not_found(error):
    """error page"""
    print "404 page not found"
    return 'This URL does not exist', 404

@telephony_server.route('/ringing/', methods=['GET', 'POST'])
def ringing():
    """ringing URL"""
    # Post params- 'to': ringing number, 'request_uuid': request id given at the time of api call
    print "We got a ringing notification"
    return "OK"

@telephony_server.route('/hangup/', methods=['GET', 'POST'])
def hangup():
    """hangup URL"""
    # Post params- 'request_uuid': request id given at the time of api call,
    #               'CallUUID': unique id of call, 'reason': reason of hangup
    print "We got a hangup notification"
    return "OK"                                  
    
@telephony_server.route('/heartbeat/', methods=['GET', 'POST'])
def heartbeat():
    """Call Heartbeat URL"""
    print "We got a call heartbeat notification\n"

    if request.method == 'POST':
        print request.form
    else:
        print request.args      
    return "OK"
                                

def get_caller(func):
    @wraps(func) 
    def inner(*args, **kwargs):         
        print """"#######################################################################
                  #     entering function: ---------------> {0}                         
                  #######################################################################""".format(func.func_name)
        if request.method == 'POST':  
            parameters = dict(request.form.items())
        else:         
            parameters = dict(request.args.items())    
        try:                                                            
            if parameters.get('uuid'):
                print request.method + ", CallUUID: {0}".format(parameters['uuid']) 
            else:
                print request.method + ", CallUUID: {0}".format(parameters['CallUUID']) 
            print parameters  
            kwargs['parameters'] = parameters
        except:
            pass                     
        if func.func_name == 'sms_in':
            m = Message()
            m.message_uuid = parameters.get('uuid')
            m.sendtime = parameters.get('edt')
            m.text = parameters.get('body')
            m.from_phonenumber_id = get_or_create(db.session, PhoneNumber, number = parameters.get('from_number')).id
            m.to_phonenumber_id = get_or_create(db.session, PhoneNumber, number = parameters.get('to_number')).id         
            db.session.add(m)
            db.session.commit()      
        else:
            c = Call()
            c.message_uuid = parameters.get('CallUUID')
            c.start_time = datetime.datetime.now()                                                                     
            c.from_phonenumber_id = get_or_create(db.session, PhoneNumber, number = parameters.get('From')).id
            c.to_phonenumber_id = get_or_create(db.session, PhoneNumber, number = parameters.get('To')).id      
            db.session.add(c)
            db.session.commit()
                                                                 
        return func(*args, **kwargs)
    return inner
        
        
@telephony_server.route('/sms/in', methods=['GET', 'POST'])   
@get_caller
def sms_in(parameters):
    """Receive an sms
    { 'uuid': uuid, 
      'edt': edt, 
      'fr': fr, 
      'to': to, 
      'from_number': from_number, 
      'body': body,
    } 
    """
    print "Parameters =" + str(parameters)    
    print "We received an SMS"      
    print parameters['from_number']
    print show_host
    print parameters['from_number'] == show_host
    print str(parameters['from_number']) == show_host                
    #look at conferenceplay
    if parameters['from_number'] == show_host or parameters['from_number'] == show_host[2:]:     
        answered_url = "http://127.0.0.1:5000/answered/"
        utils.call("sofia/gateway/switch2voip/",parameters['from_number'], answered_url) 
    else:  #obviously the below would only happen with approval of host
        answered_url = "http://127.0.0.1:5000/answered/"
        utils.call("sofia/gateway/switch2voip/",parameters['from_number'], answered_url)       
    return "OK"

@telephony_server.route('/waitmusic/', methods=['GET', 'POST'])
def waitmusic():
    if request.method == 'POST':
        print request.form.items()
    else:
        print request.args.items()
    r = plivohelper.Response()     
    r.addSpeak('Your mama is so fat.')
    r.addSpeak("Your father was a hampster and your mother smelt of elderberries.")
    #r.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-welcome.wav")
    #r.addPlay("/usr/local/freeswitch/sounds/music/8000/suite-espanola-op-47-leyenda.wav")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)    

@telephony_server.route('/hostwait/', methods=['GET', 'POST'])
def hostwait():
    if request.method == 'POST':
        print request.form.items()
    else:
        print request.args.items()
    r = plivohelper.Response()
    r.addPlay(telephony_ip+"/~csik/Hello_Host.mp3")
    r.addPlay(telephony_ip+"/~csik/You_Have_X_Listeners.mp3")
    r.addPlay(telephony_ip+"/~csik/Instructions.mp3")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)

@telephony_server.route('/answered/', methods=['GET', 'POST'])
@get_caller 
def answered(parameters):
    # Post params- 'CallUUID': unique id of call, 'Direction': direction of call,
    #               'To': Number which was called, 'From': calling number,
    #               If Direction is outbound then 2 additional params:
    #               'ALegUUID': Unique Id for first leg,
    #               'ALegRequestUUID': request id given at the time of api call
                                                                          
    r = plivohelper.Response() 
    from_number = parameters.get('From')
    print show_host
    print "Match Host: " + str(str(parameters['From']) == show_host or str(parameters['From']) == show_host[2:])                 
    if str(parameters['From']) == show_host or str(parameters['From']) == show_host[2:] :     
        p = r.addConference("plivo", muted=False, 
                            enterSound="beep:2", exitSound="beep:1",
                            startConferenceOnEnter=True, endConferenceOnExit=True,
                            waitSound="http://127.0.0.1:5000/hostwait/",
                            timeLimit=0, hangupOnStar=True)
    else:
        p = r.addConference("plivo", muted=False, 
                            enterSound="beep:2", exitSound="beep:1",
                            startConferenceOnEnter=True, endConferenceOnExit=False,
                            waitSound="http://127.0.0.1:5000/waitmusic/",
                            timeLimit=0, hangupOnStar=True)
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)


def main():
    plugins()
    return

def plugins():   
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces(["plugins"])
    manager.collectPlugins()

    # Loop round the plugins and print their names.
    for plugin in manager.getAllPlugins():
        plugin.plugin_object.print_name()
    p = manager.getAllPlugins()[0]
    p.plugin_object.activate()


if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        telephony_server.run(host='127.0.0.1', port=5000)

