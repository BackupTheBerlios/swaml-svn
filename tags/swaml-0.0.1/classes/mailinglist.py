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

import sys, os, mailbox, rfc822, string, email, email.Errors, datetime, sha
from mbox import Mbox
from subscribers import Subscribers
from message import Message
from index import Index
from rdflib import Graph, URIRef, Literal, BNode, RDF
import datetime
from dateutils import FileDate

class MailingList:
    
    def __init__(self, config, lang=None):
        """
        Constructor method
        """
        
        self.config = config
        self.lang = lang
        self.subscribers = Subscribers(config)
        self.index = Index(self.config)
        
    def __createDir(self):
        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))
        
    def __parse(self):
        """
        Parse mailingg list and load all
        indexes into memory
        """
        
        previous = None
        
        mbox = Mbox(self.config.get('mbox'))
        messages = 0
        message = mbox.nextMessage()
        
        while(message != None):
            #fisrt load message
            messages += 1
            msg = Message(message, self.config)
            
            #index it
            self.index.add(msg)
            self.subscribers.add(msg)
            subscriber = self.subscribers.get(msg.getFromMail())
            msg.setSender(subscriber)
            
            #parent message (refactor)
            inReplyTo = msg.getInReplyTo()
            if (inReplyTo != None):
                parent = self.index.get(inReplyTo)
                if (parent != None):
                    msg.setParent(parent) #link child with parent
                    parent.addChild(msg) #and parent with child
                    
            #and previous and next by date
            if (previous != None):
                previous.setNextByDate(msg)
                msg.setPreviousByDate(previous)
            
            previous = msg
            
            #and continue with next message
            message = mbox.nextMessage()

        self.messages = messages
    
    def publish(self):
        """
        Publish the messages
        """
        
        self.__createDir()
        
        #fisrt lap
        self.__parse()
        
        #and second lap
        mbox = Mbox(self.config.get('mbox'))
        messages = 0

        message = mbox.nextMessage()
        
        try: 
            
            while(message != None):
                messages += 1
                id = message['Message-Id']
                msg = self.index.getMessage(messages)
                
                if (msg != None and msg.getMessageId() == id):
                    msg.setBody('FIXME')
                    msg.toRDF()
                    #msg.toHTML()
                    #self.index.delete(id)
                else:
                    print 'Someone was wrong with message ' + str(messages) + ' with ID ' + id + ' ('+msg.getMessageId()+')'

                message = mbox.nextMessage()
                
            self.__toRDF()
    
            self.subscribers.process()
            self.subscribers.export()
            
        except Exception, detail:
            print str(detail)
            
        
        if (self.messages != messages):
            print 'Something was wrong: ' + str(self.messages) + ' parsed, but ' + str(messages) + ' processed'

        return messages
    
    def __toRDF(self):
        """Dump mailing list to RDF file"""

        #rdf graph
        store = Graph()
        
        #namespaces
        from namespaces import SWAML, SIOC, RDFS, FOAF, DC, MVCB
        store.bind('swaml', SWAML)
        store.bind('sioc', SIOC)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        store.bind('dc', DC)
        store.bind('mvcb', MVCB)

        #root node
        list = URIRef(self.config.get('url')+'index.rdf')
        store.add((list, RDF.type, SIOC['Forum']))

        #list information
        #store.add((list, DC['title'], Literal(u'FIXME')))
        #store.add((list, DC['description'], Literal(u'RDF files of a mailing list')))
        store.add((list, DC['date'], Literal(FileDate(self.config.get('mbox')).getStringFormat())))
        store.add((list, MVCB['generatorAgent'], URIRef(self.config.getAgent())))
        store.add((list, MVCB['errorReportsTo'], URIRef('http://swaml.berlios.de/bugs')))
        if (self.lang != None):
            store.add((list, DC['language'], Literal(self.lang)))

        #subscribers
        subscribers = self.subscribers.getSubscribersUris()
        for uri in subscribers:
            store.add((list, SIOC['has_subscriber'], URIRef(uri)))
                  
        #and all messages uris
        uris = self.index.getMessagesUri()                        
        for uri in uris:
            store.add((list, SIOC['container_of'], URIRef(uri)))
                    
        #and dump to disk
        try:
            rdf_file = open(self.config.get('dir')+'index.rdf', 'w+')
            rdf_file.write(store.serialize(format="pretty-xml"))
            rdf_file.flush()
            rdf_file.close()
        except IOError, detail:
            print 'Error exporting mialing list to RDF: ' + str(detail)    
    

