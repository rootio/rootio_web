from flask import Flask
from flask import request   
import sys 
import requests


GOIP_server = '127.0.0.1' #'172.248.114.178'


app = Flask(__name__)           

def debug(request):
    s = ""
    print "form data ({0}):".format(len(request.form))
    for arg in request.form.items():
        s += str(arg)
    print s 
    s = ""
    print "arg data ({0}):".format(len(request.args))
    for arg in request.args.items():
        s += str(arg)
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

@app.route("/in", methods=['GET', 'POST'])
def sms_in():  
    """
    Handles incoming messages.
    Currently getting incoming messages from GOIP8, routed to extension 1100 which triggers handle_chat.py
    Expected args: Event-Date-Timestamp (Unix epoch), from, to, from_number, body
    """
    import datetime
    debug(request)
    edt = datetime.datetime.fromtimestamp(int(request.args.get('Event-Date-Timestamp'))/1000000) #.strftime('%Y-%m-%d %H:%M:%S')    
    fr = request.args.get('from')    #This line should look up the station through its from address 
    to = request.args.get('to')    #This will be the same for all related units -- again may make sense to have a representation of sending units
    from_number = request.args.get('from_number')    #look up a number now?  Save a foreign key
    body = request.args.get('body')      
    return str(str(edt)+fr+'->'+to+from_number+body) 
      
if __name__ == "__main__":
    app.run(debug=True)
    r = requests.get('http://'+GOIP_server+'/init_goip')
                                
    
    
