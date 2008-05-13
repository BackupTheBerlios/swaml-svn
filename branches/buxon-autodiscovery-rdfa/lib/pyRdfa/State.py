# -*- coding: utf-8 -*-
"""
Parser's execution context (a.k.a. state) object and handling. The state includes:

  - dictionary for namespaces. Keys are the namespace prefixes, values are RDFLib Namespace instances
  - language, retrieved from C{@xml:lang}
  - URI base, determined by <base> (or set explicitly). This is a little bit superfluous, because the current RDFa syntax does not make use of C{@xml:base}; ie, this could be a global value.  But the structure is more or less prepared to add C{@xml:base} easily, if needed.
  - options, in the form of an L{Options<pyRdfa.Options>} instance

The execution context object is also used to turn relative URI-s and CURIES into real URI references.

@summary: RDFa core parser processing step
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var XHTML_PREFIX: prefix for the XHTML vocabulary namespace
@var XHTML_URI: URI prefix of the XHTML vocabulary
@var RDFa_PROFILE: the official RDFa profile URI
@var RDFa_VERSION: the official version string of RDFa
@var usual_protocols: list of "usual" protocols (used to generate warnings when CURIES are not protected)
@var _predefined_rel: list of predefined C{@rev} and C{@rel} values that should be mapped onto the XHTML vocabulary URI-s.
@var _predefined_property: list of predefined C{@property} values that should be mapped onto the XHTML vocabulary URI-s. (At present, this list is empty, but this has been an ongoing question in the group, so the I{mechanism} of checking is still there.)
@var __bnodes: dictionary of blank node names to real blank node
@var __empty_bnode: I{The} Bnode to be associated with the CURIE of the form "C{_:}".
"""

"""
$Id: State.py,v 1.41 2008/05/06 11:38:42 ivan Exp $
$Date: 2008/05/06 11:38:42 $
"""

from rdflib.RDF         import RDFNS   as ns_rdf
from rdflib.RDFS        import RDFSNS  as ns_rdfs
from rdflib.RDFS        import comment as rdfs_comment
from rdflib.Namespace   import Namespace
from rdflib.URIRef      import URIRef
from rdflib.Literal     import Literal
from rdflib.BNode       import BNode

_XSD_NS = Namespace(u'http://www.w3.org/2001/XMLSchema#')

import re
import random
import urlparse

RDFa_PROFILE    = "http://www.w3.org/1999/xhtml/vocab"
RDFa_VERSION    = "XHTML+RDFa 1.0"
usual_protocols = ["http","https","mailto","ftp","urn","gopher","tel"]

####Predefined @rel/@rev/@property values
# predefined values for the @rel and @rev values. These are considered to be part of a specific
# namespace, defined by the RDFa document.
XHTML_PREFIX = "xhv"
XHTML_URI    = "http://www.w3.org/1999/xhtml/vocab#"

_predefined_rel  = ['alternate', 'appendix', 'cite', 'bookmark', 'chapter', 'contents',
'copyright', 'glossary', 'help', 'icon', 'index', 'meta', 'next', 'p3pv1', 'prev',
'role', 'section', 'subsection', 'start', 'license', 'up', 'last', 'stylesheet','first','top']

#_predefined_property  = ['description', 'generator', 'keywords', 'reference', 'robots', 'title']
_predefined_property  = []

#### Managing blank nodes for CURIE-s
__bnodes = {}
__empty_bnode = BNode()
def _get_bnode_from_Curie(var) :
	"""
	'Var' gives the string after the coloumn in a CURIE of the form C{_:XXX}. If this variable has been used
	before, then the corresponding BNode is returned; otherwise a new BNode is created and
	associated to that value.
	@param var: CURIE BNode identifier
	@return: BNode
	"""
	if len(var) == 0 :
		return __empty_bnode
	if var in __bnodes :
		return __bnodes[var]
	else :
		retval = BNode()
		__bnodes[var] = retval
		return retval

