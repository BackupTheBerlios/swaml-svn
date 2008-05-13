# -*- coding: utf-8 -*-
"""
RDFa parser, also referred to as a "RDFa Distiller" and. It is
deployed, via a CGI front-end, on the U{W3C RDFa Distiller page<http://www.w3.org/2007/08/pyRdfa/>}.

For details on RDFa, the reader should consult the U{RDFa syntax document<http://www.w3.org/TR/rdfa-syntax>}. This package
can be downloaded U{as a compressed tar file<http://dev.w3.org/2004/PythonLib-IH/dist/pyRdfa.tar.gz>}. The
distribution also includes the CGI front-end and a separate utility script to be run locally.

(Simple) Usage
==============

From a Python file, expecting an RDF/XML pretty printed output::
 from pyRdfa import processFile
 print processFile('filename.html')

Other output formats (eg, turtle) are also possible. There is a L{separate entry for CGI calls<processURI>} as well
as for L{processing an XML DOM Tree directly<parseRDFa>} (instead of a file).

Return formats
--------------

By default, the output format for the graph is RDF/XML, more exactly a "pretty" version of RDF/XML. The possible return
formats are determined by the possibilities of the RDFLib package in this respect, and the strings defined by the package for the
determination of the format. At present, the following formats are available:

 - "xml": raw RDF/XML format, without an attempt to make the output more readable
 - "pretty-xml": more readable RDF/XML. 
 - "turtle": Turtle format. 
 - "nt": N triples

Options
=======

The package also implements some optional features that are not fully part of the RDFa syntax. At the moment these are:

 - extra warnings (eg, missing C{@profile} attribute, possibly erronous CURIE-s) are added to the output graph
 - possibility that plain literals are normalized in terms of white spaces. Default: false.(The RDFa specification requires keeping the white spaces and leave applications to normalize them, if needed)
 - extra, built-in transformers are executed on the DOM tree prior to RDFa processing (see below)

Options are collected in an instance of the L{Options} class and passed to the processing functions as an extra argument. Eg,
if extra warnings are required, the code may be::
 from pyRdfa import processFile, Options
 options = Options(warnings=True)
 print processFile('filename.html',options=options)

Transformers
------------

The package uses the concept of 'transformers': the parsed DOM tree is possibly
transformed before performing the real RDFa processing. This transformer structure makes it possible to
add additional 'services' without distoring the core code of RDFa processing. (Ben Adida referred to these as "hGRDDL"...)

Some transformations are included in the package and can be used at invocation. These are:

 - 'ol' and 'ul' elements are possibly transformed to generate collections or containers. See L{transform.ContainersCollections} for further details.
 - The 'name' attribute of the 'meta' element is copied into a 'property' attribute of the same element
 - Interpreting the 'openid' references in the header. See L{transform.OpenID} for further details.
 - Implementing the Dublin Core dialect to include DC statements from the header.  See L{transform.DublinCore} for further details.
 - Use the C{@prefix} attribute as a possible replacement for the C{xmlns} formalism. See L{transform.Prefix} for further details.

The user of the package may refer to those and pass it on to the L{processFile} call via an L{Options} instance. The caller of the
package may also add his/her transformer modules. Here is a possible usage with the 'openid' transformer
added to the call::
 from pyRdfa import processFile
 from pyRdfa.transform.OpenID import OpenID_transform
 options = Options(transformers=[OpenID_transform])
 print processFile('filename.html',options=options)

In the case of a call via a CGI script, these built-in transformers can be used via extra flags, see L{processURI} for further details.

Note that the current option instance is passed to all transformers as extra parameters. Extensions of the package
may make use of that to control the transformers, if necessary.

HTML5
=====

The U{RDFa syntax<http://www.w3.org/TR/rdfa-syntax>} is defined in terms of XHTML. However, in future, 
U{HTML5<http://code.google.com/p/html5lib/>} should also be considered as 
a carrier language for RDFa. To achieve this, the distiller can be started up with a separate flag to use an HTML5 parser
instead of the (standard) Python XML parser. (The distiller relies on the fact that the HTML5
parser silently ignores attributes that are not defined yet by the HTML5 specification; although this is still a topic of
discussion at the time of writing). 

The CGI entry point for the package has a separate flag for the usage of HTML5 (see L{processURI}). Note that the
the entry point automatically switches the C{@prefix} facility on for HTML5 (see L{transform.Prefix}).

@summary: RDFa parser (distiller)
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var builtInTransformers: list of built-in transformers that are unconditionally executed.
"""

