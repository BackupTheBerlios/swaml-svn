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
from subscribers import Subscribers
from message import Message
from index import Index

class Publisher:
    """Class to coordinate all publication task"""                                                               

    def publish(self):
        """Publish a mbox"""
        
        mbox = Mbox(self.config.get('mbox'))
        messages = 0

        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))

        message = mbox.nextMessage()
        
        while(message != None):
            msg = Message(message, self.config)
            messages += 1
            self.index.add(msg)
            self.subscribers.add(msg)
            subscriber = self.subscribers.get(msg.getFromMail())
            msg.setSender(subscriber)
            msg.toRDF()
            #msg.toHTML()
            message = mbox.nextMessage()
            
        self.index.toRDF()

        self.subscribers.process()
        self.subscribers.export()

        return messages
    

    def __init__(self, config):
        """Constructor method"""
        
        self.config = config
        self.subscribers = Subscribers(config)
        self.index = Index(self.config)
