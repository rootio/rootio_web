
from flask import Flask, request, render_template
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
import utils

import sys
import requests

import plivohelper
import os

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


from flask import Flask, request, render_template
import plivohelper
import os





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
    
@telephony_server.route('/sms/in', methods=['GET', 'POST'])
def sms_in():
    """Receive an sms"""
    # Post params- 'request_uuid': request id given at the time of api call,
    #               'CallUUID': unique id of call, 'reason': reason of hangup   
    if request.method == 'POST':  
        print "POST"
        parameters = dict(request.form.items())
    else:         
        print "GET" 
        parameters = dict(request.args.items())    
    try:
        print "CallUUID: {0}".format(parameters['uuid']) 
        print parameters
    except:
        pass
        
    print "We received an SMS"      
    print parameters['from_number']
    print show_host
    print parameters['from_number'] == show_host
    print str(parameters['from_number']) == show_host   
    answered_url = "http://127.0.0.1:5000/answered/"         
    #look at conferenceplay
    if parameters['from_number'] == show_host:
        utils.call("sofia/gateway/switch2voip/",parameters['from_number'], answered_url)        
    #utils.call("sofia/gateway/switch2voip/",parameters['from_number'])        
    return "OK"

@telephony_server.route('/waitmusic/', methods=['GET', 'POST'])
def waitmusic():
    if request.method == 'POST':
        print request.form.items()
    else:
        print request.args.items()
    r = plivohelper.Response()
    r.addSpeak("Please wait")
    r.addSpeak("Be patient")
    r.addPlay(telephony_ip+"/~csik/duck.mp3")
    r.addPlay("/usr/local/freeswitch/sounds/en/us/callie/ivr/8000/ivr-welcome.wav")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)    

@telephony_server.route('/hostwait/', methods=['GET', 'POST'])
def hostwait():
    if request.method == 'POST':
        print request.form.items()
    else:
        print request.args.items()
    r = plivohelper.Response()
    r.addSpeak("The program will commence in 3 minutes.")
    r.addSpeak("Be patient.")
    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)

@telephony_server.route('/answered/', methods=['GET', 'POST'])
def answered():
    # Post params- 'CallUUID': unique id of call, 'Direction': direction of call,
    #               'To': Number which was called, 'From': calling number,
    #               If Direction is outbound then 2 additional params:
    #               'ALegUUID': Unique Id for first leg,
    #               'ALegRequestUUID': request id given at the time of api call

    if request.method == 'POST':  
        print "POST"
        parameters = dict(request.form.items())
    else:         
        print "GET" 
        parameters = dict(request.args.items())    
    try:
        print "CallUUID: {0}".format(parameters['uuid']) 
        print parameters
    except:
        pass
        
    r = plivohelper.Response() 
    print str(parameters['From'])
    print show_host
    print "Match Host: " + str(str(parameters['From']) == show_host or str(parameters['From']) == show_host[2:])                 
    if str(parameters['From']) == show_host or str(parameters['From']) == show_host[2:] :     
        p = r.addConference("plivo", muted=False, 
                            enterSound="beep:2", exitSound="beep:1",
                            startConferenceOnEnter=True, endConferenceOnExit=True,
                            waitSound="http://127.0.0.1:5000/hostwait/",
                            timeLimit=60, hangupOnStar=True)
    else:
        p = r.addConference("plivo", muted=False, 
                            enterSound="beep:2", exitSound="beep:1",
                            startConferenceOnEnter=True, endConferenceOnExit=False,
                            waitSound="http://127.0.0.1:5000/waitmusic/",
                            timeLimit=60, hangupOnStar=True)
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