"""
$Id: __init__.py,v 1.37 2008/05/06 12:21:03 ivan Exp $ $Date: 2008/05/06 12:21:03 $

Sun Apr 13, 2008: Thanks to Wojciech Polak, who suggested (and provided some example code) to add the feature of 
using external file-like objects as input, too (the main usage being to use stdin). 

Tue May 6, 2008: Thanks to Elias Torrez, who provided with the necessary patches to interface to the HTML5 parser.

"""

__version__ = "1.5"
__author__  = 'Ivan Herman'
__contact__ = 'Ivan Herman, ivan@w3.org'
__license__ = u'W3C® SOFTWARE NOTICE AND LICENSE, http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231'

import sys
from rdflib.Graph	import Graph
from rdflib.URIRef	import URIRef
from rdflib.RDF		import RDFNS  as ns_rdf
from rdflib.RDFS	import RDFSNS as ns_rdfs

from pyRdfa.State	import ExecutionContext
from pyRdfa.Parse	import parse_one_node

import xml.dom.minidom

from pyRdfa.transform.utils			import dump
from pyRdfa.transform.HeadAbout	import head_about_transform

# Exception handling. Essentially, all the different exceptions are re-packaged into
# separate exception class, to allow for an easier management on the user level
class RDFaError(Exception) :
	"""Just a wrapper around the local exceptions. It does not any new functionality to the
	Exception class."""
	pass

class Options :
	"""Settable options. An instance of this class is stored in
	the L{execution context<ExecutionContext>} of the parser.

	@ivar space_preserve: whether plain literals should preserve spaces at output or not
	@type space_preserve: Boolean
	@ivar warning_graph: Graph to store warnings; None if no warning is to be generated
	@type warning_graph: RDFLib Graph
	@ivar transformers: extra transformers
	@type transformers: list
	@ivar use_html5: Use the HTML5Lib parser (if available)
	@type use_html5: Boolean
	"""
	def __init__(self, warnings = False, space_preserve = True, transformers=[], use_html5 = False) :
		self.space_preserve = space_preserve
		self.transformers   = transformers
		self.use_html5      = use_html5
		if warnings :
			self.warning_graph = Graph()
		else :
			self.warning_graph = None

# List of built-in transformers that are to be run regardless, because
# they are part of the RDFa spec
builtInTransformers = [
	head_about_transform
]

def _process_DOM(dom,base,outputFormat,options,local=False) :
	"""Core processing. The transformers ("pre-processing") is done
	on the DOM tree, the state is initialized, and the "real" RDFa parsing is done. Finally,
	the result (which is an RDFLib Graph) is serialized using RDFLib's serializers.

	The real work is done in the L{parser function<Parse.parse_one_node>}.

	@param dom: XML DOM Tree node (for the top level)
	@param base: URI for the default "base" value (usually the URI of the file to be processed)
	@param outputFormat: serialization format
	@param options: Options for the distiller
	@type options: L{Options}
	@keyword local: whether the call is for a local usage or via CGI (influences the way
	exceptions are handled)
	@return: serialized graph
	@rtype: string
	"""
	def _register_XML_serializer(formatstring) :
		from rdflib.plugin import register
		from rdflib.syntax import serializer, serializers
		register(formatstring,serializers.Serializer,"pyRdfa.serializers.PrettyXMLSerializer","PrettyXMLSerializer")
	def _register_Turtle_serializer(formatstring) :
		from rdflib.plugin import register
		from rdflib.syntax import serializer, serializers
		register(formatstring,serializers.Serializer,"pyRdfa.serializers.TurtleSerializer","TurtleSerializer")

	# Exchaning the pretty xml serializer agaist the version stored with this package
	if outputFormat == "pretty-xml" :
		outputFormat = "my-xml"
		_register_XML_serializer(outputFormat)
	elif outputFormat == "turtle" or outputFormat == "n3" :
		outputFormat = "my-turtle"
		_register_Turtle_serializer(outputFormat)

	# Create the RDF Graph
	graph   = Graph()
	# get the DOM tree

	html 	= dom.documentElement

	# Perform the built-in and external transformations on the HTML tree. This is,
	# in simulated form, the hGRDDL approach of Ben Adida
	for trans in options.transformers + builtInTransformers :
		trans(html,options)

	# collect the initial state. This takes care of things
	# like base, top level namespace settings, etc.
	# Ensure the proper initialization
	state = ExecutionContext(html,graph,base=base,options=options)

	# The top level subject starts with the current document; this
	# is used by the recursion
	subject = URIRef(state.base)

	# parse the whole thing recursively and fill the graph
	if local :
		parse_one_node(html,graph,subject,state,[])
		if options.warning_graph != None :
			for t in options.warning_graph : graph.add(t)
		retval = graph.serialize(format=outputFormat)
	else :
		# This is when the code is run as part of a Web CGI service. The
		# difference lies in the way exceptions are handled...
		try :
			# this is a recursive procedure through the full DOM Tree
			parse_one_node(html,graph,subject,state,[])
		except :
			# error in the input...
			(type,value,traceback) = sys.exc_info()
			msg = 'Error in RDFa content: "%s"' % value
			raise RDFaError, msg
		# serialize the graph and return the result
		retval = None
		try :
			if options.warning_graph != None :
				for t in options.warning_graph : graph.add(t)
			retval = graph.serialize(format=outputFormat)
		except :
			# XML Parsing error in the input
			(type,value,traceback) = sys.exc_info()
			msg = 'Error in graph serialization: "%s"' % value
			raise RDFaError, msg
	return retval

