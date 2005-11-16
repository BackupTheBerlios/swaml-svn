#!/usr/bin/python
#
# SWAML <http://swaml.berlios.de/>
# Semantic Web Archive of Mailing Lists
#
# Copyright (C) 2005 Sergio Fdez
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

import sys, os, mailbox, rfc822, string, email, email.Errors, datetime
from mbox import Mbox
from template import Template
from subscribers import Subscribers

class Publisher:

    def getIndexName(self, message, n):
        #to do: feature 1355 (allow to personalize url format)
        
        #two date formats:
        #  Case 1: May 2005 23:13:26 +0900
        #  Case 2: Fri, 16 Sep 2005 00:15:12 +0200
        #  Case 3: Fri, 06 May 05 10:25:23 Hora oficial do Brasil
        
        self.msg = message
        date = self.msg['Date'].split(',')
        index = ''
        if (len(date) == 1):
            #case 1
            date = date[0].split(' ')
            index += str(date[2]) + '-' + str(date[1])
        elif (len(date) == 2):
            #case 2 or 3
            date = date[1].split(' ')
            #case 3
            if (len(date[3])<4):
                if (date[3][1]=='9'):
                    date[3] = '19' + date[3]
                else:
                    date[3] = '20' + date[3]                
            index += str(date[3]) + '-' + str(date[2])
        else:
            index += 'unkown-date'

        if not (os.path.exists(self.config.get('dir')+index)):
            os.mkdir(self.config.get('dir')+index)
                        
        index += '/message' + str(n)
            
        return index

    def beginIndex(self):
        self.template = Template()
        self.tpl = self.template.get('rdf_index_head')
        self.tpl = self.tpl.replace('{TITLE}', 'FIXME')
        today = datetime.date(1,2,3)
        self.tpl = self.tpl.replace('{DATE}', str(today.day)+'/'+str(today.month)+'/'+str(today.year))
        rdf_file = open(self.config.get('dir') + 'index.rdf', 'w+')
        rdf_file.write(self.template.get('xml_head'))
        rdf_file.write(self.template.get('rdf_head'))
        rdf_file.write(self.tpl)
        rdf_file.flush()
        rdf_file.close()


    def addIndex(self, message, n):
        self.msg = message
        self.template = Template()
        self.tpl = self.template.get('rdf_index_item')

        try:
            self.tpl = self.tpl.replace('{FROM}', self.msg['From'])
            if (self.msg.get('To')):
                self.tpl = self.tpl.replace('{TO}', self.msg['To'])
            else:
                self.tpl = self.tpl.replace('{TO}', self.msg['Delivered-To'])
            self.tpl = self.tpl.replace('{SUBJECT}', self.msg['Subject'])
            self.tpl = self.tpl.replace('{MESSAGE_ID}', self.msg['Message-Id'])
            self.tpl = self.tpl.replace('{RDF_URL}', self.config.get('url') + self.config.get('dir') + self.getIndexName(self.msg, n) + '.rdf')
        except KeyError, detail:
            print 'Error proccesing messages: ' + str(detail)
            self.tpl = '';
                                        
        rdf_file = open(self.config.get('dir') + 'index.rdf', 'a')
        rdf_file.write(self.tpl)
        rdf_file.flush()
        rdf_file.close()                                        
                                    

    def closeIndex(self):
        self.template = Template()
        self.tpl = self.template.get('rdf_index_foot')
        rdf_file = open(self.config.get('dir') + 'index.rdf', 'a')
        rdf_file.write(self.tpl)
        rdf_file.write(self.template.get('rdf_foot'))        
        rdf_file.flush()
        rdf_file.close()


    def addSuscriber(self, from_text):
        name = ''
        mail = ''
        from_parted = from_text.split('<')
        if (len(from_parted)==1):
            name = 'unknow'
            mail = from_text
        else:
            name = from_parted[0]
            from_parted = from_parted[1].split('>')
            mail = from_parted[0]
            
        self.subscribers.add(name, mail)
                                                                

    def intoRDF(self, message, n):
        self.msg = message
        self.template = Template()
        self.tpl = self.template.get('rdf_message')

        rdf_file = open(self.config.get('dir') + self.getIndexName(self.msg, n) + '.rdf', 'w+')
        rdf_file.write(self.template.get('xml_head'))
        rdf_file.write(self.template.get('rdf_head'))
        rdf_file.flush()
                                                                
        try:
            self.tpl = self.tpl.replace('{FROM}', self.msg['From'])
            if (self.msg.get('To')):
                self.tpl = self.tpl.replace('{TO}', self.msg['To'])
            else:
                self.tpl = self.tpl.replace('{TO}', self.msg['Delivered-To'])
            self.tpl = self.tpl.replace('{SUBJECT}', self.msg['Subject'])
            self.tpl = self.tpl.replace('{DATE}', self.msg['Date'])
            self.tpl = self.tpl.replace('{MESSAGE_ID}', self.msg['Message-Id'])
            self.tpl = self.tpl.replace('{RDF_URL}', 'FIXME')
            self.tpl = self.tpl.replace('{HTML_URL}', 'FIXME')
            if (self.msg.get('In-Reply-To')):
                self.tpl = self.tpl.replace('{IN_REPLY_TO}', self.msg['In-Reply-To'])
            elif (self.msg.get('References')):
                self.tpl = self.tpl.replace('{IN_REPLY_TO}', self.msg['References'])
            else:
                self.tpl = self.tpl.replace('{IN_REPLY_TO}', 'none')
            self.tpl = self.tpl.replace('{BODY}',self.msg.fp.read())
        except KeyError, detail:
            print 'Error proccesing messages: ' + str(detail)
            self.tpl = '';

        self.addSuscriber(self.msg['From'])

        rdf_file.write(self.tpl)
        rdf_file.write(self.template.get('rdf_foot'))
        rdf_file.flush()
        rdf_file.close()


    def intoHTML(self, message):
        pass
    

    def publish(self):
        mbox = Mbox(self.config.get('file'))
        messages = 0

        if not (os.path.exists(self.config.get('dir'))):
            os.mkdir(self.config.get('dir'))
                        
        self.beginIndex()

        msg = mbox.nextMessage()
        while(msg!= None):
            messages += 1
            self.addIndex(msg, messages)
            self.intoRDF(msg, messages)
            #self.intoHTML(msg, messages)
            msg = mbox.nextMessage()
            
        self.closeIndex()

        self.subscribers.intoRDF()

        return messages
    

    def __init__(self, config):
        self.config = config
        self.subscribers = Subscribers(config)
