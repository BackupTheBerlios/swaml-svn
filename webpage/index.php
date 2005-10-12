<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
 <head>
  <title>SWAML - Semantic Web Archive of Mailing Lists</title>
  <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
  <meta name="robots" content="index,follow" />
  <meta name="keywords" content="SWAML, semantic web, mailing lists, python" />
  <meta name="language" content="es" />
  <link rel="stylesheet" type="text/css" charset="iso-8859-1" href="style.css" />
  <link rel="shortcut icon" href="favicon.ico" />
  <link rel="meta" title="DOAP" type="application/rdf+xml" href="doap.rdf" />
 </head>

 <body>
  <div id="header"> 
   <table summary="logo" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr valign="middle">
     <td>
      <div id="logo">
       <a href="/">SWAML</a>
      </div>
     </td>
     <td>
      <div id="berlios"> 
       <a href="http://developer.berlios.de/"><img src="images/berlios.png" width="132" height="50"
       alt="proyect hosted by BerliOS"/></a>
      </div>
     </td>
    </tr>
   </table>
  </div>

  <!-- toolbar -->
  <div class="toolbar">
   <div id="navbuttons">
    <a href="/" class="wiki">Home</a> &nbsp;|&nbsp;
    <a href="#news" class="wiki">News</a> &nbsp;|&nbsp;
    <a href="#doc" class="wiki">Documentation</a> &nbsp;|&nbsp;
    <a href="#files" class="download">Files</a> &nbsp;|&nbsp;
    <a href="/wiki" class="wiki">Wiki</a> &nbsp;|&nbsp;
    <a href="#contact" class="wiki">Contact</a>
   </div>
   <div id="search">
    <form action="http://www.google.es/search" method="get">
     <img src="/images/search.png" class="wiki-button" alt="search" width="22" height="22" />
     <input type="text" name="q" value="" />
     <input name="sitesearch" value="swaml.berlios.de" type="hidden" />
    </form>
   </div>
  </div>

  <br/><br/><br/>

  <!-- Page content -->
  <div id="content">
   <p>
     <acronym title="Semantic Web Archive of Mailing Lists">SWAML</acronym> is  a research 
     project around the semantic web tecnologies to publish the mailing lists&acute;s archive into 
     an <acronym title="Resource Description Framework">RDF</acronym> format, developed 
     at <a href="http://www.euitio.uniovi.es/">University of Oviedo</a> (Spain). You can
     visit the <a href="http://developer.berlios.de/projects/swaml/">project page at BerliOS</a>
     for more details.
   </p>

   <h2>
    <a href="#news"></a>News &nbsp; 
    <a href="/rss/news" type="application/rss+xml"><img src="images/xml.png" width="36" height="14" alt="XML"/></a>
   </h2>
   <div class="wikitext">
    <?php

        $months = array(   "Jan" => "01",
                           "Feb" => "02",
                           "Mar" => "03",
                           "Apr" => "04",
                           "May" => "05",
                           "Jun" => "06",
                           "Jul" => "07",
                           "Aug" => "08",
                           "Sep" => "09",
                           "Oct" => "10",
                           "Nov" => "11",
                           "Dec" => "12"
                    );

          require_once('magpierss/rss_fetch.inc');
          $url = 'http://developer.berlios.de/export/rss20_bsnews.php?group_id=4806';

          $rss = fetch_rss($url);

          if ( $rss and !$rss->ERROR) {

	    $num_items = 10;
	    $items = array_slice($rss->items, 0, $num_items);
	    echo "<dl>\n";

	    foreach ($items as $item) {
	      $title = $item[title];
	      $link  = $item[link];
	      $description  = $item[description];
	      $pubDate  = $item[pubdate];
	      $date = explode(" ", $pubDate);
	      echo "      <dt>[" . $date[1] . "-" . $months[$date[2]] . "-" . $date[3] . "]";
              echo " <a href=\"" . $link . "\">" . $title . "</a></dt>\n";
	      echo "      <dd>" . $description . "</dd>\n";
	    }

	    echo "    </dl>\n\n";

          } else { echo "Error: " . $rss->ERROR; }

    ?>
   </div>

   <h2><a href="#doc"></a>Documentation</h2>
   <div class="wikitext">
    <dl>
     <dt><a href="http://download.berlios.de/swaml/propuesta.pdf">propuesta.pdf</a>:</dt>
     <dd>a document in Spanish with the initial idea that reason the development of this project</dd>
    </dl>  
   </div>

   <h2><a href="#files"></a>Files</h2>
   <div class="wikitext">
    <p>There aren not files until the moment. While you can visit the <a href="/files">files section</a> 
    or <a href="/wsvn">subversion repository web interface</a>.</p>
   </div>

   <h2><a href="#contact"></a>Contact</h2>
   <div class="wikitext">
    <p>You can contact to any <a href="/members-list"> members of project</a>. Also you have a several 
    <a href="/lists">mailing lists</a>:</p>
    <ul>
     <li><a href="/lists/devel">Developers mailing list</a></li>
     <li><a href="/lists/users">Users mailing list</a></li>
     <li><a href="/lists/spanish">Spanish Users mailing list</a></li>
    </ul>
    <br/><p>Also, you can <a href="/bugs">report a bug</a> or sending a <a href="/features">feature request</a> 
    without you need to subscribe of any of <a href="/lists">project mailing lists</a>.</p>
   </div>

   <br/><br/><br/>

   <div id="revision">
    <p class="editdate">Last update on Wed 12 October 2005</p>
   </div>
  </div>

  <div id="footer">
     <a href="/doap.rdf" type="application/rdf+xml"><img src="images/rdfmeta.png" alt="RDF Meta" /></a> &nbsp; 
     <a href="http://validator.w3.org/check/referer"><img src="images/xhtml.png" alt="Valid XHTML" /></a> &nbsp;
     <a href="http://jigsaw.w3.org/css-validator/check/referer"><img src="images/css.png" alt="Valid CSS" /></a> &nbsp;
  </div>

 </body>
</html>
