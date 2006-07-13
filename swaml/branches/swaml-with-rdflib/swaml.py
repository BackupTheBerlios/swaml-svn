#!/usr/bin/env python2.4
#
# SWAML <http://swaml.berlios.de/>
# Semantic Web Archive of Mailing Lists
#
# Copyright (C) 2005-2006 Sergio Fdez
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


__author__ = 'Sergio Fdez <http://www.wikier.org/>'
__contributors__ = ["Diego Berrueta <http://www.berrueta.net/>",
                    "Jose Emilio Labra <http://www.di.uniovi.es/~labra/>"]
__copyright__ = "Copyright 2005-2006, Sergio Fdez"
__license__ = "GNU General Public License"
__version__ = "0.0.1"


import sys, string, getopt
from classes.configuration import Configuration
from classes.publisher import Publisher

class Swaml:
    """
    Main class of SWAML project
    
    @autor: Sergio Fdez
    @license: GPL
    """

    def args(self, argv, config):
        "Getting params of default input"

        self.config = config

        try:
            opts, args = getopt.getopt(argv, "d:u:m:f:h", ["dir=","url=","mbox=","format=","help"])
        except:
            self.usage()

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
            elif opt in ("-d", "--dir=") and arg:
                self.config.set("dir", arg)
            elif opt in ("-u", "--url=") and arg:
                self.config.set("url", arg)
            elif opt in ("-m", "--mbox=") and arg:
                self.config.set("mbox", arg)
            elif opt in ("-f", "--format=") and arg:
                self.config.set("format", arg)                                
            else:
                self.usage()


    def usage(self):
        """
        Print help to use SWAML
        
        @todo: locate better name for format vars
        """
        
        print """
Usage: swaml.py [OPTION...]
        
'swaml' publish the files of a mailing list into the semantic web.

Options:
   -d DIR, --dir=DIR          : use DIR to publish, 'archive/' by default.
   -u URL, --url=URL          : base URL.
   -m MBOX, --mbox=MBOX       : open MBOX file, by default uses 'mbox'.
   -f FORMAT, --format=FORMAT : path FORMAT to publish messages, the string 'MM-YY/messageID.rdf' uses by default.
                                Some variables you could use:
                                   'MM': month that message sent
                                   'YY'': year that message sent
                                   'ID': message id
   -h, --help                 : print this help message and exit.

Report bugs to: <http://swaml.berlios.de/bugs>
"""
        sys.exit()
        

    def __init__(self, argv):
        """
        main method
        @param argv: values of inline arguments
        """
        
        self.config = Configuration()
        args_ret = self.args(argv, self.config)
        self.pub = Publisher(self.config)
        print str(self.pub.publish()), 'messages procesed'



if __name__ == '__main__':
    execute = Swaml(sys.argv[1:])

                                                                            
del sys, string, getopt

