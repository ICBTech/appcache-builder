#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
    appcache-builder.py: Builds an appcache manifest by parsing
    the HTML code retrieved from the given URL.
"""
from urlparse import urlparse

__author__ = "Aleksandar Pejic"
__credits__ = ["Aleksandar Pejic"]
__license__ = "New BSD License"
__version__ = "0.1"
__maintaner__ = "Aleksandar Pejic"
__email__ = "aleksandar.pejic@icbtech.rs"
__status__ = "Development"

from BeautifulSoup import BeautifulSoup
import urllib, urllib2, re, sys, datetime

def verify_url(url):
    url_regex = re.compile(
        r'^(?:http)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if not re.findall(url_regex, url):
        print("Error: The provided URL is invalid!")
        sys.exit(1)
    return url

def retrieve_webpage(address):
    try:
        web_handle = urllib2.urlopen(address)
    except urllib2.HTTPError, e:
        print("Cannot retrieve URL: HTTP Error Code ", e.code)
        sys.exit(1)
    except urllib2.URLError, e:
        print("Cannot retrieve URL: " + e.reason[1])
        sys.exit(1)
    except:
        print("Cannot retrieve URL: unknown error")
        sys.exit(1)
    return web_handle

def remove_query_string(url):
    url_parts = ""
    clean_url = ""
    try:
        url_parts = url.split("?")
        clean_url = url_parts[0]
    except:
        clean_url = url
    return clean_url

def get_resources(address):
    resources = []
    soup = BeautifulSoup(retrieve_webpage(address))
    for img in soup.findAll("img"):
        if img.get('src') != None:
            src = unicode.encode(img.get('src'),'utf-8')
            resources.append(urllib.quote(remove_query_string(src)))
    for script in soup.findAll("script"):
        if script.get('src') != None:
            src = unicode.encode(script.get('src'))
            resources.append(urllib.quote(remove_query_string(src)))
    for link in soup.findAll("link"):
        if link.get('href') != None:
            src = unicode.encode(link.get('href'))
            resources.append(urllib.quote(remove_query_string(src)))
    return resources

def verify_resources(resource_list,url):
    cache_items = resource_list
    url_parts = urlparse(url)
    base_url = url_parts.scheme + "://" + url_parts.netloc
    for item in cache_items:
        item_url = ""
        http_code = ""
        if (item[0] == '/'):
            item_url = base_url + item
        else:
            item_url = url + item
        try:
            http_code = urllib.urlopen(item_url).getcode()
        except:
            print("Error: HTTP code %s", http_code)
        finally:
            if (http_code != 200):
                cache_items.remove(item)
    return cache_items


def build_manifest(cache_items):
    manifest = []
    manifest.append("CACHE MANIFEST")
    manifest.append("# " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    manifest.append(" ")
    manifest.append("CACHE:")
    for item in cache_items:
        manifest.append(item)
    manifest.append(" ")
    manifest.append("NETWORK:")
    manifest.append("*")
    return manifest

def write_appcache(content,file):
    try:
        f = open(file,'w')
        for line in content:
            f.write(line + "\n")
        f.close()
    except IOError:
        print("Error: could not write to %s", file)
        sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: %s url output_file" % (sys.argv[0]))
    sys.exit(1)

address = verify_url(sys.argv[1])
manifest_file = sys.argv[2]

cache_candidates = get_resources(address)
cache_items = verify_resources(cache_candidates, address)
manifest_content = build_manifest(cache_items)
write_appcache(manifest_content, manifest_file)

sys.exit(0)