from flask.ext.sqlalchemy import SQLAlchemy
from rootio.extensions import db

#telephony_server = Flask("ResponseServer")
#telephony_server.debug = True
#telephony_server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NLPog1986@localhost/rootio'

db = SQLAlchemy('postgresql://postgres:NLPog1986@localhost/rootio')

lines = dq.query.all()

print lines
