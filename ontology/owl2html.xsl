<?xml version="1.0" encoding="UTF-8"?>
<!--COPYRIGHT (C) 2004-2006 
	Laboratory of Advanced Information Technology and Ebiquity Group
	Department of Computer Science and Electronic Engineering
	University of Maryland Baltimore County
	1000 hilltop circle
	Baltimore, MD 21250
	ALL RIGHTS RESERVED.
	
	Author:  		Li Ding  ( http://www.cs.umbc.edu/~dingli1)
	Version:		1.3
	Last Update:	2005/01/28
-->

<!-- Transforms an OWL ontology into a java file for jena inference  -->

<!DOCTYPE xsl:stylesheet [
  <!ENTITY rdf          "http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <!ENTITY rdfs		"http://www.w3.org/2000/01/rdf-schema#">
  <!ENTITY dc		"http://purl.org/dc/elements/1.1/" > 
  <!ENTITY xsd		"http://www.w3.org/2001/XMLSchema#">
  <!ENTITY owl		"http://www.w3.org/2002/07/owl#">
]>

  	<xsl:stylesheet	version="1.0"
			xmlns:xsl="http://www.w3.org/1999/XSL/Transform"    
    			xmlns:rdf="&rdf;"
    			xmlns:rdfs="&rdfs;"
    			xmlns:xsd="&xsd;"
    			xmlns:owl="&owl;"
    			xmlns ='http://daml.umbc.edu/ontologies/webofbelief/xslt/owl2jena.xsl'
	>

  <xsl:output method="xml" indent='yes' doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"/>

  <!-- global variables and functions -->
  <!--   <xsl:variable name="namespace" select="concat(/rdf:RDF/@xml:base,'#')"/>  -->
  <xsl:variable name="namespace" select="/rdf:RDF/@xml:base"/>
<!--  <xsl:variable name="class-name" select="translate(//owl:Ontology/rdfs:label, $lowercase, $uppercase)"/>  -->
  <xsl:variable name="class-name" select="//owl:Ontology/rdfs:label"/>

  <xsl:variable name="package-name"> edu.umbc.trustweb.core.vocabulary </xsl:variable>
  <!-- TODO: setup your package name before conversion	e.g. edu.umbc.sharenet.vocabulary  -->


  <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'"/>
  <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>


  <xsl:variable name="nodeset-ontology" select=".//*[
		  rdf:type/@rdf:resource='&owl;Ontology'  or (local-name()='Ontology' and namespace-uri()='&owl;')
  ]" />

  <xsl:variable name="nodeset-class" select="./rdf:RDF/*[     
		   rdf:type/@rdf:resource='&owl;Class'  or (local-name()='Class' and namespace-uri()='&owl;')
 		or rdf:type/@rdf:resource='&rdfs;Class' or (local-name()='Class' and namespace-uri()='&rdfs;')
  ]" />

  <xsl:variable name="nodeset-property" select=".//*[  
		   (local-name()='Property' and namespace-uri()='&rdf;')
		or (local-name()='ConstraintProperty' and namespace-uri()='&rdfs;')
		or (local-name()='DatatypeProperty' and namespace-uri()='&owl;')
		or (local-name()='ObjectProperty' and namespace-uri()='&owl;')
							
  ]" />

  <xsl:variable name="nodeset-individual" select=".//*[
	  		 (@rdf:ID or @rdf:about or @rdf:resource or count(child::*)>1)
		  and not (namespace-uri()='&rdfs;')
		  and not (namespace-uri()='&owl;')
		  and not (local-name()='RDF')
  ]" />


  <!-- main template: generate the java file here--> 


<xsl:template match="/">

<html>

 <head>
  <title>SWAML Ontology</title>
  <meta name="DC.creator" content="UMBC Ontology Formatter" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="meta" title="DOAP" type="application/rdf+xml" href="/doap.rdf" />
  <style type="text/css">

	body { 	
		background: #CCCCCC; 
		font-family: Helvetica, Verdana, Arial, sans-serif;
		font-size: 12px;
		line-height: 14px;
		margin: 2em;
	}

	h2 {	
		text-align: center;
		font-weight: bold;
		font-size: 3em;
	}

	.submenu {
		text-align: center;
	}

	td {
		padding: 2em;
	}

  </style>
 </head>

