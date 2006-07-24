import sys, os, urllib2, codecs

################################################################################
################################################################################

def wget(url, encoding=None, agent=None):
  # u = urllib2.urlopen(url)
  opener = urllib2.build_opener()
  if agent:
    opener.addheaders = [('User-Agent', agent)]
  u = opener.open(url)
  html = u.read()
  u.close()
  if encoding:
    html = codecs.getdecoder(encoding)(html, 'replace')[0]
  return html
  
def wget_flat(url, encoding=None, agent=None):
  return wget(url,encoding,agent).replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
  
