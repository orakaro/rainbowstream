import json

from twitter.util import printNicely
from .colors import *


def detail_twitter_error(twitterException):
    """
    Display Twitter Errors nicely
    """
    try:
        loadedJson = json.loads(twitterException.response_data)
        for m in loadedJson.get('errors', dict()):
            info = "Error " + str(m.get('code')) + ": " + m.get('message')
            printNicely(yellow(info))
    except ValueError:
        info = "Error: " + twitterException.response_data
        printNicely(yellow(info))
