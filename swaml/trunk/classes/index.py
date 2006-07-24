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
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
from rdflib import RDF
from rdflib.store import Store

class Index:
    
    def __init__(self, config):
        self.config = config
        self.items = []
        
    def add(self, new):
        self.items.append(new.getUri())
        
    def toRDF(self):
        """Dump inde to RDF file"""

        #rdf graph
        store = Graph()
        
        #namespaces
        from namespaces import SWAML, RDFS, FOAF, DC
        store.bind('swaml', SWAML)
        store.bind('foaf', FOAF)
        store.bind('rdfs', RDFS)
        store.bind('dc', DC)
        
        index = URIRef(self.config.get('url')+'index.rdf')
        store.add((index, RDF.type, SWAML['MailingList']))
        store.add((index, DC['title'], Literal(u'title (FIXME)')))
        store.add((index, DC['publisher'], Literal(u'SWAML')))
        store.add((index, DC['description'], Literal(u'RDF files of a mailing list')))
        store.add((index, SWAML['subscribers'], URIRef(self.config.get('url')+'subscribers.rdf')))
                                           
        items = BNode()
        store.add((index, SWAML['sentMails'], items))
        store.add((items, RDF.type, RDF.Bag))

        #a BNode for each item
        for item in self.items:
            store.add((items, RDF.li, URIRef(item)))
                    
        #and dump to disk
        rdf_file = open(self.config.get('dir')+'index.rdf', 'w+')
        rdf_file.write(store.serialize(format="pretty-xml"))
        rdf_file.flush()
        rdf_file.close()
    
        
