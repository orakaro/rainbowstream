import json

from twitter.util import printNicely
from .colors import *
from .config import *


def detail_twitter_error(twitterException):
    """
    Display Twitter Errors nicely
    """
    data = twitterException.response_data
    try:
        for m in data.get('errors', dict()):
            printNicely(yellow(m.get('message')))
    except: 
        printNicely(yellow(data))


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
