#!/usr/bin/python

import sys
import os
import os.path
import re
import urllib2
import simplejson
from optparse import OptionParser

class YTMND:

  def __init__ (self):
    self.media_only = False
    self.no_web_audio = False
    self.json = False

  def fetch_user(self, user):
    if user == "":
      print("expecting one ytmnd name, got "+str(sys.argv))
      return

    # Get the url of the sound and foreground
    ytmnd_name = user 
    ytmnd_html = urllib2.urlopen("http://ytmnd.com/users/" + ytmnd_name + "/sites").readlines()
    
    domains = []
    
    for line in ytmnd_html:
      if 'profile_link' in line:
      
        expr = r"site_link\" href=\"http://(\S+).ytmn(d|sfw)?.com\""
        domain = re.search(expr,line).group(1)
        domains.append(domain)

    print ">> found %d domains" % len( domains )
    os.system("mkdir -p %s" % user)
    os.chdir(user)
    if not self.no_web_audio:
      self.copy_ytmnd_js()
    for domain in domains:
      ytmnd.fetch_ytmnd( domain )
    os.chdir("..")

  def fetch_ytmnd(self, domain):

    if domain == "":
      print("expecting one ytmnd name, got "+str(sys.argv))
      return

    print "fetching %s" % domain

    # Get the url of the sound and foreground
    ytmnd_name = domain
    ytmnd_html = urllib2.urlopen("http://" + domain + ".ytmnd.com").read()
    expr = r"ytmnd.site_id = (\d+);"
    ytmnd_id = re.search(expr,ytmnd_html).group(1)
    ytmnd_info = simplejson.load(urllib2.urlopen("http://" + domain + ".ytmnd.com/info/" + ytmnd_id + "/json"))

    if ytmnd.json:
      print simplejson.dumps(ytmnd_info, sort_keys=True, indent=4 * ' ')
      # ytmnd.write_json(ytmnd_info)
    else:
      ytmnd.fetch_media(ytmnd_info)
      if not ytmnd.media_only:
        ytmnd.write_index(ytmnd_info)

  def fetch_media(self, ytmnd_info):
    # Assign full url names for the sound and foreground
    domain = ytmnd_info['site']['domain']
    original_gif = ytmnd_info['site']['foreground']['url']
    gif_type = original_gif.split(".")[-1]
    original_wav = ytmnd_info['site']['sound']['url']
    wav_type = ytmnd_info['site']['sound']['type']
    
    if 'alternates' in ytmnd_info['site']['sound']:
      key = ytmnd_info['site']['sound']['alternates'].keys()[0]
      value = ytmnd_info['site']['sound']['alternates'][key]
      if value['file_type'] != 'swf':
        original_wav = value['file_url']
        wav_type = ytmnd_info['site']['sound']['file_type']

    # download files
    os.system("wget --quiet -O %s %s" % (domain + "." + gif_type, original_gif))
    os.system("wget --quiet -O %s %s" % (domain + "." + wav_type, original_wav))

  def write_index(self, ytmnd_info):
  
    # print simplejson.dumps(ytmnd_info)
    domain = ytmnd_info['site']['domain']
    bgcolor = ytmnd_info['site']['background']['color']
    title = ytmnd_info['site']['description']
    placement = ytmnd_info['site']['foreground']['placement']

    original_gif = ytmnd_info['site']['foreground']['url']
    gif_type = original_gif.split(".")[-1]
    wav_type = ytmnd_info['site']['sound']['type']
    
    if 'alternates' in ytmnd_info['site']['sound']:
      key = ytmnd_info['site']['sound']['alternates'].keys()[0]
      value = ytmnd_info['site']['sound']['alternates'][key]
      if value['file_type'] != 'swf':
        original_wav = value['file_url']
        wav_type = ytmnd_info['site']['sound']['file_type']

    fn = open(domain + ".html", 'w')
    fn.write("<html>\n")
    fn.write("<head>\n")
    fn.write("<title>%s</title>\n" % title)
    fn.write("<style>\n")
    fn.write("*{margin:0;padding:0;width:100%;height:100%;}\n")
    fn.write("body{background-color:%s;" % bgcolor)
    fn.write("background-image:url(%s.%s);" % (domain, gif_type))
    if placement == "mc":
      fn.write("background-position: center center; background-repeat: no-repeat;}")
    elif placement == "tile":
      fn.write("background-position: top left; background-repeat: repeat;}")
    fn.write("\n")
    fn.write("</style>\n")
    fn.write("</head>\n")

    if self.no_web_audio:
      fn.write("<body><audio src=%s.mp3 loop autoplay></body>" % domain)
    else:
      fn.write("<body></body>\n")
      fn.write("<script>var url = '%s.%s'</script>\n" % (domain, wav_type))
      fn.write("<script src='ytmnd.js'></script>\n")
      fn.write("<script type='application/json'>\n")
      fn.write(simplejson.dumps(ytmnd_info, sort_keys=True, indent=4 * ' ') + "\n")
      fn.write("</script>\n")
    fn.write("</html>")

    fn.close()
  
  def copy_ytmnd_js (self):
    if not os.path.isfile("ytmnd.js"):
      os.system("cp ../ytmnd.js .")

  def write_json (self, ytmnd_info):
    domain = ytmnd_info['site']['domain']

    fn = open(domain + '.json', 'w')
    fn.write( simplejson.dumps(ytmnd_info) )
    fn.close()

if __name__ == '__main__':

  parser = OptionParser()

  parser.add_option("-u", "--user", action="store_true")
  parser.add_option("--media-only", action="store_true")
  parser.add_option("--no-web-audio", action="store_true")
  parser.add_option("-j", "--json", action="store_true")

  (options, args) = parser.parse_args()

  if len(args) == 0:
    print "usage: ./ytmnd.py [-u username] [--media-only] [--no-web-audio] [--json] [domain]"
    sys.exit(1)
  
  ytmnd = YTMND ()
  ytmnd.media_only = options.media_only
  ytmnd.no_web_audio = options.no_web_audio
  ytmnd.json = options.json

  if options.user:
    user = args[0]
    ytmnd.fetch_user( user )

  else:
    name = args[0].replace("http://","").replace(".ytmnsfw.com","").replace(".ytmnd.com","").replace("/","")
    ytmnd.fetch_ytmnd( name )
