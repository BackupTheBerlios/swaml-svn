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
from services import Services
from rdflib import Graph
from rdflib import URIRef, Literal, BNode, Namespace
from rdflib import RDF
from rdflib import plugin
from rdflib.store import Store


class Subscriber:
    """Subscriber abstraction"""
    
    id = 0
    
    def __init__(self, name, mail):
        """Subscriber constructor"""
        self.__class__.id += 1
        self.name = name
        self.mail = mail
        service = Services()
        self.foaf = service.getFoaf(mail)
        
    def getName(self):
        """Get subscriber's name"""
        return self.name
    
    def getMail(self):
        """Get subscriber's mail address"""
        return self.mail 
    
    def getShaMail(self):
        """Get subscriber's sha sum of mail address"""
        return sha.new('mailto:'+self.mail).hexdigest()  
    
    def getFoaf(self):
        """Get subscriber's FOAF"""
        return self.foaf    
    
    def setName(self, name):
        """Set subscriber's name"""
        self.name = name
    
    def setMail(self, mail):
        """Set subscriber's mail address"""
        self.mail = mail
        
    def setFoaf(self, foaf):
        """Set subscriber's FOAF"""
        self.foaf = foaf      
                
        

class Subscribers:
    """Class to abstract the subscriber management"""

    def add(self, name, mail):
        """Add a new subscriber"""
        
        #TODO: clean names like "Roberto C. Riesgo" or "Fernando Toyos Diaz"
        if (not mail in self.subscribers):
            self.subscribers[mail] = Subscriber(name, mail)


    def toRDF(self):
        """Dump to RDF file all subscribers"""
        
        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))

        #rdf graph
        store = Graph()
        
        #namespaces
        swamlNS = 'http://swaml.berlios.de/ns/0.1/'
        store.bind('swaml', swamlNS)
        SWAML = Namespace(swamlNS)
        
        foafNS = 'http://xmlns.com/foaf/0.1/'
        store.bind('foaf', foafNS)
        FOAF = Namespace(foafNS)
        
        #subscribers = URIRef("subscribers.html")
        subscribers = BNode()
        store.add((subscribers, RDF.type, SWAML["subscribers"]))
        
        #changing default encoding?
        #sys.setdefaultencoding('latin-1')

        #a BNode for each subcriber
        for mail, subscriber in self.subscribers.items():
            subscriberNode = BNode()
            store.add((subscribers, SWAML["susbcriber"], subscriberNode))
            person = BNode()
            store.add(( subscriberNode, FOAF["Person"], person ))
            try:
                store.add(( person, FOAF["name"], Literal(subscriber.getName()) ))            
                store.add((person, FOAF["mbox_sha1sum"], Literal(subscriber.getShaMail())))
                #store.add(( person, FOAF["name"], Literal(subscriber.getFoaf()) ))
            except UnicodeDecodeError, detail:
                print 'Error proccesing subscriber ' + subscriber.getName() + ': ' + str(detail)

        #and dump to disk
        rdf_file = open(self.config.get('dir') + 'subscribers.rdf', 'w+')
        rdf_file.write(store.serialize(format="pretty-xml"))
        rdf_file.flush()
        rdf_file.close()
                                

    def __init__(self, config):
        """
        Constructor method
        
        @param config: general configuration"""
        
        self.config = config
        self.subscribers = {}

                                    
del sys, string
