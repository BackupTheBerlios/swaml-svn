# -*- coding: utf-8 -*-
"""
The core parsing function of RDFa. Some details are
put into other modules to make it clearer to update/modify (eg, generation of literals, or managing the current state).

@summary: RDFa core parser processing step
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: Parse.py,v 1.25 2008/05/02 08:33:25 ivan Exp $
$Date: 2008/05/02 08:33:25 $
"""

import sys

from pyRdfa.State   import ExecutionContext
from pyRdfa.Literal import generate_literal

from rdflib.URIRef  import URIRef
from rdflib.BNode   import BNode
from rdflib.RDF     import RDFNS  as ns_rdf
from rdflib.RDF     import type

#######################################################################
# Function to check whether one of a series of attributes
# is part of the DOM Node
def _has_one_of_attributes(node,*args) :
	"""
	Check whether one of the listed attributes is present on a (DOM) node.
	@param node: DOM element node
	@param args: possible attribute names
	@return: True or False
	@rtype: Boolean
	"""
	return True in [ node.hasAttribute(attr) for attr in args ]


#######################################################################
def parse_one_node(node,graph,parent_object,incoming_state,parent_incomplete_triples) :
	"""The (recursive) step of handling a single node. See the
	U{RDFa syntax document<http://www.w3.org/TR/rdfa-syntax>} for further details.

	@param node: the DOM node to handle
	@param graph: the RDF graph
	@type graph: RDFLib's Graph object instance
	@param parent_object: the parent's object, as an RDFLib URIRef
	@param incoming_state: the inherited state (namespaces, lang, etc)
	@type incoming_state: L{State.ExecutionContext}
	@param parent_incomplete_triples: list of hanging triples (the missing resource set to None) to be handled (or not)
	by the current node.
	@return: whether the caller has to complete it's parent's incomplete triples
	@rtype: Boolean
	"""
	def _get_resources_for_attr(attr,warning=True) :
		"""Get a series of resources encoded via CURIE-s for an attribute on a specific node.
		@param attr: the name of the attribute
		@keyword warning: if warning should be generated for invalid @rel/@rev/@property values (in some cases this
		method is invoked just to check the existence of valid values, in which case no warning should be added)
		@return: a list of RDFLib URIRef instances
		"""
		if not node.hasAttribute(attr) :
			return []
		else :
			rel  = (attr == "rel") or (attr == "rev")
			prop = (attr == "property")
			return state.get_resources(node.getAttribute(attr),rel,prop,warning)

	def _valid_rel_rev(attr) :
		"""Check whether the node has a @rel or a @rev and whether those are valid values
		@param attr: attribute name (either "rel" or "rev")
		@rtype Boolean
		"""
		return len(_get_resources_for_attr(attr,warning=False)) > 0

	# Update the state. This means, for example, the possible local settings of
	# namespaces and lang
	state = ExecutionContext(node,graph,inherited_state=incoming_state)

	#---------------------------------------------------------------------------------
	# First, let us check whether there is anything to do at all. Ie,
	# whether there is any RDFa specific attribute on the element
	#
	if not _has_one_of_attributes(node,"href","resource","about","property","rel","rev","typeof","src") :
		# nop, there is nothing to do here, just go down the tree and return...
		for n in node.childNodes :
			if n.nodeType == node.ELEMENT_NODE : parse_one_node(n,graph,parent_object,state,parent_incomplete_triples)
		return

	#-----------------------------------------------------------------
	# this flag will be used at the end of the process to control
	# whether recursion should happen at all
	recurse = True

	#-----------------------------------------------------------------
	# The goal is to establish the subject and object for local processing
	# The behaviour is slightly different depending on the presense or not
	# of the @rel/@rev attributes
	current_subject = None
	current_object  = None

	if _valid_rel_rev("rel") or _valid_rel_rev("rev") :
		# in this case there is the notion of 'left' and 'right' of @rel/@rev
		# in establishing the new Subject and the objectResource

		# set first the subject
		if node.hasAttribute("about") :
			# This not only validates the hanging triples, but will also
			# set the value for the hanging resource to the value of @about
			current_subject = state.get_Curie_ref(node.getAttribute("about"))
			retval = True
		elif node.hasAttribute("src") :
			current_subject = state.get_URI_ref(node.getAttribute("src"))
			retval = True
		elif node.hasAttribute("typeof") :
			current_subject = BNode()
		else :
			current_subject = parent_object

		# set the object resource
		if node.hasAttribute("resource") :
			current_object = state.get_Curie_ref(node.getAttribute("resource"))
		elif node.hasAttribute("href") :
			current_object = state.get_URI_ref(node.getAttribute("href"))
	else :
		# in this case all the various 'resource' setting attributes
		# behave identically, except that their value might be different
		# in terms of CURIE-s and they also have their own priority, of course
		if node.hasAttribute("about") :
			# This not only validates the hanging triples, but will also
			# set the value for the hanging resource to the value of @about
			current_subject = state.get_Curie_ref(node.getAttribute("about"))
		elif node.hasAttribute("src") :
			# This is the first fallback in case there isn't an explicit
			# @about
			current_subject = state.get_URI_ref(node.getAttribute("src"))
		elif node.hasAttribute("resource") :
			current_subject = state.get_Curie_ref(node.getAttribute("resource"))
		elif node.hasAttribute("href") :
			current_subject = state.get_URI_ref(node.getAttribute("href"))
		elif node.hasAttribute("typeof") :
			current_subject = BNode()
		else :
			current_subject = parent_object
		# in this case no non-literal triples will be generated, so the
		# only role of the current_objectResource is to be transferred to
		# the children node
		current_object = current_subject

	# ---------------------------------------------------------------------
	# The possible typeof indicates a number of type statements on the newSubject
	if node.hasAttribute("typeof") :
		for defined_type in _get_resources_for_attr("typeof") :
			graph.add((current_subject,type,defined_type))

	# ---------------------------------------------------------------------
	# In case of @rel/@rev, either triples or incomplete triples are generated
	# the (possible) incomplete triples are collected, to be forwarded to the children
	incomplete_triples  = []
	if node.hasAttribute("rel") :
		for prop in _get_resources_for_attr("rel") :
			theTriple = (current_subject,prop,current_object)
			if current_object != None :
				graph.add(theTriple)
			else :
				incomplete_triples.append(theTriple)
	if node.hasAttribute("rev") :
		for prop in _get_resources_for_attr("rev") :
			theTriple = (current_object,prop,current_subject)
			if current_object != None :
				graph.add(theTriple)
			else :
				incomplete_triples.append(theTriple)

	# ----------------------------------------------------------------------
	# Generation of the literal values, again the newSubject is the subject
	# A particularity if property is that it usually stops the parsing down the DOM tree,
	# because everything down there is part of the generated literal. The exception is if
	# the property value is specified via an explicit @content
	if node.hasAttribute("property") :
		# Generate the literal. It has been put it into a separate module to make it more managable
		# the overall return value should be set to true if any valid triple has been generated
		generate_literal(node,graph,current_subject,state)
		if not node.hasAttribute("content") : recurse = False

	# ----------------------------------------------------------------------
	# Setting the current object to a bnode is setting up a possible resource
	# for the incomplete triples downwards
	if current_object == None :
		object_to_children = BNode()
	else :
		object_to_children = current_object

	#-----------------------------------------------------------------------
	# Here is the recursion step for all the children
	if recurse :
		for n in node.childNodes :
			if n.nodeType == node.ELEMENT_NODE : parse_one_node(n,graph,object_to_children,state,incomplete_triples)

	# ---------------------------------------------------------------------
	# At this point, the parent's incomplete triples may be completed
	for (s,p,o) in parent_incomplete_triples :
		if s == None : s = current_subject
		if o == None : o = current_subject
		graph.add((s,p,o))

	# -------------------------------------------------------------------
	# This should be it...
	# -------------------------------------------------------------------
	return

