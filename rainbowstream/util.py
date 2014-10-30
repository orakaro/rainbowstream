import json

from twitter.util import printNicely
from .colors import *
from .config import *


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


def format_prefix(listname='', keyword=''):
    """
    Format the custom prefix
    """
    formattedPrefix = c['PREFIX']
    owner = '@' + c['original_name']
    place = ''
    # Public stream
    if keyword:
        formattedPrefix = ''.join(formattedPrefix.split('#owner'))
        formattedPrefix = ''.join(formattedPrefix.split('#place'))
        formattedPrefix = ''.join(formattedPrefix.split('#me'))
    # List stream
    elif listname:
        formattedPrefix = ''.join(formattedPrefix.split('#keyword'))
        formattedPrefix = ''.join(formattedPrefix.split('#me'))
        owner, place = listname.split('/')
        place = '/' + place
    # Personal stream
    else:
        formattedPrefix = ''.join(formattedPrefix.split('#keyword'))
        formattedPrefix = ''.join(formattedPrefix.split('#owner'))
        formattedPrefix = ''.join(formattedPrefix.split('#place'))

    formattedPrefix = formattedPrefix.replace('#owner', owner)
    formattedPrefix = formattedPrefix.replace('#place', place)
    formattedPrefix = formattedPrefix.replace('#keyword', keyword)
    formattedPrefix = formattedPrefix.replace('#me', '@' + c['original_name'])

    return formattedPrefix
