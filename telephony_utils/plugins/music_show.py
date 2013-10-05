import os,sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from plugin_categories import IProgram as Program

class Music_Show(Program):
    def print_name(self):
        print "This is a music show"
    def activate(self):
        super(Music_Show, self).activate()
        print "I've been activated!"
    def deactivate(self):
        super(Music_Show, self).deactivate()
        print "I've been deactivated!"

