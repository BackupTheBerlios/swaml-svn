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
import datetime, email, email.Errors, email.Utils
from rdflib import Graph
from rdflib import URIRef, Literal, Variable, BNode
from rdflib import RDF
from services import FoafUtils, Charset

class Message:
    """Mail message abstraction"""
    
    id = 0
    
    def __init__(self, msg, config, sender=None):
        """Message constructor"""
        self.__class__.id += 1
        self.id = self.__class__.id
        self.config = config
        self.sender = sender
        
        try:
            self.subject = Charset().decode(msg['Subject'])
        except:
            self.subject = unicode(msg['Subject'], errors='ignore') 
        
        self.messageId = msg['Message-Id']
        self.date = msg['Date']
        self.From = msg['From']
        self.getAddressFrom = msg.getaddr('From')
        try:
            self.to = msg['To']    
        except:
            #some mails have not a 'to' field
            self.to = self.config.get('defaultTo')    
        
        
        self.body = msg.fp.read()
        #[(self.body, enconding)] = decode_header(msg.fp.read())
        
    def setSender(self, sender):
        """
        Set message's sender
        """
        self.sender = sender
        
    def getId(self):
        return self.id
    
    def getSwamlId(self):
        #TODO: obtain a better SWAML ID
        parted_id = self.messageId.split('.')
        msg_id = parted_id[len(parted_id)-1] + '-' + self.date + '-swaml-' + str(self.id)
        return sha.new(msg_id).hexdigest()        
        
    def getPath(self):
        """Return the message's index name"""

        #replace vars        
        #format permited vars (feature #1355)
        index = self.config.get('format')
	
        #message date
        date = email.Utils.parsedate(self.date)

        #day
        if (date[2] < 10):
            index = index.replace('DD', '0' + str(date[2]))
        else:
            index = index.replace('DD', str(date[2]))

        #long string month
        longMonths = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        index = index.replace('MMMM', longMonths[date[1]-1])

        #short string month
        shortMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        index = index.replace('MMM', shortMonths[date[1]-1])

        #numeric month
        if (date[1] < 10):
            index = index.replace('MM', '0' + str(date[1]))
        else:
            index = index.replace('MM', str(date[1]))

        #year
        index = index.replace('YYYY', str(date[0]))

        #swaml id
        index = index.replace('ID', str(self.id))

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
    
    def parseFrom(self, from_text):
        """Method to parse from field"""
        
        from_parted = from_text.split(' ')
        name = ' '.join(from_parted[:-1])
        mail = from_parted[-1]

        return [unicode(name, errors='ignore'), mail]
    
    def getFromName(self):   
        if(self.From.find('<')!= -1):
            #mail similar than: Name Surmane <name@domain.com>
            from_name = str(self.getAddressFrom[0])
        else:
            #something like: Name Surmane name@domain.com
            from_name, from_mail = self.parseFrom(self.From)
            
        return Charset().decoded(from_name)
            
    def getFromMail(self):   
        if(self.From.find('<')!= -1):
            #mail similar than: Name Surmane <name@domain.com>
            return str(self.getAddressFrom[1])
        else:
            #something like: Name Surmane name@domain.com
            from_name, from_mail = self.parseFrom(self.From)
            return from_mail             
        
        
    def getTo(self):        
        to = self.to
                
        to = to.replace('@', self.config.getAntiSpam())
        to = to.replace('<', '')
        to = to.replace('>', '')                                     
        
        return unicode(to, errors='ignore')
    
    def getSubject(self):
        return self.subject
        
    def getDate(self):
        return self.date
    
    def getInReplyTo(self):
        # self.msg.get('In-Reply-To')
        # self.msg.get('References')
        # None 
        return 'FIXME'
    
    def getBody(self):
        return self.body
    
    def toRDF(self):
        """
        Print a message into RDF in XML format
        """
        
        #rdf graph
        store = Graph()
        
        #namespaces
        from namespaces import SWAML, RDFS, FOAF
        store.bind('swaml', SWAML)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        
        #message node
        message = URIRef(self.getUri())
        store.add((message, RDF.type, SWAML["Message"]))
        
        try:
                        
            #sender
            sender = BNode()
            store.add((message, SWAML["sender"], sender))
            store.add((sender, RDF.type, FOAF["Person"]))   
                      
            name = self.getFromName()
            if (len(name) > 0):
                store.add((sender, FOAF["name"], Literal(name) ))   
                
            mail = self.getFromMail()
            store.add((sender, FOAF["mbox_sha1sum"], Literal(FoafUtils().getShaMail(mail))))
            
            foafResource = self.sender.getFoaf()
            if (foafResource != None):
                store.add((sender, RDFS["seeAlso"], URIRef(foafResource)))
                
            #mail details
            store.add((message, SWAML['id'], Literal(self.getSwamlId())))
            store.add((message, SWAML['to'], Literal(self.getTo())))                         
            store.add((message, SWAML['subject'], Literal(self.getSubject()))) 
            store.add((message, SWAML['date'], Literal(self.getDate())))                
            store.add((message, SWAML['inReplyTo'], Literal(self.getInReplyTo())))                
            store.add((message, SWAML['body'], Literal(self.getBody())))      
            
        except UnicodeDecodeError, detail:
            print 'Error proccesing message ' + str(self.getId()) + ': ' + str(detail) 
        
        #and dump to disk
        try:
            rdf_file = open(self.config.get('dir') + self.getPath(), 'w+')
            rdf_file.write(store.serialize(format="pretty-xml"))
            rdf_file.flush()
            rdf_file.close()        
        except IOError, detail:
            print 'IOError saving message ' + str(self.getId()) + ': ' + str(detail)
        

        


        
