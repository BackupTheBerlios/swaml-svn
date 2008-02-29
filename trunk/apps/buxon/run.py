#!/usr/bin/env python2.4
# -*- coding: utf8 -*-

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

"""Buxon, a sioc:Forum browser"""

import sys
sys.path.append('./src')

import os
import logging
import pygtk
pygtk.require('2.0')
import gtk, pango
from gazpacho.loader.loader import ObjectBuilder
from buxon.ui.gtkui import GtkUI
from buxon.ui.loadprogressbar import LoadProgressBar
from buxon.ui.calendarwindow import CalendarWindow
from buxon.rdf.cache import Cache
from buxon.rdf.namespaces import SIOC, RDF, DC, DCTERMS

try:
    import rdflib
    from rdflib import sparql, Namespace
except:
    print 'RDFLib is required'
    sys.exit(-1)


class Callbacks:

    def destroy(self):
        return buxon.destroy()

    def goButtonClicked(self):
        uri = widgets.get_widget('urlInput').get_text()
        if (uri != ''):
            buxon.clear()
            buxon.clearSearchForm()
            buxon.messageBar( 'query on ' + uri)
            buxon.uri = uri
            buxon.drawTree(buxon.getPosts(uri))

    def searchButtonClicked(self):
        uri = buxon.getUri()
        if (uri != None):
            buxon.clear()
            buxon.text.get_buffer().set_text('')
            text = widgets.get_widget('searchInput').get_text()
            min, max = buxon.getDates()
            buxon.drawTree(buxon.getPosts(uri, min, max, text))

    def selectRow(self, path, column):
        buxon.showPost()

    def fromButtonClicked(self):
        CalendarWindow(widgets.get_widget('fromEntry'))

    def toButtonClicked(self):
        CalendarWindow(widgets.get_widget('toEntry'))

    def alertButtonClicked(self):
        buxon.alertWindow.destroy()


