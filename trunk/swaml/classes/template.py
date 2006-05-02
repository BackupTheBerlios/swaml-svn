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

import sys, string, email

class Template:
    """Templates management"""

    def get(self, template):
        """Get a template"""
        
        try:
            fich = open('includes/templates/' + template + '.tpl','r')
            head = fich.read()
            fich.close()
            return head
        except IOError, detail:
            return 'ERROR: ' +  str(detail)

                                    
