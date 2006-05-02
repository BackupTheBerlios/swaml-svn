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

import sys, os, string, sha
from template import Template

class Subscribers:
    """Class to abstract the subscriber management"""

    def add(self, name, mail):
        """Add a new subscriber"""
        
        if (not name in self.subscribers):
            self.subscribers[name] = mail


    def intoRDF(self):
        """Dump to RDF file all subscribers"""
        
        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))

        self.template = Template()
        
        rdf_file = open(self.config.get('dir') + 'subscribers.rdf', 'w+')
        rdf_file.write(self.template.get('xml_head'))
        rdf_file.write(self.template.get('rdf_head'))
        rdf_file.write(self.template.get('rdf_subscribers_head'))
        rdf_file.flush()

        for name, mail in self.subscribers.items():
            self.tpl = self.template.get('rdf_subscriber')
            self.tpl = self.tpl.replace('{NAME}', name)
            self.tpl = self.tpl.replace('{MAIL}', sha.new('mailto:'+mail).hexdigest())
            self.tpl = self.tpl.replace('{FOAF}', "FIXME")
            rdf_file.write(self.tpl)
            rdf_file.flush()

        rdf_file.write(self.template.get('rdf_subscribers_foot'))
        rdf_file.write(self.template.get('rdf_foot'))
        rdf_file.flush()
        rdf_file.close()
                                

    def __init__(self, config):
        """Constructor method"""
        
        self.config = config
        self.subscribers = {}

                                    
del sys, string
