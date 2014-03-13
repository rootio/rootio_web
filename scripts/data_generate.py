#dummy data generation script
# to run, start a flask shell with ipython
# > ipython manage.py run
# > %run scripts/data_generate.py

import string
import random

#from config import *
from rootio.user.models import *
from rootio.radio.models import *
from rootio.telephony.models import *



################# User
#u = User()
#u.name = 'csik'
#u.role_code =0
#u.email='csik@media.mit.edu'
#u.password='my secret password'
#db.session.add(u)
#db.session.commit()

################# Phone
pn0 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744800',
				 raw_number='0417744800',
				 )
pn1 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744801',
				 raw_number='0417744801',
				 )
pn2 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744802',
				 raw_number='0417744802',
				 )
pn3 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744803',
				 raw_number='0417744803',
				 )
pn4 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744804',
				 raw_number='0417744804',
				 )
pn5 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744805',
				 raw_number='0417744805',
				 )
pn6 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744806',
				 raw_number='0417744806',
				 )
pn7 = PhoneNumber(carrier='utl',
				 countrycode='256',
				 number='417744807',
				 raw_number='0417744807',
				 )
db.session.add(pn0)
db.session.add(pn1)
db.session.add(pn2)
db.session.add(pn3)
db.session.add(pn4)
db.session.add(pn5)
db.session.add(pn6)
db.session.add(pn7)
db.session.commit()

				

################# Locations
#l.addressline1  l.country       l.id            l.longitude     l.modifieddate  l.name          l.query_class   
#l.addressline2  l.district      l.latitude      l.metadata      l.municipality  l.query   

l = Location(latitude=.12, longitude=30.5, country='Uganda',district='Ibanda',name='Ibanda',municipality='Ibanda')
db.session.add(l)
db.session.commit()

l = Location(latitude=3.712811,longitude=31.783345, country='Uganda',district='Metuli',name='Metuli',municipality='Metuli')
db.session.add(l)
db.session.commit()

l = Location(latitude=2.695784,longitude=32.029277, country='Uganda',district='',name='Alero',municipality='Alero')
db.session.add(l)
db.session.commit()


l = Location(latitude=1.161839,longitude=32.815294, country='Uganda',district='',name='Mugongo',municipality='Mugongo')
db.session.add(l)
db.session.commit()


l = Location(latitude=2.316237,longitude=32.686708, country='Uganda',district='',name='Aber',municipality='Aber')
db.session.add(l)
db.session.commit()


l = Location(latitude=2.634716,longitude=31.997509, country='Uganda',district='Gulu',name='Tam Pi Diki',municipality='Tam Pi Diki')
db.session.add(l)
db.session.commit()



#2.695784, 32.029277 Alero
#1.161839, 32.815294 Mugongo
#2.316237, 32.686708 Aber
#2.634716, 31.997509 Tam Pi Diki (NOT ACCURATE)


################# People
#p.additionalcontact  p.gender             p.languages          p.middlename         p.privacy            p.query_class        
#p.email              p.gender_code        p.lastname           p.phone              p.privacy_code       p.role               
#p.firstname          p.id                 p.metadata           p.phone_id           p.query              p.title              


################# Stations
#s.about                 s.cloud_phone_id        s.init                  s.name                  s.owner_id              s.scheduled_programs    
#s.analytics             s.current_block         s.languages             s.network               s.query                 s.status                
#s.api_key               s.current_program       s.location              s.network_id            s.query_class           s.transmitter_phone     
#s.blocks                s.frequency             s.location_id           s.next_program          s.recent_analytics      s.transmitter_phone_id  
#s.cloud_phone           s.id                    s.metadata              s.owner                 s.recent_telephony      

def id_generator(size=10, chars=string.ascii_letters + string.digits):
    #return base64.urlsafe_b64encode(os.urandom(size))
    return ''.join(random.choice(chars) for x in range(size))

s0 = Station(name='Radio Aber', frequency=88.5, api_key=id_generator())
s1 = Station(name='Pabo FM', frequency=89.0, api_key=id_generator())
s2 = Station(name='Ibanda FM', frequency=102.6, api_key=id_generator())
s3 = Station(name='Metuli RootIO', frequency=102.6, api_key=id_generator())
s4 = Station(name='Alero Community Radio', frequency=102.6, api_key=id_generator())
s5 = Station(name='Mugongo Farm Fresh SACCO', frequency=102.6, api_key=id_generator())
s6 = Station(name='Tom Pi Diki FM', frequency=95.5, api_key=id_generator())
db.session.add(s0)
db.session.add(s1)
db.session.add(s2)
db.session.add(s3)
db.session.add(s4)
db.session.add(s5)
db.session.add(s6)
db.session.commit()

################## Program
#p.duration            p.id                  p.language_id         p.name                p.program_type_id     p.query_class         p.update_recurrence   
#p.episodes            p.language            p.metadata            p.program_type        p.query               p.scheduled_programs  

#pt = ProgramType(name='URN Report', description='Hourly URN update', definition=program_dict)

