import json

from twitter.util import printNicely
from .colors import *


def detail_twitter_error(twitterException):
    """
    Display Twitter Errors nicely
    """
    try:
        # twitterException.response_data can be byte string on Python 3
        # or nornal dict on Python 2
        loadedJson = json.loads(twitterException.response_data.decode('utf8'))
        for m in loadedJson.get('errors', dict()):
            info = "Error " + str(m.get('code')) + ": " + m.get('message')
            printNicely(yellow(info))
    except:
        info = "Error: " + twitterException.response_data.decode('utf8')
        printNicely(yellow(info))
