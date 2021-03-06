#!/usr/bin/python
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

import string

class Configuration:
    """Class to encapsulate SWAML's configuration"""

    def __init__(self):
        """Constructor method"""
        
        #default values
        self.config = {            
            'dir' : 'archive/',
            'url' : 'http://localhost/swaml/',
            'mbox' : 'mbox',
            'format' : 'YYYY-MMM/messageID.rdf',
            'defaultTo' : 'foo@bar.com'
            }        
        self.antispam = ' AT '


    def getAntiSpam(self):
        """String to fight against the SPAM"""
        
        return self.antispam;


    def get(self, var):
        """Method to get a configuration property"""
        
        if (var in self.config.keys()):
            return self.config[var]

    def set(self, var, value):
        """Method to set a configuration property"""
        
        if (var in self.config.keys()):
            
            #two litle exceptions in var format
            if ((var=='dir' or var=='url') and value[-1]!='/'):
                value += '/'
            if (var=='format' and value[-4:]!='.rdf'):
                value += '.rdf'
                
            self.config[var] = value
            return True
        else:
            return False


    def show(self):
        """[Deprecated] Show al configure options"""
        
        for var in self.config.keys():
            print var + ': ' + self.config[var]



