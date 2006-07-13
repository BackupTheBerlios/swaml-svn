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
import email, email.Errors

class Message:
    """Mail message abstraction"""
    
    id = 0
    
    def __init__(self, msg, config):
        """Message constructor"""
        self.__class__.id += 1
        self.msg = msg
        self.config = config
        
    def getId(self):
        return self.id
    
    def getSwamlId(self):
        #TODO: obtain a better SWAML ID
        parted_id = self.msg['Message-Id'].split('.')
        msg_id = parted_id[len(parted_id)-1] + '-' + self.msg['Date'] + '-swaml-' + str(self.id)
        return sha.new(msg_id).hexdigest()        
        
    def getPath(self):
        """Return the message's index name"""
        
        #format permited vars (feature 1355)
        message_month = 'unknow'
        message_year = 'unknow'
        message_id = str(self.id)

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
    
    def getUri(self):    
        return self.config.get('url') + self.getPath()
    
    def parseFrom(self, from_text):
        """Method to parse from field"""
        
        from_parted = from_text.split(' ')
        name = ' '.join(from_parted[:-1])
        mail = from_parted[-1]

        return [name, mail]
    
    def getFromName(self):   
        if(self.msg['From'].find('<')!= -1):
            #mail similar than: Name Surmane <name@domain.com>
            return str(self.msg.getaddr('From')[0])
        else:
            #something like: Name Surmane name@domain.com
            from_name, from_mail = self.parseFrom(self.msg['From'])
            return from_name
            
    def getFromMail(self):   
        if(self.msg['From'].find('<')!= -1):
            #mail similar than: Name Surmane <name@domain.com>
            return str(self.msg.getaddr('From')[1])
        else:
            #something like: Name Surmane name@domain.com
            from_name, from_mail = self.parseFrom(self.msg['From'])
            return from_mail             
        
        
    def getTo(self):        
        to = ' '
        
        try:                
            to = self.msg['To']
        except:
            #some mails have not a 'to' field
            to = self.config.get('defaultTo')
                
        to = to.replace('@', self.config.getAntiSpam())
        to = to.replace('<', '&lt;')
        to = to.replace('>', '&gt;')                                     
        
        return to     
    
    def getSubject(self):
        return self.msg['Subject']
    
    def getDate(self):
        return self.msg['Date']    
    
    def getInReplyTo(self):
        #if (self.msg.get('In-Reply-To')):
        #    self.tpl = self.tpl.replace('{IN_REPLY_TO}', self.msg['In-Reply-To'])
        #elif (self.msg.get('References')):
        #    self.tpl = self.tpl.replace('{IN_REPLY_TO}', self.msg['References'])
        #else:
        #    self.tpl = self.tpl.replace('{IN_REPLY_TO}', 'none')        
        return 'FIXME'
    
    def getBody(self):
        return self.msg.fp.read()
        
        