#### Core Class definition
class ExecutionContext :
	"""State at a specific node, including the current set
	of namespaces in the RDFLib sense, the
	current language, and the base. The class is also used to interpret URI-s and CURIE-s to produce
	URI references for RDFLib.
	"""
	def __init__(self,node,graph,inherited_state=None,base="",options=None) :
		"""
		@param node: the current DOM Node
		@param graph: the RDFLib Graph
		@keyword inherited_state: the state as inherited
		from upper layers. This inherited_state is mixed with the state information
		retrieved from the current node.
		@type inherited_state: L{State.ExecutionContext}
		@keyword base: string denoting the base URI for the specific node. This is
		overridden by a possible C{@xml:base}, but it overrides the possible
		base inherited from the upper layers. Note: C{@xml:base} is not officially part of the
		XHTML+RDFa syntax, but this could/should handle by the DTD validation of the
		incoming document. The code itself is prepared for the C{@xml:base} usage, in 
		accordnace with the reference (in the RDFa syntax document) to other XML dialects that might use it.
		@keyword options: invocation option
		@type options: L{Options<pyRdfa.Options>}
		"""
		#-----------------------------------------------------------------
		# settling the base
		# note that, strictly speaking, it is not necessary to add the base to the
		# context, because there is only one place to set it (<base> element of the <header>).
		# It is done because it is prepared for a possible future change in direction of
		# accepting xml:base on each element.
		# At the moment, it is invoked with a 'None' at the top level of parsing, that is
		# when the <base> element is looked for.
		if inherited_state :
			self.base            = inherited_state.base
			self.warning_URI_ref = inherited_state.warning_URI_ref
			self.options         = inherited_state.options
		else :
			# this is the branch called from the very top
			self.base = ""
			for bases in node.getElementsByTagName("base") :
				if bases.hasAttribute("href") :
					self.base = bases.getAttribute("href")
					continue
			if self.base == "" :
				self.base = base
			if node.hasAttribute("xml:base") :
				self.base = node.getAttribute("xml:base")		
			self.warning_URI_ref = URIRef(base)
			# this is just to play safe. I believe this branch should actually not happen...
			if options == None :
				from pyRdfa import Options
				self.options = Options()
			else :
				self.options = options

			# check the the presense of the @profile and or @version attribute for the RDFa profile...
			# (Not 100% sure that is necessary...)
			html = node.ownerDocument.documentElement
			if not( html.hasAttribute("version") and RDFa_VERSION == html.getAttribute("version") ):
				# see if least the profile has been set
				
				# Find the <head> element
				head = None
				for index in range(0,html.childNodes.length-1) :
					if html.childNodes.item(index).nodeName == "head" :
						head = html.childNodes.item(index)
						break
				
				if not( head != None and head.hasAttribute("profile") and RDFa_PROFILE in head.getAttribute("profile").strip().split() ) :
					self.add_warning("Neither an RDFa profile nor an RFDa version is set")

		#-----------------------------------------------------------------
		# Settling the language tags
		# check first the lang or xml:lang attribute
		# RDFa does not allow the lang attribute. XHTML5 relies :-( on @lang;
		# I just want to be prepared here...
		if node.hasAttribute("lang") :
			self.lang = node.getAttribute("lang")
			if len(self.lang) == 0 : self.lang = None
		elif node.hasAttribute("xml:lang") :
			self.lang = node.getAttribute("xml:lang")
			if len(self.lang) == 0 : self.lang = None
		elif inherited_state :
			self.lang = inherited_state.lang
		else :
			self.lang = None

		#-----------------------------------------------------------------
		# Handling namespaces
		# First get the local xmlns declarations/namespaces stuff.
		dict = {}
		for i in range(0,node.attributes.length) :
			attr = node.attributes.item(i)
			if attr.name.find('xmlns:') == 0 :	
				# yep, there is a namespace setting
				key = attr.localName
				if key != "" :
					# exclude the top level xmlns setting...
					uri = attr.value
					# 1. create a new Namespace entry
					ns = Namespace(uri)
					# 2. 'bind' it in the current graph to
					# get a nicer output
					graph.bind(key,uri)
					# 3. Add an entry to the dictionary
					dict[key] = ns

		# See if anything has been collected at all.
		# If not, the namespaces of the incoming state is
		# taken over
		self.ns = {}
		if len(dict) == 0 and inherited_state :
			self.ns = inherited_state.ns
		else :
			if inherited_state :
				for k in inherited_state.ns : self.ns[k] = inherited_state.ns[k]
				# copying the newly found namespace, possibly overwriting
				# incoming values
				for k in dict :  self.ns[k] = dict[k]
			else :
				self.ns = dict

		# see if the xhtml core vocabulary has been set
		self.xhtml_prefix = None
		for key in self.ns.keys() :
			if XHTML_URI == str(self.ns[key]) :
				self.xhtml_prefix = key
				break
		if self.xhtml_prefix == None :
			if XHTML_PREFIX not in self.ns :
				self.ns[XHTML_PREFIX] = Namespace(XHTML_URI)
				self.xhtml_prefix = XHTML_PREFIX
			else :
				# the most disagreeable thing, the user has used
				# the prefix for something else...
				self.xhtml_prefix = XHTML_PREFIX + '_' + ("%d" % random.randint(1,1000))
				self.ns[self.xhtml_prefix] = Namespace(XHTML_URI)
			graph.bind(self.xhtml_prefix,XHTML_URI)

		# extra tricks for unusual usages...
		# if the 'rdf' prefix is not used, it is artificially added...
		if "rdf" not in self.ns :
			self.ns["rdf"] = ns_rdf
		if "rdfs" not in self.ns :
			self.ns["rdfs"] = ns_rdfs
			
		# Final touch: setting the default namespace...
		if node.hasAttribute("xmlns") :
			self.defaultNS = node.getAttribute("xmlns")
		elif inherited_state and inherited_state.defaultNS != None :
			self.defaultNS = inherited_state.defaultNS
		else :
			self.defaultNS = None

	def _get_predefined_rels(self,val,warning) :
		"""Get the predefined URI value for the C{@rel/@rev} attribute.
		@param val: attribute name
		@param warning: whether a warning should be generated or not
		@type warning: boolean
		@return: URIRef for the predefined URI (or None)
		"""
		vv = val.strip().lower()
		if vv in _predefined_rel :
			return self.ns[self.xhtml_prefix][vv]
		else :
			if warning: self.add_warning("invalid @rel/@rev value: '%s'" % val)
			return None

	def _get_predefined_properties(self,val,warning) :
		"""Get the predefined value for the C{@property} attribute.
		@param val: attribute name
		@param warning: whether a warning should be generated or not
		@type warning: boolean
		@return: URIRef for the predefined URI (or None)
		"""
		vv = val.strip().lower()
		if vv in _predefined_property :
			return self.ns[self.xhtml_prefix][vv]
		else :
			if warning: self.add_warning("invalid @property value: '%s'" % val)
			return None

	def add_warning(self,txt) :
		"""Add a warning. A comment triplet is added to the separate "warning" graph.
		@param txt: the warning text. It is preceded by the string "==== pyRdfa Warning ==== "
		"""
		if self.options.warning_graph != None :
			comment = Literal("=== pyRdfa warning === " + txt)
			self.options.warning_graph.add((self.warning_URI_ref,rdfs_comment,comment))

	def get_resource(self,val,rel=False,prop=False,warning=True) :
		"""Get a resource for a CURIE.
		The input argument is a CURIE; this is interpreted
		via the current namespaces and the corresponding URI Reference is returned
		@param val: string of the form "prefix:lname"
		@keyword rel: whether the predefined C{@rel/@rev} values should also be interpreted
		@keyword prop: whether the predefined C{@property} values should also be interpreted
		@keyword warning: whether warning should be generated
		@return: an RDFLib URIRef instance (or None)
		"""
		if val == "" :
			return None
		elif val.find(":") != -1 :
			key   = val.split(":",1)[0]
			lname = val.split(":",1)[1]
			if key == "_" :
				# A possible error: this method is invoked for property URI-s, which
				# should not refer to a blank node. This case is checked and a possible
				# error condition is handled
				raise Exception("Blank node CURIE cannot be used in this position: _:%s" % lname)
			if key == "" :
				# This is the ":blabla" case
				key = self.xhtml_prefix
		else :
			# if the resources correspond to a @rel or @rev or @property, then there
			# may be one more possibility here, namely that it is one of the
			# predefined values
			if rel :
				return self._get_predefined_rels(val,warning)
			elif prop :
				return self._get_predefined_properties(val,warning)
			else:
				if warning: self.add_warning("invalid CURIE (without prefix): '%s'" % val)
				return None

		if key not in self.ns :
			raise Exception("CURIE used with non declared prefix: %s" % key)
		else :
			if lname == "" :
				return URIRef(str(self.ns[key]))
			else :
				return self.ns[key][lname]

	def get_resources(self,val,rel=False,prop=False,warning=True) :
		"""Get a series of resources encoded in CURIE-s.
		The input argument is a list of CURIE-s; these are interpreted
		via the current namespaces and the corresponding URI References are returned.
		@param val: strings of the form prefix':'lname, separated by space
		@keyword rel: whether the predefined C{@rel/@rev} values should also be interpreted
		@keyword prop: whether the predefined C{@property} values should also be interpreted
		@keyword warning: if warning should be generated for invalid @rel/@rev/@property values (in some cases this
		method is invoked just to check the existence of valid values, in which case no warning should be added)
		@return: a list of RDFLib URIRef instances (possibly empty)
		"""
		val.strip()
		resources = [ self.get_resource(v,rel,prop,warning) for v in val.split() if v != None ]
		return [ r for r in resources if r != None ]

	def get_URI_ref(self,val) :
		"""Create a URI RDFLib resource for a URI.
		The input argument is a URI. It is checked whether it is a local
		reference with a '#' or not. If yes, a URIRef combined with the
		stored base value is returned. In both cases a URIRef for a full URI is created
		and returned
		@param val: URI string
		@return: an RDFLib URIRef instance
		"""
		if val == "" :
			return URIRef(self.base)
		elif val[0] == '[' and val[-1] == ']' :
			raise Exception("Illegal usage of CURIE: %s" % val)
		else :
			return URIRef(urlparse.urljoin(self.base,val))

	def get_Curie_ref(self,val) :
		"""Create a URI RDFLib resource for a CURIE.
		The input argument is a CURIE. This means that it is
		  - either of the form [a:b] where a:b should be resolved as an 'unprotected' CURIE, or
		  - it is a traditional URI (relative or absolute)

		If the second case the URI value is also compared to 'usual' URI protocols ('http', 'https', 'ftp', etc)
		(see L{usual_protocols}).
		If there is no match, a warning is generated (indeed, a frequent mistake in authoring RDFa is to forget
		the '[' and ']' characters to "protect" CURIE-s.)

		@param val: CURIE string
		@return: an RDFLib URIRef instance
		"""
		if len(val) == 0 :
			return URIRef(self.base)
		elif val[0] == "[" :
			if val[-1] == "]" :
				curie = val[1:-1]
				# A possible Blank node reference should be separated here:
				if len(curie) >= 2 and curie[0] == "_" and curie[1] == ":" :
					return _get_bnode_from_Curie(curie[2:])
				else :
					return self.get_resource(val[1:-1])
			else :
				# illegal CURIE...
				raise Exception("Illegal CURIE: %s" % val)
		else :
			# check the value, to see if an error may have been made...
			# Usual protocol values in the URI
			v = val.strip().lower()
			protocol = urlparse.urlparse(val)[0]
			if protocol != "" and protocol not in usual_protocols :
				err = "Possible URI error with '%s'; the intention may have been to use a protected CURIE" % val
				self.add_warning(err)
			return self.get_URI_ref(val)

