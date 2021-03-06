# -*- coding: utf8 -*-

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

"""Configuration related code"""

import string
from ConfigParser import ConfigParser

class Configuration:
    """Class to encapsulate SWAML's configuration"""

    def __init__(self):
        """
        Constructor method
        """
        
        #default values
        self.config = { 
            'title' : '',
            'description' : '',
            'host' : '',
            'verbose' : False,         
            'dir' : 'archive/',
            'base' : 'http://localhost/swaml/',
            'mbox' : 'mbox',
            'post' : 'YYYY-MMM/messageID',
            'to' : 'foo@bar.com',
            'kml' : True,
            'search': 'swse',
            'foaf' : True
            }       
             
        self.antispam = ' AT '
        
    def parse(self, argv):
        """
        Getting params of default input
        
        @param argv: arguments values array
        @return: parse ok
        @rtype: boolean
        @todo: process one o more lists
        """
        
        if (len(argv) == 0):
            return False
        else:
            path = argv[0]
            config = ConfigParser()
            
            try:
                config.read(path)
            except:
                print 'Error parsing config file'
                
            section = 'SWAML'    
            
            if (config.has_section(section)):
                for option in config.options(section):
                    if not self.set(option, config.get(section, option)):
                        print 'unknow option in ' + path
                        return False
            
            else:
                print 'No SWAML section founded'
                return False
            
            return True


    def getAntiSpam(self):
        """
        String to fight against the SPAM
        """
        
        return self.antispam;


    def get(self, var):
        """
        Method to get a configuration property
        
        @param var: var key
        """
        
        if (var in self.config.keys()):
            return self.config[var]
        
    def getAgent(self):
        """
        Return the agent URL
        """
        return self.agent

    def set(self, var, value):
        """
        Method to set a configuration property
        
        @param var: var key
        @param value: value var
        """
        
        if (var in self.config.keys()):
            
            #two litle exceptions in var format
            if ((var == 'dir' or var == 'base') and value[-1] != '/'):
                value += '/'
            elif (var == 'kml' or var == 'foaf'):
                if (value.lower() == 'no'):
                    value = False
                else:
                    value = True
                
            self.config[var] = value
            return True
        else:
            return False
        
    def setAgent(self, agent):
        """
        Store the agent's url
        
        @param agent: agent uri
        """
        
        self.agent = agent


    def show(self):
        """
        Show all configure options
        """
        
        for var in self.config.keys():
            print var + ': ' + str(self.config[var])