<body>

<h2>SWAML Ontology</h2>

<p class="submenu">
	<a href="#Ontology">Ontology Description</a> | 
	<a href="#Classes">Classes</a> | 
	<a href="#Properties">Properties</a> | 
	<a href="#Individuals">Individuals</a> | 
	<a href="#Undetermined "> Undetermined </a>
</p>

<table border="1" cellspacing="0" width="100%" id="AutoNumber2" bgcolor="#f2f2f2" bordercolor="#000000" cellpadding="0">
<tr>
<td>

<h3><a name="Ontology">Ontology Description</a></h3>
        <xsl:if test="count($nodeset-ontology)>0">
        <ol>
           <xsl:apply-templates select="$nodeset-ontology" mode="details">  
          </xsl:apply-templates>
        </ol>
        </xsl:if>
<p></p>
<h3><a name="Classes">Classes</a> (<xsl:value-of select="count($nodeset-class)"/>):</h3>

        <xsl:if test="count($nodeset-class)>0">
        <ol>
           <xsl:apply-templates select="$nodeset-class" mode="details">  
          </xsl:apply-templates>
        </ol>
        </xsl:if>


<p></p>
<h3><a name="Properties">Properties</a> (<xsl:value-of select="count($nodeset-property)"/>):</h3>
        <xsl:if test="count($nodeset-property)>0">
        <ol>
           <xsl:apply-templates select="$nodeset-property" mode="details">  
          </xsl:apply-templates>
        </ol>
        </xsl:if>

<p></p>
<h3><a name="Individuals">Individuals</a> (<xsl:value-of select="count($nodeset-individual)"/>):</h3>
        <xsl:if test="count($nodeset-individual)>0">
        <ol>
           <xsl:apply-templates select="$nodeset-individual" mode="details">  
          </xsl:apply-templates>
        </ol>
        </xsl:if>

<p></p>
<h3><a name="Undetermined ">Undetermined (N/A)</a> </h3>
<p></p>

</td>
</tr>
</table>


<h3>References:</h3>
<ul>
  <li>
	<a href="http://swaml.berlios.de/">SWAML Project</a>  
  </li>
  <li>
	<a href="http://www.w3.org/TR/REC-rdf-syntax/">RDF Syntax and Model</a>  
  </li>
  <li>
	<a href="http://www.w3.org/TR/rdf-schema/">RDF Schemas</a>
  </li>
  <li>
	<a href="http://www.w3.org/TR/owl-ref/">OWL Web Ontology Language Reference</a> 
  </li>
  <li>
	<a href="http://www.w3.org/TR/owl-semantics/">OWL Web Ontology Language Semantics and Abstract Syntax </a>
  </li>
  <li>
	<a href="http://www.w3.org/TR/xslt">XSL Transformations (XSLT) Version 1.0</a>
  </li>
  <li>
	<a href="http://www.wasab.dk/morten/2004/05/owl2html.xsl">OWL2HTML XSLT</a> (We made some changes based on this application)
  </li>   
  <li>
	<a href="http://www.w3.org/2002/06/rdfs2html.xsl">RDF2HTML XSLT</a> (We learned many good ideas from this application)
  </li>
</ul>

<hr/>
$Author: Wikier $ - $Id: owl2html.xsl,v 1.3.1 2006/08/10 9:26:57 Wikier Exp $

</body>

</html>


</xsl:template>



  <xsl:template match="*" mode="details">

    <li>
   
    <b>
	[
     <xsl:variable name="ref">
     <xsl:choose>
        <xsl:when test="@rdf:ID">
			<xsl:value-of select="@rdf:ID"/>
        </xsl:when>
        <xsl:when test="@rdf:about">
			<xsl:value-of select="@rdf:about"/>
        </xsl:when>
        <xsl:otherwise>
			BLANK
        </xsl:otherwise>
     </xsl:choose>
     </xsl:variable>

     <xsl:if test="string-length($ref)>0">	
		    <a name="{$ref}"><xsl:value-of select="$ref"/></a> 
     </xsl:if> 	
	]
    </b>
	( rdf:type
	
		<xsl:call-template name="url">
	            <xsl:with-param name="ns" select="namespace-uri()"/>
	            <xsl:with-param name="name" select="local-name()"/>
	    </xsl:call-template>
	)


