<?php

// PHP utils functions to SWAML webpage
//*************************************

class SWAML {

	function make_clickable($text) {

	  $ret = " " . $text;
	// matches an "xxxx://yyyy" URL at the start of a line, or after a space.
	// xxxx can only be alpha characters.
	// yyyy is anything up to the first space, newline, or comma.
	$ret = preg_replace("#([\n ])([a-z]+?)://([a-z0-9\-\.,\?!%\*_\#:;~\\&$@\/=\+]+)#i", "\\1<a href=\"\\2://\\3\" target=\"_blank\">\\2://\\3</a>", $ret);

	// matches a "www.xxxx.yyyy[/zzzz]" kinda lazy URL thing
	// Must contain at least 2 dots. xxxx contains either alphanum, or "-"
	// yyyy contains either alphanum, "-", or "."
	// zzzz is optional.. will contain everything up to the first space, newline, or comma.
	// This is slightly restrictive - it's not going to match stuff like "forums.foo.com"
	// This is to keep it from getting annoying and matching stuff that's not meant to be a link.
	$ret = preg_replace("#([\n ])www\.([a-z0-9\-]+)\.([a-z0-9\-.\~]+)((?:/[a-z0-9\-\.,\?!%\*_\#:;~\\&$@\/=\+]*)?)#i", "\\1<a href=\"http://www.\\2.\\3\\4\" target=\"_blank\">www.\\2.\\3\\4</a>", $ret);

	// matches an email@domain type address at the start of a line, or after a space.
	// Note: Only the followed chars are valid; alphanums, "-", "_" and or ".".
	$ret = preg_replace("#([\n ])([a-z0-9\-_.]+?)@([\w\-]+\.([\w\-\.]+\.)?[\w]+)#i", "\\1<a href=\"mailto:\\2@\\3\">\\2@\\3</a>", $ret);

		// Remove our padding..
		$ret = substr($ret, 1);

		return($ret);
	}

	function parse_rss() {

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

		require_once('./magpierss/rss_fetch.inc');
          	$url = 'http://developer.berlios.de/export/rss20_bsnews.php?group_id=4806';

          	$rss = fetch_rss($url);

          	if ( $rss and !$rss->ERROR) {

	    		$num_items = 10;
	    		$items = array_slice($rss->items, 0, $num_items);
	    		
			$ret = "<dl>\n";

	    		foreach ($items as $item) {
	      			$title = $item[title];
	      			$link  = $item[link];
	      			$description = $this->make_clickable($item[description]);
	      			$pubDate  = $item[pubdate];
	      			$date = explode(" ", $pubDate);
	      			$ret .= "      <dt>[" . $date[1] . "-" . $months[$date[2]] . "-" . $date[3] . "]";
              			$ret .= " <a href=\"" . $link . "\">" . $title . "</a></dt>\n";
	      			$ret .= "      <dd>" . $description . "</dd>\n";
	    		}

	    		$ret .= "    </dl>\n\n";

          	} else { 
			$ret = "Error: " . $rss->ERROR; 
		}

		return $ret;

	}

}

?>