def _process(input,base,outputFormat,options,local=False) :
	"""Core processing. The XML input is parsed, the transformers ("pre-processing") is done
	on the DOM tree, the state is initialized, and the "real" RDFa parsing is done. Finally,
	the result (which is an RDFLib Graph) is serialized using RDFLib's serializers.

	This is just a simle front end to the L{DOM Processing function<_process_DOM>}, parsing the input.

	@param input: file like object for the XHTML input
	@param base: URI for the default "base" value (usually the URI of the file to be processed)
	@param outputFormat: serialization format
	@param options: Options for the distiller
	@type options: L{Options}
	@keyword local: whether the call is for a local usage or via CGI (influences the way
	exceptions are handled)
	@return: serialized graph
	@rtype: string
	"""
	parse = xml.dom.minidom.parse
	if options.use_html5 :
		try :
			import html5lib
			from html5lib import treebuilders
			parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
			parse = parser.parse
		except :
			(type,value,traceback) = sys.exc_info()
			msg = 'Problems importing the HTML5 parser: "%s"' % value
			raise RDFaError, msg
	
	try :
		dom = parse(input)
	except :
		# XML Parsing error in the input
		(type,value,traceback) = sys.exc_info()
		msg = 'Parsing error in input file: "%s"' % value
		raise RDFaError, msg

	return _process_DOM(dom,base,outputFormat,options,local)

def processURI(uri,outputFormat,form={}) :
	"""The standard processing of an RDFa uri (ie, as an entry point from a CGI call).

	The call accepts extra form options (ie, HTTP GET options) as follows:

	 - C{warnings=true} means that extra warnings (eg, missing C{@profile} attribute, possibly erronous CURIE-s) are added to the output graph. Default: False
	 - C{space-preserve=false} means that plain literals are normalized in terms of white spaces. Default: false.
	 - C{extras=true} means that extra, built-in transformers are executed on the DOM tree prior to RDFa processing. Default: false. Alternatively, a finer granurality can be used with the following options:
	  - C{extras-meta=true}: the 'name' attribute of the 'meta' element is copied into a 'property' attribute of the same element
	  - C{extras-dc=true}: implement the Dublin Core dialect to include DC statements from the header. See L{transform.DublinCore} for further details.
	  - C{extras-openid=true}: interpret the 'openid' references in the header. See L{transform.OpenID} for further details.
	  - C{extras-li=true}: 'ol' and 'ul' elements are possibly transformed to generate collections or containers. See L{transform.ContainersCollections} for further details.
	  - C{extras-prefix=true}: the @prefix attribute can be used as a replacement for the xmlns handling
	 - C{html5=true}: use the HTML5 parser, if available 

	@param uri: URI to access
	@param outputFormat: serialization formats, as understood by RDFLib. Note that though "turtle" is
	a possible parameter value, the RDFLib turtle generation does funny (though legal) things with
	namespaces, defining unusual and unwanted prefixes...
	@param form: extra call options (from the CGI call) to set up the local options
	@type form: cgi FieldStorage instance
	@return: serialized graph
	@rtype: string
	"""
	import urllib
	# Note the that method below will raise exceptions if the
	# uri cannot be dereferenced properly...
	# It is also the simplest dereferencing. Ie, no handling of redirections, for example...
	input = None
	try :
		input = urllib.urlopen(uri)
	except :
		# XML Parsing error in the input
		(type,value,traceback) = sys.exc_info()
		msg = 'Problems in accessing the information: "%s"\n (problematic URI: %s)' % (value,uri)
		raise RDFaError, msg

	# working through the possible options
	html5_parsing = False
	if "html5" in form.keys() and form["html5"].value.lower() == "true" :
		# the request is to perform HTML5 parsing, if possible, before trying to do proper XML
		html5_parsing = True
		# note the 'if' branch below: if this flag is set to true, than the @prefix handling is automatically turned on.
		# This is a bit speculative at the moment, but this may indeed be the only way to get RDFa
		# accepted by the HTML5 crowd...
		
	transformers = []
	if "extras" in form.keys() and form["extras"].value.lower() == "true" :
		from pyRdfa.transform.MetaName              	import meta_transform
		from pyRdfa.transform.OpenID                	import OpenID_transform
		from pyRdfa.transform.DublinCore            	import DC_transform
		from pyRdfa.transform.ContainersCollections	import decorate_li_s
		from pyRdfa.transform.Prefix				 	import set_prefixes
		transformers = [decorate_li_s, OpenID_transform, DC_transform, meta_transform,set_prefixes]
	else :
		if "extra-meta" in form.keys() and form["extra-meta"].value.lower() == "true" :
			from pyRdfa.transform.MetaName import meta_transform
			transformers.append(MetaName)
		if "extra-openid" in form.keys() and form["extra-openid"].value.lower() == "true" :
			from pyRdfa.transform.OpenID import OpenID_transform
			transformers.append(OpenID_transform)
		if "extra-dc" in form.keys() and form["extra-dc"].value.lower() == "true" :
			from pyRdfa.transform.DublinCore import DC_transform
			transformers.append(DC_transform)
		if "extra-li" in form.keys() and form["extra-li"].value.lower() == "true" :
			from pyRdfa.transform.ContainersCollections import decorate_li_s
			transformers.append(decorate_li_s)
		if html5_parsing == True or ("extra-prefix" in form.keys() and form["extra-prefix"].value.lower() == "true") :
			from pyRdfa.transform.Prefix import set_prefixes
			transformers.append(set_prefixes)

	if "warnings" in form.keys() and form["warnings"].value.lower() == "true" :
		warnings = True
	else :
		warnings = False

	if "space-preserve" in form.keys() and form["space-preserve"].value.lower() == "false" :
		space_preserve = False
	else :
		space_preserve = True

	options = Options(warnings,space_preserve,transformers,html5_parsing)
	return _process(input,uri,outputFormat,options)

