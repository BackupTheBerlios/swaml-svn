# -*- coding: utf-8 -*-
"""
Possibility to use the C{@prefix} attribute instead of C{@xmlns:} to set the prefixes for Curies. 

At the moment, although RDFa does I{not} use XML namespaces for CURIE-s, it does use the C{@xmlns:} attributes (borrowed from XML namespaces)
to set the prefixes for CURIE-s. This may not be the best options on long term, in view of the disagreements in HTML circles
on the usage of namespaces (or anything that reminds of namespaces). This transformer implements an alternative. For each element
in the DOM tree, the C{@prefix} attribute is considered. The value of the attribute should be::
 <... prefix="pref1=uri1 pref2=uri2" ...>
The behaviour is I{exactly} the same as if::
 <... xmlns:pref1="uri1" xmlns:pref2="uri2" ...>	 
was used, including inheritance rules of prefixes. C{@prefix} has a higher priority; ie, in case of::
 <... prefix="pref=uri1" xmlns:pref="uri2" ...>
the setting with C{uri2} will be ignored.

@summary: Transfomer to handle C{@prefix} as an alternative to C{@xmlns:} type namespace setting
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: Prefix.py,v 1.2 2008/05/06 11:39:00 ivan Exp $
$Date: 2008/05/06 11:39:00 $
"""

import random
from pyRdfa.transform.utils import traverse_tree, dump

def set_prefixes(html,options) :
	def _handle_prefix(node) :
		if node.hasAttribute("prefix") :
			for pref in node.getAttribute("prefix").strip().split() :
				# this should be of the format prefix=uri
				spec = pref.split('=')
				if len(spec) >= 2 :
					node.setAttributeNS("","xmlns:%s" % spec[0],spec[1])
		return False
		# We have to collect the current bnode id-s from the file to avoid conflicts
	traverse_tree(html,_handle_prefix)

