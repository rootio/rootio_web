import os 
import threading

def do_bundle_purchase():
    os.system('python /home/amour/RootIO_Web_Old/rootio/radiostation/sms_server/bundle_robot.py >> /home/amour/bundle_purchase.log')

def chat(message, args):
    txt = message.getBody()
    if 'bundle' in txt  and 'expired' in txt:
        pid = os.fork()
        if pid == 0: #Am a child :-)
            do_bundle_purchase()
