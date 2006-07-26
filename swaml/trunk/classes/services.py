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

class Services:
    """
    Collection of util services to SWAML
    """
    
    def getFoaf(self, mail):
        """
        Services to obtain FOAF URI from an email address
        
        @param mail: an email address
        @type mail: string
        @return: the FOAF URI of this email owner
        @rtype: string
        
        @todo customize foaf service
        """
        
        mail_sha1sum = self.getShaMail(mail)
        
        # TODO: customize this with a real service
        #
        #         ideas: - PyGoogle <http://pygoogle.sourceforge.net/> 
        #                      import google
        #                      google.LICENSE_KEY = '...'
        #                      data = google.doGoogleSearch('119222cf3a2893a375cc4f884a0138155c771415 filetype:rdf')
        #
        #                - Swoogle <http://swoogle.umbc.edu/>
        
        foafs = {    '119222cf3a2893a375cc4f884a0138155c771415' : 'http://www.wikier.org/foaf.rdf',
                     '98a99390f2fe9395041bddc41e933f50e59a5ecb' : 'http://www.asturlinux.org/~berrueta/foaf.rdf',
                     '8114083efd55b6d18cae51f1591dd9906080ae89' : 'http://di002.edv.uniovi.es/~labra/labraFoaf.rdf',
                     '84d076726727b596b08198e26ef37e4817353e97' : 'http://frade.no-ip.info:2080/~ivan/foaf.rdf',
                     'bd6566af7b3bfa28f917aa545bf4174661817d79' : 'http://www.asturlinux.org/~jsmanrique/foaf.rdf'
                }
                
        if (mail_sha1sum in foafs):
            return foafs[mail_sha1sum]
        else:
            return None
        
    def getGeoPosition(self, foaf):
        """
        Obtain geography information from foaf
        """
        
        import rdflib
        from rdflib.sparql import sparqlGraph, GraphPattern
        from rdflib import Namespace, Literal
        from namespaces import SWAML, RDF, RDFS, FOAF, GEO

        sparqlGr = sparqlGraph.SPARQLGraph()
        sparqlGr.parse(foaf)
    
        select = ('?lat', '?long')
        where  = GraphPattern([    ('?x', RDF['type'], FOAF['Person']),
                    ('?x', FOAF['based_near'], '?y'),
                    ('?y', GEO['lat'], '?lat'),
                    ('?y', GEO['long'], '?long')    ])
    
        result = sparqlGr.query(select, where)
    
        for one in result:
            return [one[0], one[1]]
        
        return [None, None]

        
    def getShaMail(self, mail):
        """
        Services to obtain encrypted email address
        
        @param mail: an email address
        @type mail: string
        @return: encryted mail on foaf:mbox_sha1sum format
        @rtype: string
        """        
        
        return sha.new('mailto:'+mail).hexdigest()



        