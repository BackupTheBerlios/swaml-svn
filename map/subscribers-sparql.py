#!/usr/bin/env python2.4
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


__author__ = 'Sergio Fdez <http://www.wikier.org/>'
__contributors__ = ['Diego Berrueta <http://www.berrueta.net/>',
                    'Jose Emilio Labra <http://www.di.uniovi.es/~labra/>']
__copyright__ = 'Copyright 2005-2006, Sergio Fdez'
__license__ = 'GNU General Public License'
__version__ = '0.0.1'

import rdflib
from rdflib.sparql import sparqlGraph, GraphPattern
from rdflib import Namespace, Literal

SWAML = rdflib.Namespace('http://swaml.berlios.de/ns/0.1#')
FOAF = rdflib.Namespace('http://xmlns.com/foaf/0.1/')
RDF = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
RDFS = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')
GEO = rdflib.Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

#obtain subscribers foaf's uri 
subscribers = 'http://localhost/swaml/subscribers.rdf'
sparqlGr = sparqlGraph.SPARQLGraph()
sparqlGr.parse(subscribers)

select = ('?foaf')
where  = GraphPattern([	('?x', SWAML['subscriber'], '?y'),
			('?y', RDF['type'], FOAF['Person']),
			('?y', RDFS['seeAlso'], '?foaf')])

foafs = sparqlGr.query(select, where)

#an obtain his geopossition
for foaf in foafs:
	sparqlGr = sparqlGraph.SPARQLGraph()
	sparqlGr.parse(foaf)

	select = ('?name', '?lat', '?long')
	where  = GraphPattern([	('?x', RDF['type'], FOAF['Person']),
				('?x', FOAF['name'], '?name'),
				('?x', FOAF['based_near'], '?y'),
				('?y', GEO['lat'], '?lat'),
				('?y', GEO['long'], '?long')	])

	result = sparqlGr.query(select, where)

	for one in result:
		print ' - ' + one[0] + ' (' + one[1] + ',' + one[2] + ')'
		
	#TODO: add a query to extract 	

