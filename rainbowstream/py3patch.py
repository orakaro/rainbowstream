import sys

# Library compatibility
if sys.version[0] == "2":
    from HTMLParser import HTMLParser
    from urllib2 import URLError
else:
    from html.parser import HTMLParser
    from urllib.error import URLError

unescape = HTMLParser().unescape
# According to https://github.com/python/cpython/blob/master/Lib/html/parser.py#L547 ,
# in python 3.5 maybe I should use
# from html import unescape
# but it is a far-future story:)


# Function compatibility
# xrange, raw_input, map ,unicde
if sys.version[0] == "2":
    lmap = lambda f, a: map(f, a)
    str2u = lambda x: x.decode('utf-8')
    u2str = lambda x: x.encode('utf-8')
else:
    xrange = range
    raw_input = input
    lmap = lambda f, a: list(map(f, a))
    str2u = u2str = lambda x: x
