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

    def __init__(self):
        self.config = {
            #default values
            'dir' : 'archive/',
            'url' : 'http://localhost/',
            'mbox' : 'mbox',
            'format' : 'MM-YY/messageID.rdf'
            }        
        self.antispam = ' AT '


    def getAntiSpam(self):
        return self.antispam;


    def get(self, var):
        if (var in self.config.keys()):
            return self.config[var]


    def set(self, var, value):
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
        for var in self.config.keys():
            print var + ': ' + self.config[var]