class Buxon(GtkUI):

    def clear(self):
        """
Clear all GTK components on Buxon
        """

        #tree
        self.treeTranslator = {}
        for column in self.treeView.get_columns():
            self.treeView.remove_column(column)

        #text
        self.text.get_buffer().set_text('')

    def clearSearchForm(self):
        """
        Clear search form
        """

        widgets.get_widget('searchInput').set_text('')
        widgets.get_widget('fromEntry').set_text('01/01/1995')
        widgets.get_widget('toEntry').set_text('31/31/2010')

    def showPost(self):
        """
        Show post selected at gtk.TreeView
        """

        selection = self.treeView.get_selection()
        (model, iter) = selection.get_selected()
        uri = model.get_value(iter, 0)
        author, authorUri, listName, listUri, title, date, content = self.cache.getPost(uri)
        self.messageBar('loaded post ' + uri)
        self.writePost(uri, author, authorUri, listName, listUri, title, date, content)

    def writePost(self, uri, author=None, authorUri='', listName=None, listUri='', title='', date='', content=''):
        """
        Write a post on the gtkTextView

        @param uri: post uri
        @param author: author's name
        @param authorUri: author's uri
        @param listName: mailing list's name
        @param listUri: mailing list's uri
        @param title: post subject
        @param date: post date
        @param content: post body
        """

        PANGO_SCALE = 1024
        buffer = self.text.get_buffer()
        buffer.set_text('')
        iter = buffer.get_iter_at_offset(0)
        buffer.insert(iter, '\n')

        buffer.insert_with_tags_by_name(iter, 'Post URI: \t', 'bold')
        buffer.insert_with_tags_by_name(iter, uri, 'monospace')
        buffer.insert(iter, '\n')

        buffer.insert_with_tags_by_name(iter, 'From: \t', 'bold')
        if (author == None):
            buffer.insert_with_tags_by_name(iter, authorUri, 'monospace')
        else:
            buffer.insert(iter, author)
            buffer.insert(iter, '  <')
            buffer.insert_with_tags_by_name(iter, authorUri, 'monospace')
            buffer.insert(iter, '>')
        buffer.insert(iter, '\n')

        buffer.insert_with_tags_by_name(iter, 'To: \t\t', 'bold')
        if (listName == None):
            buffer.insert_with_tags_by_name(iter, listUri, 'monospace')
        else:
            buffer.insert(iter, listName)
            buffer.insert(iter, '  <')
            buffer.insert_with_tags_by_name(iter, listUri, 'monospace')
            buffer.insert(iter, '>')
        buffer.insert(iter, '\n')

        buffer.insert_with_tags_by_name(iter, 'Subject: \t', 'bold')
        buffer.insert(iter, title)
        buffer.insert(iter, '\n')

        buffer.insert_with_tags_by_name(iter, 'Date: \t', 'bold')
        buffer.insert(iter, date)
        buffer.insert(iter, '\n\n')

        buffer.insert_with_tags_by_name(iter, content, 'wrap_mode')

        buffer.insert(iter, '\n')

    def getDates(self):
        """
        Get selected dates

        @return: dates
        @rtype: tuple
        """

        #min date
        fromDate = widgets.get_widget('fromEntry').get_text().split('/')
        min  = float(fromDate[2]) * 10000000000
        min += float(fromDate[1]) * 100000000
        min += float(fromDate[0]) * 1000000

        #max date
        toDate = widgets.get_widget('toEntry').get_text().split('/')
        max  = float(toDate[2]) * 10000000000
        max += float(toDate[1]) * 100000000
        max += float(toDate[0]) * 1000000

        return min, max

    def getPosts(self, uri, min=None, max=None, text=None):
        """
        Get mailing list's posts

        @param uri: mailing list's uri
        @param min: min date
        @param max: max date
        @param text: text to search
        """

        if (self.cache == None):
            pb = LoadProgressBar()
            self.cache = Cache(uri, self.checkping.get_active(), pb)
        else:
            if (uri!=self.cache.uri or not bool(self.cache.graph)):
                pb = LoadProgressBar()
                self.cache = Cache(uri, self.checkping.get_active(), pb)

        min, max = self.getDates()

        if bool(self.cache.graph):
            posts = self.cache.query()

            if (posts == None):
                self.messageBar('unknow problem parsing RDF at ' + self.uri)
                return None
            else:
                if (min!=None or max!=None or text!=None):
                    posts = self.cache.filterPosts(posts, min, max, text)
                return posts
        else:
            self.alert('An exception ocurred parsing this URI')
            return None

    def drawTree(self, posts):
        """
        Draw post on gtk.TreeView

        @param posts: posts
        @type posts: tuple
        """

        if (posts!=None and len(posts)>0):

            #create tree
            self.treeStore = gtk.TreeStore(str, str)
            self.treeView.set_model(self.treeStore)

            #append items
            parent = None
            for (post, title, date, creator, content, parent) in posts:
                self.treeTranslator[post] = self.treeStore.append(self.__getParent(parent), [str(post), str(title)])
                #print 'drawing post', post, 'on tree'

            #and show it
            treeColumn = gtk.TreeViewColumn('Posts')
            self.treeView.append_column(treeColumn)
            cell = gtk.CellRendererText()
            treeColumn.pack_start(cell, True)
            treeColumn.add_attribute(cell, 'text', 1)
            treeColumn.set_sort_column_id(0)

            self.messageBar('loaded ' + self.cache.uri)

        else:

            self.messageBar('no posts found at ' + self.cache.uri)

    def __getParent(self, uri):
        """
        Get the parent post

        @param uri: post uri
        @return: parent uri
        """

        if (uri in self.treeTranslator):
            return self.treeTranslator[uri]
        else:
            return None

    def messageBar(self, text):
        """
        Write a message on the status bar

        @param text: text
        """

        self.statusbar.push(0, text)

    def insertBufferTag(self, buffer, name, property, value):
        """
        Insert a new tag on buffer

        @param buffer: buffer
        @param name: tag name
        @param property: property to customize
        @param value: property value
        """

        tag = gtk.TextTag(name)
        tag.set_property(property, value)
        table = buffer.get_tag_table()
        table.add(tag)

    def getUri(self):
        """
        Get actual URI

        @return: actual uri
        """

        if (self.cache == None):
            return None
        else:
            return self.cache.uri

    def destroy(self):
        """
        Destoy all the infraestructure
        """

        print 'Exiting...'
        gtk.main_quit()
        return gtk.FALSE

    def main(self, uri=None):
        """
        Main bucle

        @param uri: uri
        """

        #widgets
        self.treeView = widgets.get_widget('postsTree')

        self.text = widgets.get_widget('buxonTextView')
        buffer = self.text.get_buffer()
        self.insertBufferTag(buffer, 'bold', 'weight', pango.WEIGHT_BOLD)
        self.insertBufferTag(buffer, 'monospace', 'family', 'monospace')
        self.insertBufferTag(buffer, 'wrap_mode', 'wrap_mode', gtk.WRAP_WORD)

        self.input = widgets.get_widget('urlInput')
        self.checkping = widgets.get_widget('checkping')
        self.statusbar = widgets.get_widget('buxonStatusbar')
        self.messageBar('ready')

        #main window
        self.window = widgets.get_widget('buxon')
        if (os.path.exists('/usr/share/pixmaps/buxon.xpm')):
            self.window.set_icon_from_file('/usr/share/pixmaps/buxon.xpm')
        else:
            self.window.set_icon_from_file(self.base + 'includes/images/rdf.xpm')
        self.window.show()

        if (uri != None):
            self.input.set_text(uri)

        gtk.main()

    def __init__(self, base='./'):
        """
        Buxon constructor

        @param base: base directory
        """

        GtkUI.__init__(self, 'buxon', base)

        self.base = base
        self.cache = None
        self.treeTranslator = {}


#global vars
widgets = None
callbacks = None
buxon = None

class BuxonMain:

    def __init__(self, argv, base='./'):
        """
        All operation that Buxon need to run
        """

        #configure buxon logger
        self.logger = logging.getLogger('buxon')
        self.logger.setLevel(logging.DEBUG)
        _hdlr = logging.StreamHandler()
        _hdlr.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s'))
        self.logger.addHandler(_hdlr)

        self.logger.info('Starting up Buxon')

        try:
            global widgets
            global callbacks
            global buxon

            widgets = ObjectBuilder(base + 'includes/ui/graphical/buxon.glade')
            callbacks = Callbacks()
            widgets.signal_autoconnect(Callbacks.__dict__)
            self.logger.debug('GUI loaded')

            buxon = Buxon(base)

            if ('-h' in argv or '--help' in argv):
                buxon.usage()

            if (len(argv)>0):
                buxon.main(argv[0])
            else:
                buxon.main()

        except KeyboardInterrupt:
            self.logger.info('Received Ctrl+C or another break signal. Exiting...')
            sys.exit()


if __name__ == '__main__':
    BuxonMain(sys.argv[1:])

