
from yapsy.PluginManager import PluginManager
import logging

from flask import Flask
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy

import sys
import requests

logging.basicConfig(level=logging.DEBUG)
GOIP_server = '127.0.0.1' #'172.248.114.178'


app = Flask(__name__)
from rootio.extensions import db #expection symlink of rootio in own directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:NLPog1986@localhost'
db = SQLAlchemy(app)
from rootio.telephony.models import *
from rootio.radio.models import *







def main():
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

if __name__ == "__main__":
	main()
