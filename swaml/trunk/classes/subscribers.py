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

import sys, os, string
from services import Services
from message import Message
import rdflib
from rdflib import Graph
from rdflib import URIRef, Literal, Variable, BNode
from rdflib import RDF
from rdflib import plugin
from rdflib.sparql import sparqlGraph, GraphPattern
from namespaces import SWAML, RDF, RDFS, FOAF, GEO


class Subscriber:
    """Subscriber abstraction"""
    
    id = 0
    
    def __init__(self, name, mail):
        """Subscriber constructor"""
        self.__class__.id += 1
        self.setName(name)
        self.setMail(mail)
        services = Services()
        self.setFoaf(services.getFoaf(mail))
        if (self.foaf != None):
            lat, lon = services.getGeoPosition(self.getFoaf())
            self.setGeo(lat, lon)
        else:
            self.setGeo()
        self.mails = []
        
    def getName(self):
        """Get subscriber's name"""
        return self.name
    
    def getMail(self):
        """Get subscriber's mail address"""
        return self.mail 
    
    def getShaMail(self):
        """Get subscriber's sha sum of mail address"""
        return Services().getShaMail(self.mail) 
    
    def getFoaf(self):
        """Get subscriber's FOAF"""
        return self.foaf    
    
    def getSentMails(self):
        """Get the array with subscriber sent mails ids"""
        
        sent = []
        for one in self.mails:
            sent.append(one.getUri())
        
        return sent
    
    def getGeo(self):
        return self.geo
    
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
        
    def setGeo(self, lat=None, lon=None):
        self.geo = [lat, lon]
                
        

class Subscribers:
    """
    Class to abstract the subscribers management
    """
    
    def __init__(self, config):
        """
        Constructor method
        
        @param config: general configuration
        """
        
        self.config = config
        self.subscribers = {}


    def add(self, msg):
        """Add a new subscriber"""
        
        name = msg.getFromName()
        mail = msg.getFromMail()
        
        if (not mail in self.subscribers):
            self.subscribers[mail] = Subscriber(name, mail)
            
        self.subscribers[mail].addMail(msg)


    def __toRDF(self):
        """Dump to RDF file all subscribers"""
        
        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))

        #rdf graph
        store = Graph()
        
        #namespaces
        store.bind('swaml', SWAML)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        
        #subscribers
        subscribers = URIRef(self.config.get('url') + 'subscribers.rdf')
        store.add((subscribers, RDF.type, SWAML["Subscribers"]))

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
                    lat, lon = subscriber.getGeo()
                    if (lat != None and lon != None): 
                        store.bind('geo', GEO)                       
                        geo = BNode()
                        store.add((person, FOAF['based_near'], geo))
                        store.add((geo, GEO['lat'], Literal(lat)))
                        store.add((geo, GEO['long'], Literal(lon)))
                        #TODO: we want something like <foaf:based_near geo:lat="" geo:long="" />
                        
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
        try:
            rdf_file = open(self.config.get('dir') + 'subscribers.rdf', 'w+')
            rdf_file.write(store.serialize(format="pretty-xml"))
            rdf_file.flush()
            rdf_file.close()
        except IOError, detail:
            print 'Error exporting subscribers to RDF: ' + str(detail)
        
    def __toKML(self):
        """
        Public subscribers' geography information,
        if it's available in his foaf files,
        into KML file
        """

        from kml import KML
        kml = KML()
        
        for mail, subscriber in self.subscribers.items():
            lat, lon = subscriber.getGeo()
            if ((lat != None) and (lon != None)): 
                kml.addPlace(lat, lon, name=subscriber.getName())
            
        #and dump to disk
        try:
            kml_file = open(self.config.get('dir') + 'subscribers.kml', 'w+')
            kml.write(kml_file)
            kml_file.flush()
            kml_file.close()
        except IOError, detail:
            print 'Error exporting coordinates to KML: ' + str(detail)
        
        del KML
                                

    def process(self):
        """
        Process subscriber to obtain more semantic information
        """
        
        #first compact list
        self.__compact()
        
        #more ideas?

    def __compact(self):
        """
        Compact mailing list subscribers
        according his foaf information
        """
        
        #diego's idea: look on foaf if the subscriber uses more than one address
        pass
    
    def export(self):
        """
        Export subscriber information into multiple
        formats (RDF and KML)
        """
        
        self.__toRDF()
        self.__toKML()
                           
                                    
del sys, string
