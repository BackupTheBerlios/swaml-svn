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

"""Subscribers management"""

import sys, os, string
from message import Message
from foaf import FOAFS
import rdflib
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib import RDF
from rdflib import Namespace
from namespaces import SWAML, SIOC, RDF, RDFS, FOAF, GEO


class Subscriber:
    """
    Subscriber abstraction
    """
    
    id = 0
    
    def __init__(self, name, mail, config):
        """
        Subscriber constructor
        
        @param name: name
        @param mail: mail address
        @param config: config params
        """
        
        self.__class__.id += 1
        self.id = self.__class__.id
        self.setName(name)
        self.setMail(mail)
        self.foaf = None
        self.geo = [None, None]
        self.pic = None
        self.mails = []
        self.config = config
        
    def getName(self):
        """
        Get subscriber's name
        
        @return: name
        """
        
        return self.name
    
    def getMail(self):
        """
        Get subscriber's mail address
        
        @return: mail
        """
        
        return self.mail 
    
    def getShaMail(self):
        """
        Get subscriber's sha sum of mail address
        
        @return: sha1mail
        """
        
        return FOAFS().getShaMail(self.mail) 
    
    def getFoaf(self):
        """
        Get subscriber's FOAF
        
        @return: foaf url
        """
        
        return self.foaf    
    
    def getSentMails(self):
        """
        Get the array with subscriber sent mails ids
        
        @return: sent mails list
        """
           
        sent = []
        for one in self.mails:
            sent.append(one.getUri())
        
        return sent
    
    def getGeo(self):
        """
        Obtain geo coordinates
        
        @return: coordinates tuple
        """
        
        return self.geo
    
    def getPic(self):
        """
        Return the uri of his picture
        
        @return: picture url
        """
        
        return self.pic
    
    def getId(self):
        """
        Return subscriber numeric id
        
        @return: id
        """
        
        return self.id
    
    def getStringId(self):
        """
        Return string id
        
        @return: string id
        """
        
        return 's' + str(self.getId())
    
    def getUri(self):
        """
        Return the subscriber's URI
        
        @return: subscriber uri
        """
        
        return self.config.get('url') + 'subscribers.rdf#' + self.getStringId()
    
    def setName(self, name):
        """
        Set subscriber's name
        
        @param name: name
        """
        
        if (len(name)>1 and name[0]=='"' and name[-1]=='"'):
            self.name = name[1:-1]
        else:
            self.name = name
    
    def setMail(self, mail):
        """
        Set subscriber's mail address
        
        @param mail: mail address
        """
        
        self.mail = mail
        
    def setFoaf(self, foaf):
        """
        Set subscriber's FOAF
        
        @param foaf: foaf url
        """
        
        self.foaf = foaf     
        
    def addMail(self, new):
        """
        Add new sent mail
        
        @param new: newmail address
        """
        
        self.mails.append(new) 
        
    def setGeo(self, lat, lon):
        """
        Set coordinates
        
        @param lat: latitude
        @param lon: longitude
        """
        
        self.geo = [lat, lon]
        
    def setPic(self, uri):
        """
        Set subscriber picture
        
        @param uri: picture url
        """
        
        self.pic = uri
                
        

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
        self.baseUri = self.config.get('url') + 'subscribers.rdf'
        self.subscribers = {}


    def add(self, msg):
        """
        Add a new subscriber
        
        @param msg: new message
        """
        
        name = msg.getFromName()
        mail = msg.getFromMail()
        
        if (not mail in self.subscribers):
            self.subscribers[mail] = Subscriber(name, mail, self.config)
            
        self.subscribers[mail].addMail(msg)
        
    def get(self, mail):
        """
        Get subscriber
        
        @param mail: subscriber's mail address
        """
        
        if (mail in self.subscribers):
            return self.subscribers[mail]
        else:
            return None

    def __toRDF(self):
        """
        Dump to RDF file all subscribers
        """
        
        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))

        #rdf graph
        store = Graph()
        
        #namespaces
        store.bind('swaml', SWAML)
        store.bind('sioc', SIOC)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        
        count = 0

        #a Node for each subcriber
        for mail, subscriber in self.subscribers.items():
            count += 1
            
            person = URIRef(self.baseUri + '#' + subscriber.getStringId())
            store.add((person, RDF.type, SIOC['User']))
            
            try:
                name = subscriber.getName()
                if (len(name) > 0):
                    store.add((person, SIOC['name'], Literal(name) ))            
                store.add((person, SIOC['email_sha1sum'], Literal(subscriber.getShaMail())))
                
                if (self.config.get('foaf')):
                    foafResource = subscriber.getFoaf()
                    if (foafResource != None):
                        store.add((person, RDFS['seeAlso'], URIRef(foafResource)))
                        
                        #coordinates
                        lat, lon = subscriber.getGeo()
                        if (lat != None and lon != None): 
                            store.bind('geo', GEO)                       
                            geo = BNode()
                            store.add((person, FOAF['based_near'], geo))
                            store.add((geo, RDF.type, GEO['Point']))		
                            store.add((geo, GEO['lat'], Literal(lat)))
                            store.add((geo, GEO['long'], Literal(lon)))
                            
                        #depiction
                        pic = subscriber.getPic()
                        if (pic != None):
                            store.add((person, SIOC['avatar'], URIRef(pic)))
                        
            except UnicodeDecodeError, detail:
                print 'Error proccesing subscriber ' + subscriber.getName() + ': ' + str(detail)
            
            sentMails = subscriber.getSentMails()
            if (len(sentMails)>0):
                for uri in sentMails:
                    store.add((person, SIOC['creator_of'], URIRef(uri)))
                    
        #and dump to disk
        try:
            rdf_file = open(self.config.get('dir') + 'subscribers.rdf', 'w+')
            store.serialize(destination=rdf_file, format="pretty-xml")
            rdf_file.flush()
            rdf_file.close()
            print count, 'subscribers exported in RDF'
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
        
        count = 0
        
        for mail, subscriber in self.subscribers.items():
            lat, lon = subscriber.getGeo()
            pic = subscriber.getPic()
            if ((lat != None) and (lon != None)): 
                count += 1
                kml.addPlace(lat, lon, name=subscriber.getName(), description=pic)
                
            
        #and dump to disk
        try:
            kml_file = open(self.config.get('dir') + 'subscribers.kml', 'w+')
            kml.write(kml_file)
            kml_file.flush()
            kml_file.close()
            print count, 'subcribers\' coordinates exported in KML'
        except IOError, detail:
            print 'Error exporting coordinates to KML: ' + str(detail)
        
        del KML
                                

    def process(self):
        """
        Process subscribers to obtain more semantic information
        """
        
        foafserv = FOAFS()
        
        self.foafEnriched = 0
        
        for mail, subscriber in self.subscribers.items():
            self.__copileFoafInfo(subscriber, foafserv) #get foaf information
            self.__compact(subscriber, foafserv) #compact subscribers lis
            #more ideas?
            
        print self.foafEnriched, 'subscribers enriched using FOAF'

    def __copileFoafInfo(self, subscriber, foafserv):
        """
        Compile subscribers' information from his FOAFs
        
        @param subscriber: subscriber reference
        @param foafserv: FOAF service reference
        """
        
        mail = subscriber.getMail()
        foaf = foafserv.getFoaf(mail)
        if (foaf != None):
            subscriber.setFoaf(foaf)
            self.foafEnriched += 1
            
            #coordinates
            lat, lon = foafserv.getGeoPosition(foaf, foafserv.getShaMail(mail))
            if (lat != None and lon != None):
                subscriber.setGeo(lat, lon)
                
            pic = foafserv.getPic(foaf, foafserv.getShaMail(mail))
            if (pic != None):
                subscriber.setPic(pic)
                
                

    def __compact(self, subscriber, foafserv):
        """
        Compact mailing list subscribers
        according his foaf information
        
        @param subscriber: subscriber reference
        @param foafserv: FOAF service reference
        """
        
        #diego's idea: look on foaf if the subscriber uses more than one address
        pass
    
    def export(self):
        """
        Export subscribers information into multiple
        formats (RDF and KML)
        """
        
        self.__toRDF()
        
        if (self.config.get('kml')):
            self.__toKML()
            
    def getSubscribersUris(self):
        """
        Get a list of subscribers' URIs
        
        @return: subscribers uris
        """
        
        uris = []
        
        for mail, subscriber in self.subscribers.items():
            uris.append(subscriber.getUri())
            
        return uris
                           
                                    
del sys, string
