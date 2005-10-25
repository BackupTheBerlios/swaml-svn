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

import string

class Configuration:

    def __init__(self):
        self.dir_path = "archive/"
        self.url_base = "http://localhost/"
        self.file_path = "mbox"
                
    def setDir(self, text):
        self.dir_path = text

    def setUrl(self, text):
        self.url_base = text
        
    def setFile(self, text):
        self.file_path = text
                                
    def getDir(self):
        return self.dir_path

    def getUrl(self):
        return self.url_base

    def getFile(self):
        return self.file_path

    def show(self):
        print 'Dir:  ' + self.getDir()
        print 'URL:  ' + self.getUrl()
        print 'File: ' + self.getFile()
    
