import lxml.html
import requests, base64, urllib, urllib2
import redis
                                                                            
def create_flags():
    #make some (hopefully) thread-safe flags for checking if we're already logged in to GOIP 
    import redis
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set('Glogged_in','False')
    r.set('Gsmskey','False')
    return True

def init():
    """
    Logs in to goip with auth credentials
    """    
    s = requests.Session()
    s.auth=('admin', 'argh')
    goip_page = s.get("http://192.168.8.1/default/en_US/tools.html?type=sms")        
    if not goip_page.status_code==200:
        print "Problem authorizing...."
    
    #Successful log in yields a hidden input field called smskey, pull that out 
    root = lxml.html.fromstring(goip_page.text)
    smskey = root.cssselect("input[name='smskey']")[0].get('value')      
    if len(smskey) < 6:
        print "Unable to parse smskey!"
    else:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.set('Glogged_in','True')  
        r.set('Gsmskey',smskey)    
        

def send(line, to_number, message):
    """
    Expects line, to_number, message.
    """       
    r = redis.StrictRedis(host='localhost', port=6379, db=0) 
    if r.get('Glogged_in') == 'False' or r.get('Gsmskey') == 'False':
        init()                                            
        
    #prepare form data for                                                                                                  
    payload={
            'send'        :'Send',
            'smscontent'  :message,
            'telnum'      :str(to_number),
            'action'      :'SMS',
            'smskey'      :r.get('Gsmskey'),
            'line'        :str(line),  
            }
                                   
    #prepare data for some header elements               
    data = urllib.urlencode(payload)        
    base64string = base64.encodestring('%s:%s' % ('admin', 'argh')).replace('\n', '')
    
    headers = { "Host"	            :   '192.168.8.1',
                "User-Agent"	    :   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:24.0) Gecko/20100101 Firefox/24.0',
                "Accept"	        :   'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' ,
                "Accept-Language"	:   'lg,en-us;q=0.7,en;q=0.3',
                "Content-Type"      :   "application/x-www-form-urlencoded",
                "Content-Length"    :   str(len(data)),
                "Connection"        :   "keep-alive",
                "Referer"           :   "http://192.168.8.1/default/en_US/sms.html",      
                "Accept-Encoding"   :   "gzip, deflate",
                "Authorization"     :   "Basic %s" % base64string,
    }
    #make request to goip                                 
    opener = urllib2.build_opener()
    opener.addheaders = headers.items()                                                                                     
    s = 'http://192.168.8.1/default/en_US/sms_info.html'
    response = opener.open(s,data)
    if response.code != 200:
        print "Error, apparently this request was not made correctly."
    else: 
        return True