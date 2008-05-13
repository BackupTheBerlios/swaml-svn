from rdflib import RDF, RDFS

from rdflib	   import URIRef, Literal, BNode
from rdflib.util  import first, uniq, more_than
from rdflib.Graph import Seq

from rdflib.syntax.serializers	import Serializer
from pyRdfa.serializers.XMLWriter import XMLWriter

XMLLANG = "http://www.w3.org/XML/1998/namespacelang"


# TODO:
def fix(val):
	"strip off _: from nodeIDs... as they are not valid NCNames"
	if val.startswith("_:"):
		return val[2:]
	else:
		return val

class PrettyXMLSerializer(Serializer):

	def __init__(self, store, max_depth=8):
		super(PrettyXMLSerializer, self).__init__(store)
		self.listHeads = [ l for l in self.store.subjects(RDF.first,None) if (None,RDF.rest,l) not in self.store ]

	def serialize(self, stream, base=None, encoding=None, **args):
		self.__serialized = {}
		store = self.store
		self.base = base
		#self.max_depth = args.get("max_depth", 3)
		self.max_depth = 8

		self.nm = nm = store.namespace_manager
		self.writer = writer = XMLWriter(stream, nm, encoding)

		namespaces = {}
		possible = uniq(store.predicates()) + uniq(store.objects(None, RDF.type))
		for predicate in possible:
			prefix, namespace, local = nm.compute_qname(predicate)
			namespaces[prefix] = namespace
		namespaces["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
		writer.push(RDF.RDF)
		writer.namespaces(namespaces.iteritems())

		# Write out subjects that can not be inline
		for subject in store.subjects():
			if (None, None, subject) in store:
				if (subject, None, subject) in store:
					self.subject(subject, 1)
			else:
				self.subject(subject, 1)

		# write out anything that has not yet been reached
		for subject in store.subjects():
			self.subject(subject, 1)

		writer.pop(RDF.RDF)

		# Set to None so that the memory can get garbage collected.
		self.__serialized = None

	def subject(self, subject, depth=1):
		store  = self.store
		writer = self.writer
		if not subject in self.__serialized:
			self.__serialized[subject] = 1
			type = first(store.objects(subject, RDF.type))
			try:
				self.nm.qname(type)
			except:
				type = None
			element = type or RDF.Description
			writer.push(element)
			if isinstance(subject, BNode):
				def subj_as_obj_more_than(ceil):
					return more_than(store.triples((None, None, subject)), ceil)
				if (depth == 1 and subj_as_obj_more_than(0)) or subj_as_obj_more_than(1):
					writer.attribute(RDF.nodeID, fix(subject))
			else:
				writer.attribute(RDF.about, self.relativize(subject))
			if (subject, None, None) in store:
				for predicate, object in store.predicate_objects(subject):
					if not (predicate==RDF.type and object==type):
						self.predicate(predicate, object, depth+1)
			writer.pop(element)

	def predicate(self, predicate, object, depth=1):
		def defaultCase() :
			if depth <= self.max_depth:
				self.subject(object, depth+1)
			elif isinstance(object, BNode):
				writer.attribute(RDF.nodeID, fix(object))
			else:
				writer.attribute(RDF.resource, self.relativize(object))
		#####
		
		writer = self.writer
		store = self.store
		writer.push(predicate)
		
		if isinstance(object, Literal):
			attributes = ""
			if object.language:
				writer.attribute(XMLLANG, object.language)
			if object.datatype:
				if ("%s" % object.datatype) == "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral" :
					writer.attribute(RDF.parseType, "Literal")
				else :
					writer.attribute(RDF.datatype, object.datatype)
			writer.text(object)
		elif object in self.__serialized or not (object, None, None) in store:
			if isinstance(object, BNode):
				if more_than(store.triples((None, None, object)), 0):
					writer.attribute(RDF.nodeID, fix(object))
			else:
				writer.attribute(RDF.resource, self.relativize(object))
		elif (object,RDF.type,RDF.Seq) in store or (object,RDF.type,RDF.Bag) in store or (object,RDF.type,RDF.Alt) in store :
			seq = Seq(store,object)
			self.__serialized[object] = 1
			if (object,RDF.type,RDF.Seq) in store :
				typ = RDF.Seq
			elif (object,RDF.type,RDF.Alt) in store :
				typ = RDF.Alt
			else :
				typ = RDF.Bag
			writer.push(typ)
			for item in seq :
				self.predicate(RDF.li,item,depth+1)
			writer.pop(typ)
		elif object in self.listHeads :
			items = [item for item in store.items(object)]
			if True not in [ isinstance(item,Literal) for item in items ] :
				# This is a kosher list that could be handled with the Collection parse type trick
				collection = object
				self.__serialized[object] = 1
				writer.attribute(RDF.parseType, "Collection")
				for item in items :
					if item in self.__serialized :
						# bugger; already done somewhere else... :-)
						writer.push(RDF.Description)
						if isinstance(item, BNode):
							if more_than(store.triples((None, None, item)), 0):
								writer.attribute(RDF.nodeID, fix(item))
						else:
							writer.attribute(RDF.about, self.relativize(item))
						writer.pop(RDF.Description)
					else :
						self.subject(item)
						self.__serialized[item] = 1
			else :
				defaultCase()
		else :
			defaultCase()
		writer.pop(predicate)

