from os import sys, path

activate_this = '/opt/rootio/venvs/rootio_web/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from manage import app as application
# from rootio.app import create_app as application
