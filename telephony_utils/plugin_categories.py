from yapsy.IPlugin import IPlugin

class IProgram(IPlugin):
    def print_name(self):
        print "This is a blank program"