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

"""Mail message abstraction"""

import sys, os, string, sha
import datetime, email, email.Errors
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib import RDF
from services import FoafUtils, Charset
from dateutils import MailDate, FileDate

class Message:
    """Mail message abstraction"""
    
    id = 0
    
    def __init__(self, msg, config, sender=None):
        """Message constructor"""
        self.__class__.id += 1
        self.id = self.__class__.id
        self.config = config
        self.sender = sender
        self.subject = msg['Subject']
        self.messageId = msg['Message-Id']
        self.date = msg['Date']
        self.From = msg['From']
        self.getAddressFrom = msg.getaddr('From')
        try:
            self.to = msg['To']    
        except:
            #some mails have not a 'to' field
            self.to = self.config.get('to')   
            
        try:
            self.inReplyTo = msg['In-Reply-To']    
        except:
            self.inReplyTo = None
            
        self.parent = None
        self.childs = []
            
        self.__calculateId()
        self.nextByDate = None
        self.previousByDate = None
        
        #body after indexing all messages
        self.body = None
        #self.body = msg.fp.read()
        #[(self.body, enconding)] = decode_header(msg.fp.read())
        
    def setBody(self, body):
        self.body = body
        
    def setSender(self, sender):
        """
        Set message's sender
        """
        self.sender = sender
        
    def setParent(self, parent):
        self.parent = parent.getUri()
        
    def addChild(self, child):
        self.childs.append(child.getUri())
        
    def setNextByDate(self, next):
        self.nextByDate = next.getUri()
        
    def setPreviousByDate(self, previous):
        self.previousByDate = previous.getUri()
        
    def getId(self):
        return self.id
    
    def getSwamlId(self):
        return self.swamlId    
    
    def getMessageId(self):
        return self.messageId
        
    def getPath(self):
        """Return the message's index name"""

        #replace vars        
        #FIXME: format permited vars (feature #1355)
        index = self.config.get('format')
        
        #message date
        date = MailDate(self.date)   
             
         #replace vars
        index = index.replace('DD', date.getStringDay()) #day
        index = index.replace('MMMM', date.getLongStringMonth()) #long string month
        index = index.replace('MMM', date.getShortStringMonth()) #short string month
        index = index.replace('MM', date.getStringMonth()) #numeric month
        index = index.replace('YYYY', date.getStringYear()) #year
        index = index.replace('ID', str(self.id)) #swaml id

        #create subdirs
        dirs = index.split('/')[:-1]
        index_dir = ''
        for one_dir in dirs:
            index_dir += one_dir + '/'
            if not (os.path.exists(self.config.get('dir')+index_dir)):
                os.mkdir(self.config.get('dir')+index_dir)
            
        return index
    
    def getUri(self):    
        return self.config.get('url') + self.getPath()
    
    def getSender(self):
        return self.sender
    
    def __parseFrom(self, from_text):
        """Method to parse from field"""
        
        from_parted = from_text.split(' ')
        name = ' '.join(from_parted[:-1])
        mail = from_parted[-1]

        return [name, mail]
    
    def getFromName(self):   
        if(self.From.find('<')!= -1):
            #mail similar than: Name Surmane <name@domain.com>
            from_name = str(self.getAddressFrom[0])
        else:
            #something like: Name Surmane name@domain.com
            from_name, from_mail = self.__parseFrom(self.From)
            
        return Charset().encode(from_name)
            
    def getFromMail(self):   
        if(self.From.find('<')!= -1):
            #mail similar than: Name Surmane <name@domain.com>
            return str(self.getAddressFrom[1])
        else:
            #something like: Name Surmane name@domain.com
            from_name, from_mail = self.__parseFrom(self.From)
            return from_mail             
        
        
    def getTo(self):        
        to = self.to
                
        to = to.replace('@', self.config.getAntiSpam())
        to = to.replace('<', '')
        to = to.replace('>', '')                                     
        
        return to
    
    def getSubject(self):
        return Charset().encode(self.subject)
        
    def getDate(self):
        return self.date
    
    def getInReplyTo(self):
        return self.inReplyTo
    
    def getParent(self):
        return self.parent
    
    def getNextByDate(self):
        return self.nextByDate
        
    def getPreviousByDate(self):
        return self.previousByDate
   
    def getBody(self):
        return self.body
    
    def toRDF(self):
        """
        Print a message into RDF in XML format
        """
        
        #rdf graph
        store = Graph()
        
        #namespaces
        from namespaces import SWAML, SIOC, RDFS, FOAF, DC, DCTERMS
        store.bind('swaml', SWAML)
        store.bind('sioc', SIOC)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        store.bind('dc', DC)
        store.bind('dcterms', DCTERMS)
        
        #message node
        message = URIRef(self.getUri())
        store.add((message, RDF.type, SIOC["Post"]))
        
        try:
                 
            store.add((message, SIOC['id'], Literal(self.getSwamlId())))
            store.add((message, SIOC['link'], URIRef(self.getUri())))  
            store.add((message, SIOC['has_container'],URIRef(self.config.get('url')+'index.rdf')))   
            store.add((message, SIOC["has_creator"], URIRef(self.getSender().getUri())))                    
            store.add((message, SIOC['title'], Literal(self.getSubject()))) 
            store.add((message, DCTERMS['created'], Literal(self.getDate())))  
            
            parent = self.getParent()
            if (parent != None):
                store.add((message, SIOC['reply_of'], URIRef(parent)))  
                
            if (len(self.childs) > 0):
                for child in self.childs:
                    store.add((message, SIOC['has_reply'], URIRef(child)))
                
            previous = self.getPreviousByDate()
            if (previous != None):
                store.add((message, SWAML['previousByDate'], URIRef(previous)))
                
            next = self.getNextByDate()
            if (next != None):
                store.add((message, SWAML['nextByDate'], URIRef(next)))                
                        
            store.add((message, SIOC['content'], Literal(self.getBody())))      
            
        except Exception, detail:
            print 'Error proccesing message ' + str(self.getId()) + ': ' + str(detail) 
        
        #and dump to disk
        try:
            rdf_file = open(self.config.get('dir') + self.getPath(), 'w+')
            rdf_file.write(store.serialize(format="pretty-xml"))
            rdf_file.flush()
            rdf_file.close()        
        except IOError, detail:
            print 'IOError saving message ' + str(self.getId()) + ': ' + str(detail)
            
    def __calculateId(self):
        """
        Calculate SWAML ID

        @todo: obtain a better SWAML ID
        """
        
        #id: hashcode of 'MessageId - Date + ID'
        self.swamlId = sha.new(self.messageId + '-' + self.date + '-swaml-' + str(self.id)).hexdigest()            
        

        


        