def processFile(input, outputFormat="xml", options = None, base="") :
	"""The standard processing of an RDFa file.

	@param input: input file name or file-like object. If the type of the input is a string (unicode or otherwise), that
	is considered to be the name of a file, and is opened
	@keyword outputFormat: serialization format, as understood by RDFLib. Note that though "turtle" is
	a possible parameter value, the RDFLib turtle generation does funny (though legal) things with
	namespaces, defining unusual and unwanted prefixes...
	@keyword options: Options for the distiller (in case of C{None}, the default options are used)
	@type options: L{Options}
	@keyword base: the base URI to be used in the RDFa generation. In case 'input' is a file and this value is empty, the
	file name will be used.
	@return: serialized graph
	@rtype: string
	"""
	inputStream = None
	if isinstance(input,basestring) :
		# a file should be opened for the input
		try :
			inputStream = file(input)
			if base == "" : base = input
		except :
			# Problems opening the file
			(type,value,traceback) = sys.exc_info()
			msg = 'Problems in opening the file: "%s"\n (problematic file name: %s)' % (value,input)
			raise RDFaError, msg
	else :
		# This is already a file-like object
		inputStream = input	
	return _process(inputStream,base,outputFormat,options,local=True)

def parseRDFa(dom,base,graph = None,options=None) :
	"""The standard processing of an RDFa DOM into a Graph. This method is aimed at the inclusion of
	the library in other RDF applications using RDFLib.

	@param dom: DOM node for the document element (as returned from an XML parser)
	@param base: URI for the default "base" value (usually the URI of the file to be processed)
	@keyword graph: a graph. If the value is None, the graph is created.
	@type graph: RDFLib Graph
	@keyword options: Options for the distiller (in case of C{None}, the default options are used)
	@type options: L{Options}
	@return: the graph
	@rtype: RDFLib Graph
	"""
	if graph == None :
		graph = Graph()
	if options == None :
		options = Options()

	html = dom.documentElement

	# Creation of the top level execution context

	# Perform the built-in and external transformations on the HTML tree. This is,
	# in simulated form, the hGRDDL approach of Ben Adida
	for trans in options.transformers + builtInTransformers :
		trans(html,options)

	# collect the initial state. This takes care of things
	# like base, top level namespace settings, etc.
	# Ensure the proper initialization
	state = ExecutionContext(html,graph,base=base,options=options)

	# The top level subject starts with the current document; this
	# is used by the recursion
	subject = URIRef(state.base)

	# parse the whole thing recursively and fill the graph
	parse_one_node(html,graph,subject,state,[])
	if options.warning_graph != None :
		for t in options.warning_graph : graph.add(t)

	# That is it...
	return Graph


