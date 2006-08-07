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

class MailingList:
    
    def __init__(self, config):
        """
        Constructor method
        """
        
        self.config = config
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
            
            #complete data
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
                msg = self.index.get(id)
                
                if (msg != None):
                    msg.setBody('FIXME')
                    msg.toRDF()
                    #msg.toHTML()
                    #self.index.delete(id)
                else:
                    print id

                message = mbox.nextMessage()
                
            self.index.toRDF()
    
            self.subscribers.process()
            self.subscribers.export()
            
        except Exception, detail:
            print str(detail)
            
        
        if (self.messages != messages):
            print 'Something was wrong: ' + str(self.messages) + ' parsed, but ' + str(messages) + ' processed'

        return messages
    

