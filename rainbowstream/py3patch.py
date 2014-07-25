"""
  Python 3 supports
"""
import sys

# StringIO module
try:
    from StringIO import StringIO, BytesIO
except:
    from io import StringIO, BytesIO

# HTMLParser module
try:
    from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape
except:
    from html import unescape

# raw_input and map function behaviour
if sys.version[0] == "3":
    raw_input = input
    lmap = lambda f, a: list(map(f, a))
else:
    lmap = lambda f, a: map(f, a)
