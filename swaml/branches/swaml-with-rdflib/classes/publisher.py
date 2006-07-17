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

import sys, os, mailbox, rfc822, string, email, email.Errors, datetime, sha
from mbox import Mbox
from template import Template
from subscribers import Subscribers
from message import Message

class Publisher:
    """Class to coordinate all publication task"""


    def beginIndex(self):
        """Begin file with mail list's index"""
        
        self.template = Template()
        self.tpl = self.template.get('rdf_index_head')
        self.tpl = self.tpl.replace('{TITLE}', 'FIXME')
        today = datetime.date.today()
        self.tpl = self.tpl.replace('{DATE}', str(today))
        rdf_file = open(self.config.get('dir') + 'index.rdf', 'w+')
        rdf_file.write(self.template.get('xml_head'))
        rdf_file.write(self.template.get('rdf_head'))
        rdf_file.write(self.tpl)
        rdf_file.flush()
        rdf_file.close()


    def addIndex(self, msg):
        """Add an item to index file"""
        
        template = Template()
        tpl = template.get('rdf_index_item')

        try:
            tpl = tpl.replace('{FROM_NAME}', msg.getFromName())
            tpl = tpl.replace('{FROM_MBOX}', sha.new('mailto:'+msg.getFromMail()).hexdigest())                              
            tpl = tpl.replace('{TO}', msg.getTo())                          
            tpl = tpl.replace('{SUBJECT}', msg.getSubject())
            tpl = tpl.replace('{MESSAGE_ID}', msg.getSwamlId())
            tpl = tpl.replace('{RDF_URL}', msg.getUri())            
        except KeyError, detail:
            print 'Error proccesing messages: ' + str(detail)
            self.tpl = ''
                                        
        rdf_file = open(self.config.get('dir') + 'index.rdf', 'a')
        rdf_file.write(self.tpl)
        rdf_file.flush()
        rdf_file.close()                                        
                                    

    def closeIndex(self):
        """Close index file"""
        
        self.template = Template()
        self.tpl = self.template.get('rdf_index_foot')
        rdf_file = open(self.config.get('dir') + 'index.rdf', 'a')
        rdf_file.write(self.tpl)
        rdf_file.write(self.template.get('rdf_foot'))        
        rdf_file.flush()
        rdf_file.close()
                                                                

    def toRDF(self, msg):
        """Print a message into RDF in XML format"""        
        
        template = Template()
        tpl = template.get('rdf_message')

        rdf_file = open(self.config.get('dir') + msg.getPath(), 'w+')
        rdf_file.write(template.get('xml_head'))
        rdf_file.write(template.get('rdf_head'))
        rdf_file.flush()
            
        name = msg.getFromName()
        tpl = tpl.replace('{FROM_NAME}', name)
        mail = msg.getFromMail()
        tpl = tpl.replace('{FROM_MBOX}', sha.new('mailto:'+mail).hexdigest())
        tpl = tpl.replace('{TO}', msg.getTo())                                                                                                              
        tpl = tpl.replace('{SUBJECT}', msg.getSubject())
        tpl = tpl.replace('{DATE}', msg.getDate())
        tpl = tpl.replace('{MESSAGE_ID}', msg.getSwamlId())
        tpl = tpl.replace('{RDF_URL}', msg.getUri())
        tpl = tpl.replace('{HTML_URL}', 'FIXME')
        tpl = tpl.replace('{IN_REPLY_TO}', msg.getInReplyTo())            
        tpl = tpl.replace('{BODY}', msg.getBody())
        
        self.subscribers.add(name, mail, msg)

        rdf_file.write(tpl)
        rdf_file.write(template.get('rdf_foot'))
        rdf_file.flush()
        rdf_file.close()


    def toHTML(self, message):
        """Print a message into HTML format"""
        
        pass
    

    def publish(self):
        """Publish a mbox"""
        
        mbox = Mbox(self.config.get('mbox'))
        messages = 0
        self.default_to = ''

        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))
                        
        self.beginIndex()

        message = mbox.nextMessage()
        
        while(message != None):
            msg = Message(message, self.config)
            messages += 1
            self.addIndex(msg)
            self.toRDF(msg)
            #message.toRdf()
            #self.toHTML(msg, messages)
            message = mbox.nextMessage()
            
        self.closeIndex()

        self.subscribers.toRDF()

        return messages
    

    def __init__(self, config):
        """Constructor method"""
        
        self.config = config
        self.subscribers = Subscribers(config)
