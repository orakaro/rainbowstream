import json

from twitter.util import printNicely
from .colors import *
from .config import *


def detail_twitter_error(twitterException):
    """
    Display Twitter Errors nicely
    """
    error_response = twitterException.response_data
    try:
        if isinstance(error_response, bytes):
            error_response = json.loads(error_response.decode('utf-8'))
        elif isinstance(error_response, (str, unicode)):
            error_response = json.loads(error_response)

        for error in error_response.get('errors', {}):
            error_code, message = error.get('code', ''), error.get('message', '')
            info = "Error %s: %s" % (error_code, message)
            printNicely(yellow(info))
    except:
        info = "Error: %r " % twitterException.response_data
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
