#!/usr/bin/python
# -*- coding: utf8 -*-
#
# SWAML <http://swaml.berlios.de/>
# Semantic Web Archive of Mailing Lists
#
# Copyright (C) 2005-2008 Sergio Fernández
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

"""Wizard to create config files for SWAML"""

import sys, os, string
from swaml.ui.ui import ConsoleUI
from swaml.common.configuration import Configuration
import ConfigParser

class ConfigWizard(ConsoleUI):
    """
    SWAML's config wizard
    
    @author: Sergio Fdez
    @license: GPL
    """
    
    def requestData(self):
        """
        Queries the user a new configuration
        """
        
        self.config = Configuration()
        
        print 'Write your configuration options:'
        print '(default value goes between [...])'
        
        for var in self.config.config.keys():
            defaultValue = str(self.config.config[var])
            value = raw_input('\t - ' + var + '[' + defaultValue + ']: ')
            if (len(value) > 0):
                self.config.set(var, value)
    
    def printData(self):
        """
        Dump on hard disk the configuration
        """
        
        ini = ConfigParser.ConfigParser()
        
        ini.add_section(self.section)
        
        for var in self.config.config.keys():
            ini.set(self.section, var, str(self.config.config[var]))
                     
        try:
            file = open(self.output, 'w+')
            ini.write(file)
            file.flush()
            file.close()
            print 'new config file created in', self.output, 'with chosen parameters'
        except IOError, detail:
            print 'Error exporting coordinates config file: ' + str(detail)
    
    def wizard(self):
        """
        Executes all the wizard functions
        """
        
        self.requestData()
        self.printData()
        
    def __init__(self, argv):
        """
        main method
        
        @param argv: values of inline arguments
        """       
        
        ConsoleUI.__init__(self, 'configWizard')
        
        self.section = 'SWAML'
        
        for arg in argv:
            if arg == "-h" or arg == "--help":
                self.usage()
                
        if (len(argv)>=1):
            self.output = argv[0]
            self.wizard()
        else:
            self.usage()


if __name__ == '__main__':
    try:
        ConfigWizard(sys.argv[1:])
    except KeyboardInterrupt:
        print 'Received Ctrl+C or another break signal. Exiting...'

