import os
import sys
os.environ['PYTHON_EGG_CACHE'] = '/home/csik/.python-eggs'
os.environ['PYTHONPATH'] = "/home/csik/public_python/rootiocloud/deploy/venv/bin/python:/home/csik/public_python/rootiocloud/rootio"
BASE_DIR= '/home/csik/public_python/rootiocloud/deploy'
sys.path.append('/home/csik/public_python/rootiocloud/')

# activate virtualenv
activate_this = os.path.join(BASE_DIR, "../venv/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
# give wsgi the "application"
from rootio.app import create_app
application = create_app()