#######################################################################


###################################################################################
#
# $Log: Parse.py,v $
# Revision 1.25  2008/05/02 08:33:25  ivan
# *** empty log message ***
#
# Revision 1.24  2008/04/04 09:43:41  ivan
# *** empty log message ***
#
# Revision 1.23  2008/02/19 15:27:20  ivan
# *** empty log message ***
#
# Revision 1.22  2008/02/02 15:04:15  ivan
# Added/updated epydoc documentation
#
# Revision 1.21  2008/01/27 13:20:42  ivan
# *** empty log message ***
#
# Revision 1.20  2007/12/30 11:44:14  ivan
# Updated to the state of knowledge and decisions in the group for Dec 2007.
# This includes the new (and hopefully final) version of @instanceof behaviour.
#
#
# Revision 1.15  2007/09/12 15:25:53  ivan
# 1. adapted to the latest version of the processing step discussion (around @instanceof) though this version is not yet fully accepted by the group
# 2. Using now CURIE-s for @resource and @about
#
# Revision 1.14  2007/09/09 11:52:39  ivan
# The precedence of @src and @href was incorrect, compared to the specification...
#
# Revision 1.13  2007/09/04 12:03:34  ivan
# *** empty log message ***
#
# Revision 1.12  2007/08/22 11:11:58  ivan
# Moved the collection/container management into a separate module as a transformer.
# This meant adding the post-processing possibility, too
#
# Revision 1.11  2007/08/21 15:33:47  ivan
# Added the transformation mechanism. This means:
# - removed all 'special' cases from Parse and State (eg, handling of a meta element for @name,
# all traces of the 'dotted' qualified name notation from State
# - added the import and the management of transformer functions in __init__
#
# Revision 1.10  2007/08/09 15:49:49  ivan
# Additional features built in to accomodate eRDF and DCMI style features, like:
#
# <meta> accepts @name instead of @property
# a prefix.value type rdf-qname is also accepted, not only prefix:value
# <link rel="schema.prefix"... type of elements are also accepted to define
# (top level) namespaces for the prefix
#
# Revision 1.9  2007/08/08 10:59:24  ivan
# Added the front-end to handle URI-s (as opposed to file names only)
#
# Revision 1.8  2007/08/07 14:34:07  ivan
# Changed the core algorithm, see http://www.w3.org/2007/08/RdfaAlgo.{svg,png}
#
# Revision 1.7  2007/08/06 12:44:23  ivan
# After the first round of official tests. The following tests pass:
# 0001, 0006, 0007, 0008, 0009, 0010, 0011, 0012, 0013, 0014, 0018,
# 0029, 0030, 0031, 0032
#
#


