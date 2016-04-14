"""Scan a URL's contents to find related feeds

This is a compatible replacement for Aaron Swartz's feedfinder module,
using feedparser to check whether the URLs it returns are feeds.

It finds links to feeds within the following elements:
- <link rel="alternate" ...> (standard feed discovery)
- <a ...>, if the href contains words that suggest it might be a feed

It orders feeds using a quality heuristic: the first result is the most
likely to be a feed for the given URL.

Required: Python 2.4 or later, feedparser
"""

__license__ = """
Copyright (c) 2008 Decklin Foster <decklin@red-bean.com>
Copyright (c) 2013, 2015 Adam Sampson <ats@offog.org>

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that
the above copyright notice and this permission notice appear in all
copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

import cStringIO
import feedparser
import gzip
import re
import urllib2
import urlparse
import HTMLParser

def is_feed(url):
    """Return true if feedparser can understand the given URL as a feed."""

    p = feedparser.parse(url)
    version = p.get("version")
    if version is None:
        version = ""
    return version != ""

def fetch_url(url):
    """Fetch the given URL and return the data from it as a Unicode string."""

    request = urllib2.Request(url)
    request.add_header("Accept-Encoding", "gzip")

    f = urllib2.urlopen(request)
    headers = f.info()
    data = f.read()
    f.close()

    # We have to support gzip encoding because some servers will use it
    # even if you explicitly refuse it in Accept-Encoding.
    encodings = headers.get("Content-Encoding", "")
    encodings = [s.strip() for s in encodings.split(",")]
    if "gzip" in encodings:
        f = gzip.GzipFile(fileobj=cStringIO.StringIO(data))
        data = f.read()
        f.close()

    # Silently ignore encoding errors -- we don't need to go to the bother of
    # detecting the encoding properly (like feedparser does).
    data = data.decode("UTF-8", "ignore")

    return data

class FeedFinder(HTMLParser.HTMLParser):
    def __init__(self, base_uri):
        HTMLParser.HTMLParser.__init__(self)
        self.found = []
        self.count = 0
        self.base_uri = base_uri

    def add(self, score, href):
        url = urlparse.urljoin(self.base_uri, href)
        lower = url.lower()

        # Some sites provide feeds both for entries and comments;
        # prefer the former.
        if lower.find("comment") != -1:
            score -= 50

        # Prefer Atom, then RSS, then RDF (RSS 1).
        if lower.find("atom") != -1:
            score += 10
        elif lower.find("rss2") != -1:
            score -= 5
        elif lower.find("rss") != -1:
            score -= 10
        elif lower.find("rdf") != -1:
            score -= 15

        self.found.append((-score, self.count, url))
        self.count += 1

    def urls(self):
        return [link[2] for link in sorted(self.found)]

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        href = attrs.get('href')
        if href is None:
            return
        if tag == 'link' and attrs.get('rel') == 'alternate' and \
                not attrs.get('type') == 'text/html':
            self.add(200, href)
        if tag == 'a' and re.search(r'\b(rss|atom|rdf|feeds?)\b', href, re.I):
            self.add(100, href)

def feeds(page_url):
    """Search the given URL for possible feeds, returning a list of them."""

    # If the URL is a feed, there's no need to scan it for links.
    if is_feed(page_url):
        return [page_url]

    data = fetch_url(page_url)
    parser = FeedFinder(page_url)
    try:
        parser.feed(data)
    except HTMLParser.HTMLParseError:
        pass
    found = parser.urls()

    # Return only feeds that feedparser can understand.
    return [feed for feed in found if is_feed(feed)]
