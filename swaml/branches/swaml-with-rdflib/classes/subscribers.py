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
from message import Message
from rdflib import Graph
from rdflib import URIRef, Literal, Variable, BNode
from rdflib import RDF
from rdflib import plugin
from rdflib.store import Store


class Subscriber:
    """Subscriber abstraction"""
    
    id = 0
    
    def __init__(self, name, mail):
        """Subscriber constructor"""
        self.__class__.id += 1
        self.setName(name)
        self.setMail(mail)
        self.setFoaf(Services().getFoaf(mail))
        self.mails = []
        
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
    
    def getSentMails(self):
        """Get the array with subscriber sent mails ids"""
        
        sent = []
        for one in self.mails:
            sent.append(one.getUri())
        
        return sent
    
    def setName(self, name):
        """Set subscriber's name"""
        if (len(name)>1 and name[0]=='"' and name[-1]=='"'):
            self.name = name[1:-1]
        else:
            self.name = name
    
    def setMail(self, mail):
        """Set subscriber's mail address"""
        self.mail = mail
        
    def setFoaf(self, foaf):
        """Set subscriber's FOAF"""
        self.foaf = foaf     
        
    def addMail(self, new):
        """Add new sent mail"""
        self.mails.append(new) 
                
        

class Subscribers:
    """Class to abstract the subscriber management"""

    def add(self, name, mail, msg):
        """Add a new subscriber"""
        
        if (not mail in self.subscribers):
            self.subscribers[mail] = Subscriber(name, mail)
            
        self.subscribers[mail].addMail(msg)


    def toRDF(self):
        """Dump to RDF file all subscribers"""
        
        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))

        #rdf graph
        store = Graph()
        
        #namespaces
        from namespaces import SWAML, RDFS, FOAF
        store.bind('swaml', SWAML)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        
        #subscribers = URIRef("subscribers.html")
        subscribers = BNode()
        store.add((subscribers, RDF.type, SWAML["Subscribers"]))
        
        #changing default encoding?
        #sys.setdefaultencoding('latin-1')

        #a BNode for each subcriber
        for mail, subscriber in self.subscribers.items():
            #subscriberNode = BNode()
            person = BNode()
            store.add((subscribers, SWAML["subscriber"], person))
            store.add((person, RDF.type, FOAF["Person"]))
            try:
                name = subscriber.getName()
                if (len(name) > 0):
                    store.add((person, FOAF["name"], Literal(name) ))            
                store.add((person, FOAF["mbox_sha1sum"], Literal(subscriber.getShaMail())))
                foafResource = subscriber.getFoaf()
                if (foafResource != None):
                    store.add((person, RDFS["seeAlso"], URIRef(foafResource)))
            except UnicodeDecodeError, detail:
                print 'Error proccesing subscriber ' + subscriber.getName() + ': ' + str(detail)
            
            sentMails = subscriber.getSentMails()
            if (len(sentMails)>0):
                #build rdf:Bag
                mails = BNode()
                store.add((person, SWAML["sentMails"], mails))
                store.add((mails, RDF.type, RDF.Bag))
                for uri in sentMails:
                    store.add((mails, RDF.li, URIRef(uri)))
                    
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
