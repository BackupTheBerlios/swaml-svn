<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es" lang="es">
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
    <table width="100%" cellpadding="0" cellspacing="0" border="0">
     <tr valign="middle">
      <td align="left">
       <a href="/" class="wiki">Home</a>
       &nbsp;|&nbsp;
       <a href="#news" class="wiki">News</a>
       &nbsp;|&nbsp;
       <a href="#doc" class="wiki">Documentation</a>
       &nbsp;|&nbsp;
       <a href="#files" class="download">Files</a>
       &nbsp;|&nbsp;
       <a href="/wiki" class="wiki">Wiki</a>
       &nbsp;|&nbsp;
       <a href="#contact" class="wiki">Contact</a>
      </td>
      <td align="right" width="150">
       <div id="search">
        <form action="http://www.google.es/search" method="get">
         <nobr>
	  <img src="/images/search.png" class="wiki-button" alt="search" width="22" height="22"/>
	  <input type="text" name="q" value="" />
          <input name="sitesearch" value="swaml.berlios.de" type="hidden"/>
	 </nobr>
        </form>
       </div>
      </td>
     </tr>
    </table>
   </div>
  </div>

  <!-- Page content -->
  <div id="content">
   <p>
     <acronym title="Semantic Web Archive of Mailing Lists">SWAML</acronym> is  a research 
     project around the semantic web tecnologies to publish the mailing lists's archive into 
     an <acronym title="Resource Description Framework">RDF</acronym> format, developed 
     at <a href="http://www.euitio.uniovi.es/">University of Oviedo</a> (Spain). You can
     visit the <a href="http://developer.berlios.de/projects/swaml/">project page at BerliOS</a>
     for more details.
   </p>

   <h2>
    <a href="#news"></a>News &nbsp; 
    <a href="http://developer.berlios.de/export/rss20_bsnews.php?group_id=4806" type="application/rss+xml"><img 
    src="images/xml.png" width="36" height="14" alt="XML"/></a>
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
	    echo "<ul>\n";

	    foreach ($items as $item) {
	      $news++;
	      $title = $item[title];
	      $link  = $item[link];
	      $description  = $item[description];
	      $pubDate  = $item[pubdate];
	      $date = explode(" ", $pubDate);
	      echo "      <li>[" . $date[1] . "-" . $months[$date[2]] . "-" . $date[3] . "]\n";
              echo " <a href=\"" . $link . "\">" . $title . "</a>: " . $description . "</li>\n";
	    }

	    echo "    </ul>\n\n";

          } else { echo "Error: " . $rss->ERROR; }

    ?>
   </div>

   <h2><a href="#doc"></a>Documentation</h2>
   <div class="wikitext">
    There aren't documentation until the moment.
   </div>

   <h2><a href="#files"></a>Files</h2>
   <div class="wikitext">
    There aren't files until the moment. While you can visit the 
    <a href="http://svn.berlios.de/wsvn/swaml">subversion repository web interface</a>.
   </div>

   <h2><a href="#contact"></a>Contact</h2>
   <div class="wikitext">
    <ul>
     <li>Sergio Fdez &lt;<a href="mailto:wikierATasturlinux.org">wikierATasturlinux.org</a>&gt;</li>
     <li>Diego Berrueta &lt;<a href="mailto:diegoATberrueta.net">diegoATberrueta.net</a>&gt;</li>
     <li>Jose E. Labra &lt;<a href="mailto:labraATuniovi.es">labraATuniovi.es</a>&gt;</li>
    </ul>
   </div>

   <br/><br/><br/>

   <div id="revision">
    <p class="editdate">Last update on Mon 3 October 2005</p>
   </div>
  </div>

 </body>
</html>
