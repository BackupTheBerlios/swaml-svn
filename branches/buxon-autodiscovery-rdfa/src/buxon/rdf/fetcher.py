# -*- coding: utf8 -*-
#
# Buxon, a sioc:Forum Visor
#
# SWAML <http://swaml.berlios.de/>
# Semantic Web Archive of Mailing Lists
#
# Copyright (C) 2006-2008 Sergio Fernández, Diego Berrueta
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

"""a fetcher for sioc:Forums"""

import sys
from rdflib import URIRef
from rdflib.Graph import ConjunctiveGraph
from rdflib.sparql.sparqlGraph import SPARQLGraph
from rdflib.sparql.graphPattern import GraphPattern
from rdflib.sparql import Query
from rdflib import Namespace
from buxon.rdf.namespaces import SIOC, RDF, RDFS, DC, DCTERMS
from buxon.rdf.ptsw import PTSW
import socket
import gtk
import urllib2
from xml.dom import minidom
from pyRdfa import parseRDFa, RDFaError

class Fetcher:

    def __request(self, url):
        """
        Request a URL
        """
        
        request = urllib2.Request(url)
        request.add_header("'User-Agent", "buxon (http://swaml.berlios.de/)")
        request.add_header("Accept", "application/rdf+xml")
        try:
            response = urllib2.urlopen(request)
            return self.__parse(response, url)
        except urllib2.HTTPError, e:
            print "Error requesting %s: %s" % (url, str(e))
            return False

    def __parse(self, response, base=None):
        """
        Parse response
        """
        
        rdfxml = "application/rdf+xml"
        xhtml = "application/xhtml+xml"
        html = "text/html"
    
        if (base == None):
            base = response.url

        if (response.code == 200):

            ct = response.info()["content-type"]
            if (len(ct.split(";"))>1):
                ct = ct.split(";")[0]
        
            if (ct == rdfxml):
                try:
                    self.graph.load(response, publicID=' ')
                    return True
                except Exception, e:
                    print "Error parsing RDF/XML:", str(e)
                    return False
            elif (ct == xhtml or ct == html):
                #FIXME: autodiscovery (XPath)
                try:
                    dom = minidom.parse(response)
                    parseRDFa(dom, response.url, self.graph)
                    return True
                except RDFaError, e:
                    print "Error parsing RDFa:", str(e)
                    return False
            else:
                print "Unknow format:", ct
                return False

        else:
            return False
            

    def __listPosts(self):
        """
        List post at cache
        """

        try:
            sparqlGr = SPARQLGraph(self.graph)
            select = ('?post', '?title')
            where  = GraphPattern([('?post', RDF['type'],   SIOC['Post']),
                              ('?post', DC['title'], '?title')])
            posts = Query.query(sparqlGr, select, where)

            print len(posts), 'posts:'

            for post, title in posts:
                print post,
                try:
                    print title
                except:
                    print '(bad formed title)'

        except Exception, details:
            print 'parsing exception:', str(details)
            return None


    def loadForum(self, uri):
        """
        Load a forum into a memory graph

        @param uri: mailing list's uri
        """

        print 'Getting forum data (', uri, ')...',
        if self.__request(uri):
            self.loaded.append(uri)
            print 'OK, loaded', len(self.graph), 'triples'

            forums = self.__getForums(self.graph)
            if forums.__len__() < 1:
                return False
        
            self.uri = forums[0]
            print 'Using ' + self.uri + ' sioc:Forum'

            if (self.pb != None):
                self.pb.progress()

            if (self.ptsw != None):
                self.ptsw.ping(uri)

            return True
        else:
            return False

    def __loadData(self, uri):
        """
        Load data

        @param uri: uri to load
        """

        if (not uri in self.loaded):
            print 'Resolving reference to get additional data (', uri, ')...',
            if self.__request(uri):
                self.loaded.append(uri)

                if (self.pb != None):
                    self.pb.progress()
                    while gtk.events_pending():
                        gtk.main_iteration()

                if (self.ptsw != None):
                    self.ptsw.ping(uri)

                print 'OK, now', len(self.graph), 'triples'

    def __getForums(self, graph):
        """
        Get all sioc:Forum's in a graph
        """

        sparqlGr = SPARQLGraph(graph)
        select = ('?uri')
        where  = GraphPattern([('?uri', RDF['type'], SIOC['Forum'])])
        forums = Query.query(sparqlGr, select, where)
        return forums;


    def loadAdditionalData(self):
        """
        Load additional data of a mailing list
        """

        for post in self.graph.objects(self.uri, SIOC['container_of']):
            if not self.hasValueForPredicate(post, SIOC['id']):
                postSeeAlso = self.getValueForPredicate(post, RDFS['seeAlso'])
                if (postSeeAlso == None):
                    self.__loadData(post)
                else:
                    self.__loadData(postSeeAlso)

        for user in self.graph.objects(predicate=SIOC['has_subscriber']):
            if not self.hasValueForPredicate(user, SIOC['email_sha1']):
                self.__loadData(user)

    def hasValueForPredicate(self, subject, predicate):
        """
        Get if a predicate exists

        @param subject: subject
        @param predicate: predicate
        """

        return (len([x for x in self.graph.objects(URIRef(subject), predicate)]) > 0)

    def getValueForPredicate(self, subject, predicate):
        """
        Get value of a predicate

        @param subject: subject
        @param predicate: predicate
        """

        value = [x for x in self.graph.objects(URIRef(subject), predicate)]
        if (len(value) > 0):
            return value[0]
        else:
            return None

    def getData(self):

        self.graph = ConjunctiveGraph()
        try:
             self.bad = self.loadForum(self.uri)
        except Exception, details:
            print '\nAn exception ocurred parsing ' + self.uri + ': ' + str(details)
            self.bad = True
            return

        if self.graph == None:
            self.bad = True
            print 'None sioc:Forum founded on', self.uri
        else:
            self.loadAdditionalData()
            #self.__listPosts()

        if (self.pb != None):
            self.pb.destroy()

        if (self.ptsw != None):
            print self.ptsw.stats()

        if self.bad:
            return None
        else:
            print 'Total triples loaded:', len(self.graph)
            return self.graph

    def __init__(self, base, ping, pb=None):
        """
        Cache constructor

        @param base: base uri to load
        @param pb: progress bar
        """

        self.uri = base
        self.graph = None
        self.bad = False
        self.loaded = []
        self.pb = pb
        self.ptsw = None
        if ping:
            self.ptsw = PTSW()

        socket.setdefaulttimeout(5)

