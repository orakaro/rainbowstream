import json
import shutil
import platform
import os

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


def get_terminal_size():
    if platform.system() == 'Windows':
        return shutil.get_terminal_size()
    else:
        return os.popen('stty size', 'r').read().split()


def add_tweetmode_parameter(kwargs):
    """
    Add support for extended mode to Twitter API calls unless explicitly stated in config
    """
    if not c.get('DISABLE_EXTENDED_TWEETS'):
        kwargs['tweet_mode'] = 'extended'
    return kwargs
