#!/usr/bin/python
#
# SWAML <http://swaml.berlios.de/>
# Semantic Web Archive of Mailing Lists
#
# Copyright (C) 2005 Sergio Fdez
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

import sys, string, getopt
from classes.configuration import Configuration
from classes.publisher import Publisher

class Swaml:

    def args(self, arg, config):
        "Getting params"
        self.config = config
        optlist, arg = getopt.getopt(arg, 'dufh')
        for optpair in optlist:
            opt, value = optpair
            print 'opt: ' + opt + ', value: ' + value
            if (opt=="-d"):
                self.config.setDir(value)
            elif (opt=="-u"):
                self.config.setUrl(value)
            elif (opt=="-f"):
                self.config.setFile(value)
            elif (opt in ("-h", "--help")):
                return """Usage: swaml [OPTION...]

                'swaml' publish an mbox file into a RDF format."""
                                    

    def __init__(self, argv):
        self.config = Configuration()
        args_ret = self.args(argv, self.config)
        if (args_ret == None):
            self.pub = Publisher(self.config)
            self.config.show()
            print str(self.pub.publish()), 'messages procesed'
        else:
            print args_ret


if __name__ == '__main__':
    execute = Swaml(sys.argv[1:])

                                                                            
del sys, string, getopt

