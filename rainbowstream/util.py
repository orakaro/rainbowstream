import json

from twitter.util import printNicely
from .colors import *


def printTwitterErrors(twitterException):
    """
    Display Twitter Errors nicely
    """
    try:
        loadedJson = json.loads(twitterException.response_data)
        for m in loadedJson.get('errors', dict()):
            printNicely(
                magenta("Error " + str(m.get('code')) + ": " + m.get('message')))
    except ValueError:
        printNicely(magenta("Error: " + twitterException.response_data))
