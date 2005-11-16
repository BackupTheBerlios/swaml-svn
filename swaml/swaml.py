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


__author__ = 'Sergio Fdez <wikier@asturlinux.org>'
__version__ = "0.0.1"


import sys, string, getopt
from classes.configuration import Configuration
from classes.publisher import Publisher

class Swaml:

    def args(self, argv, config):
        "Getting params"

        self.config = config

        try:
            opts, args = getopt.getopt(argv, "d:u:f:h", ["dir=","url=","file=","help"])
        except:
            self.usage()

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
            elif opt in ("-d", "--dir=") and arg:
                self.config.set("dir", arg)
            elif opt in ("-u", "--url=") and arg:
                self.config.set("url", arg)
            elif opt in ("-f", "--file=") and arg:
                self.config.set("file", arg)
            else:
                self.usage()


    def usage(self):
        print """Usage: python swaml.py [OPTION...]
        
'swaml' publish a mbox file into semantic web

Options:
   -d DIR, --dir=DIR    : use DIR to publish, \'archive/\' by default
   -u URL, --url=URL    : base URL
   -f FILE, --file=FILE : open mbox FILE, by default uses \'mbox'\ file
   -h, --help           : show this help message and exit

Report bugs to: <http://swaml.berlios.de/bugs>
""" 
        sys.exit()
        

    def __init__(self, argv):
        self.config = Configuration()
        args_ret = self.args(argv, self.config)
        self.pub = Publisher(self.config)
        print str(self.pub.publish()), 'messages procesed'



if __name__ == '__main__':
    execute = Swaml(sys.argv[1:])

                                                                            
del sys, string, getopt

