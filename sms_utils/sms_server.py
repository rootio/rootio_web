from flask import Flask
from flask import request   
from flask.ext.sqlalchemy import SQLAlchemy 

import datetime
import uuid as uid

import sys 
import requests
import urllib2


GOIP_server = '127.0.0.1' #'172.248.114.178'
telephony_server = '127.0.0.1:5000/sms/in'


app = Flask(__name__)    
from rootio.extensions import db
from config import SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
from rootio.telephony.models import PhoneNumber, Message       

def debug(request): 
    if request.method == 'POST':
        deets = request.form.items() 
        print >> sys.stderr, type(deets)
        deets_method = 'POST'
    else:
        deets = request.args.items() 
        print >> sys.stderr, type(deets)
        deets_method = 'GET'
    s = ""
    #print "({0}) parameters via {1}".format(len(deets)-1, deets_method)
    for deet in deets:
        s += str(deet)
    print s 


@app.route("/", methods=['GET', 'POST'])
def hello():
    debug(request)
    return "Hello World!" 
    
@app.route("/init_goip", methods=['GET', 'POST'])
def init_goip():
    try:
        import send_sms_GOIP
        if not send_sms_GOIP.create_flags(): 
            raise Exception("Wrong machine")
    except:
        print "Unable to init GOIP -- are you sure you called the right machine?"
        return "Unable to init GOIP", 404              
        
@app.route("/out", methods=['GET', 'POST'])
def sms_out():
    """
    Handles outgoing message requests.
    Currently only from GOIP8, should be generalized to any type of sending unit, called by station.  
    Expected args: line, to_number, message
    """   
    try:
        import send_sms_GOIP
    except:
        print "Unable to init GOIP -- are you sure you called the right machine?"
        return "Unable to init GOIP", 404
    debug(request)    
    line = request.args.get('line')
    to_number = request.args.get('to_number')
    message = request.args.get('message')
    if not line or not to_number or not message:
        print "Insufficient number of arguments!"
        return "False"        
    if not send_sms_GOIP.send(line,to_number,message):
        print "Uh Oh, some kind of error in send_sms_GOIP"
        return "False"
    else: 
        return "Sent!"

@app.route("/in/", methods=['GET', 'POST'])
def sms_in():  
    """
    Handles incoming messages.
    Currently getting incoming messages from GOIP8, routed to extension 1100 which triggers handle_chat.py
    Expected args: Event-Date-Timestamp (Unix epoch), from, to, from_number, body
    """                              
    debug(request)
    
    uuid = uid.uuid5(uid.NAMESPACE_DNS, 'rootio.org')
    edt = datetime.datetime.fromtimestamp(int(request.args.get('Event-Date-Timestamp'))/1000000) #.strftime('%Y-%m-%d %H:%M:%S')    
    fr = request.args.get('from')    #This line should look up the station through its from address 
    to = request.args.get('to')    #This will be the same for all related units -- again may make sense to have a representation of sending units
    from_number = request.args.get('from_number')    #look up a number now?  Save a foreign key
    body = request.args.get('body')      
    payload = { 'uuid': uuid, 
                'edt': edt, 
                'fr': fr, 
                'to': to, 
                'from_number': from_number, 
                'body': body,
               }
    r= requests.get('http://127.0.0.1:5000/sms/in',params=payload)    
    print r.text
    return "looks alright " + str(uuid)
    #return str(str(edt)+'\n'+fr+'->'+to+'\n'+from_number+'\n'+body+'\n'+uuid) 
      
if __name__ == "__main__":
    app.run(debug=True)
    r = requests.get('http://'+GOIP_server+'/init_goip')
                                
    
    

