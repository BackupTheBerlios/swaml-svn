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

class Publisher:
    """Class to coordinate all publication task"""

    def getIndexName(self, message, n):
        """Return the message's index name"""
        
        #format permited vars (feature 1355)
        message_month = 'unknow'
        message_year = 'unknow'
        message_id = str(n)

        self.msg = message
        date_text = self.msg['Date'].split(',')                

        #possible date formats:
        #  Case 1: May 2005 23:13:26 +0900
        #  Case 2: Fri, 16 Sep 2005 00:15:12 +0200
        #          Wed,  6 Jul 2005 16:54:29 +0200
        #  Case 3: Fri, 06 May 05 10:25:23 Hora oficial do Brasil
        #
        #to do: locate an standar function to parse date
        
        if (len(date_text) == 1):
            #case 1
            date = date_text[0].split(' ')
            message_month = date[1]
            message_year = date[2]

        elif (len(date_text) == 2):
            #case 2 or 3
            date = date_text[1]
            while(date[0]==' '):
                date = date[1:]
            date = date.split(' ')
            
            if (len(date[2])<4):
                #case 3
                if (date[2][0]=='9'):
                    date[2] = '19' + date[2]
                else:
                    date[2] = '20' + date[2]                

            message_month = date[1]
            message_year = date[2]


        index = self.config.get('format')
        index = index.replace('MM', message_month)
        index = index.replace('YY', message_year)
        index = index.replace('ID', message_id)

        dirs = index.split('/')[:-1]
        index_dir = ''
        for one_dir in dirs:
            index_dir += one_dir + '/'
            if not (os.path.exists(self.config.get('dir')+index_dir)):
                os.mkdir(self.config.get('dir')+index_dir)
            
        return index


    def parseFrom(self, from_text):
        """Method to parse from field"""
        
        name = ''
        mail = ''
        from_parted = from_text.split('<')
        if (len(from_parted)==1):
            name = from_text.replace('@', self.config.getAntiSpam())
            mail = from_text
        else:
            name = from_parted[0][:-1]
            from_parted = from_parted[1].split('>')
            mail = from_parted[0]

        return [name, mail]
            
            
    def getId(self, id, date, n):
        """Return a message's unique id"""
        
        parted_id = id.split('.')
        msg_id = parted_id[len(parted_id)-1] + '-' + date + '-swaml-' + str(n)
        return sha.new(msg_id).hexdigest()


    def beginIndex(self):
        """Begin file with mail list's index"""
        
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
        """Add an item to index file"""
        
        self.msg = message
        self.template = Template()
        self.tpl = self.template.get('rdf_index_item')

        try:
            from_name, from_mail = self.parseFrom(self.msg['From'])
            self.tpl = self.tpl.replace('{FROM_NAME}', from_name)
            self.tpl = self.tpl.replace('{FROM_MBOX}', sha.new('mailto:'+from_mail).hexdigest())

            #somes mails have not a 'to' field
            tmp_to = ' '
            try:                
                tmp_to = self.msg['To']
                if (self.default_to == ''):
                    self.default_to = tmp_to
            except:
                if (self.default_to != ''):
                    tmp_to = self.default_to         
                    
            tmp_to = tmp_to.replace('@', self.config.getAntiSpam())
            tmp_to = tmp_to.replace('<', '&lt;')
            tmp_to = tmp_to.replace('>', '&gt;')                                 
            self.tpl = self.tpl.replace('{TO}', tmp_to)  
                            
            self.tpl = self.tpl.replace('{SUBJECT}', self.msg['Subject'])

            #self.tpl = self.tpl.replace('{MESSAGE_ID}', self.msg['Message-Id'])
            self.tpl = self.tpl.replace('{MESSAGE_ID}', self.getId(self.msg['Message-Id'], self.msg['Date'], n))

            self.tpl = self.tpl.replace('{RDF_URL}', self.config.get('url') + self.config.get('dir') + self.getIndexName(self.msg, n) + '.rdf')
            
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


    def addSubscriber(self, from_text):
        """Add a new subscriber"""
        
        name, mail = self.parseFrom(from_text)
        self.subscribers.add(name, mail)
                                                                

    def toRDF(self, message, n):
        """Print a message into RDF in XML format"""
        
        msg = message
        template = Template()
        tpl = template.get('rdf_message')

        rdf_file = open(self.config.get('dir') + self.getIndexName(msg, n), 'w+')
        rdf_file.write(template.get('xml_head'))
        rdf_file.write(template.get('rdf_head'))
        rdf_file.flush()
                                                                
        try:
            from_name, from_mail = self.parseFrom(msg['From'])
            tpl = tpl.replace('{FROM_NAME}', from_name)
            tpl = tpl.replace('{FROM_MBOX}', sha.new('mailto:'+from_mail).hexdigest())
            
            #some mails have not a 'to' field
            tmp_to = ' '
            try:                
                tmp_to = msg['To']
                if (self.default_to == ''):
                    self.default_to = tmp_to
            except:
                if (self.default_to != ''):
                    tmp_to = self.default_to   
                    
            tmp_to = tmp_to.replace('@', self.config.getAntiSpam())
            tmp_to = tmp_to.replace('<', '&lt;')
            tmp_to = tmp_to.replace('>', '&gt;')                                     
            tpl = tpl.replace('{TO}', tmp_to)              
                                                                                                    
            tpl = tpl.replace('{SUBJECT}', msg['Subject'])

            tpl = tpl.replace('{DATE}', msg['Date'])

            #self.tpl = self.tpl.replace('{MESSAGE_ID}', self.msg['Message-Id'])
            tpl = tpl.replace('{MESSAGE_ID}', self.getId(msg['Message-Id'], msg['Date'], n))

            tpl = tpl.replace('{RDF_URL}', 'FIXME')
            tpl = tpl.replace('{HTML_URL}', 'FIXME')

            #pending to link indexes
            tpl = tpl.replace('{IN_REPLY_TO}', 'FIXME')
            #if (self.msg.get('In-Reply-To')):
            #    self.tpl = self.tpl.replace('{IN_REPLY_TO}', self.msg['In-Reply-To'])
            #elif (self.msg.get('References')):
            #    self.tpl = self.tpl.replace('{IN_REPLY_TO}', self.msg['References'])
            #else:
            #    self.tpl = self.tpl.replace('{IN_REPLY_TO}', 'none')
                
            tpl = tpl.replace('{BODY}', msg.fp.read())
            
        except KeyError, detail:
            print 'Error proccesing messages: ' + str(detail)
            tpl = '';

        self.addSubscriber(msg['From'])

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

        msg = mbox.nextMessage()
        while(msg!= None):
            messages += 1
            self.addIndex(msg, messages)
            self.toRDF(msg, messages)
            #message = Message(self.config, msg, messages)
            #message.toRdf()
            #self.toHTML(msg, messages)
            msg = mbox.nextMessage()
            
        self.closeIndex()

        self.subscribers.toRDF()

        return messages
    

    def __init__(self, config):
        """Constructor method"""
        
        self.config = config
        self.subscribers = Subscribers(config)