<!--     <xsl:if test="count(*)+count(@*[local-name()!=ID and local-name()!=about])>0">	 -->
		<xsl:if test="count(*)+count(@*)>0">
	    <ul>
				<xsl:text> </xsl:text>	
    	<xsl:apply-templates select="." mode="attribute"/>
    
	    <xsl:apply-templates select="*" mode="child"/>
    
    	</ul>
     </xsl:if> 	

    </li>
  </xsl:template>


  <xsl:template name="url">
	<xsl:param name="ns"/>
	<xsl:param name="name"/>
      	<xsl:choose>
           <xsl:when test="$ns='&rdf;'">
		<a href="{concat($ns,$name)}"> rdf:<xsl:value-of select="$name"/></a>  
           </xsl:when>
           <xsl:when test="$ns='&rdfs;'">
		<a href="{concat($ns,$name)}"> rdfs:<xsl:value-of select="$name"/></a>  
           </xsl:when>
           <xsl:when test="$ns='&owl;'">
		<a href="{concat($ns,$name)}"> owl:<xsl:value-of select="$name"/></a>  
           </xsl:when>
           <xsl:when test="$ns='&dc;'">
		<a href="{concat($ns,$name)}"> dc:<xsl:value-of select="$name"/></a>  
           </xsl:when>
           <xsl:when test="$ns=/rdf:RDF/@xml:base">
		<a href="{concat('#',$name)}"> <xsl:value-of select="$name"/></a>  
           </xsl:when>
           <xsl:when test="(string-length($ns)>0) or starts-with($name,'http://')">
		<a href="{concat($ns,$name)}"> <xsl:value-of select="$name"/></a>  
           </xsl:when>
           <xsl:otherwise>
		<xsl:value-of select="$name"/>
           </xsl:otherwise>
	</xsl:choose>
  </xsl:template>



  <xsl:template match="*" mode="resource">
      	<xsl:choose>
	   <xsl:when test="@rdf:resource">
		<a href="{@rdf:resource}"> <xsl:value-of select="@rdf:resource"/></a>  
           </xsl:when>
	</xsl:choose>
  </xsl:template>

<xsl:template match="*" mode="attribute">
<!--	<xsl:for-each select="@*[local-name()!=ID and local-name()!=about]"> -->
	<xsl:for-each select="@*[local-name()!=lang]">
	<li>

	<xsl:call-template name="url">
		<xsl:with-param name="ns" select="namespace-uri()"/>
		<xsl:with-param name="name" select="local-name()"/>
	</xsl:call-template>
	
	-- 
	<xsl:call-template name="url">
		<xsl:with-param name="ns" select="''"/>
		<xsl:with-param name="name" select="."/>
	</xsl:call-template>

	</li>
	</xsl:for-each>
</xsl:template>

  <xsl:template match="*" mode="child">
	<li>

	<i>
	<xsl:call-template name="url">
            <xsl:with-param name="ns" select="namespace-uri()"/>
            <xsl:with-param name="name" select="local-name()"/>
        </xsl:call-template>
	</i>
	
	<xsl:text> -- </xsl:text>	    
      	<xsl:choose>
       <xsl:when test="@rdf:resource">
			<xsl:apply-templates select="." mode="resource"/>
       </xsl:when>

       <xsl:when test="@*">
			<xsl:value-of select='text()'/>
			<xsl:if test="@xml:lang">
				^^<xsl:apply-templates select="@xml:lang" mode="resource"/>
			</xsl:if>
			<ul>
				<xsl:text> </xsl:text>	
				<xsl:apply-templates select="." mode="attribute"/>
			</ul>
       </xsl:when>
       <xsl:otherwise>
			<xsl:value-of select='text()'/>
			<xsl:if test="@xml:lang">
				^^<xsl:apply-templates select="@xml:lang" mode="resource"/>
			</xsl:if>
			<ul> 
				<xsl:text> </xsl:text>	
				<xsl:apply-templates select="./*" mode="details"/>
			</ul>
       </xsl:otherwise>
	</xsl:choose>

      	
	</li>
  </xsl:template>

</xsl:stylesheet>
