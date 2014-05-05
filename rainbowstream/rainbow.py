"""
Colorful user's timeline stream
"""

from __future__ import print_function

import os, os.path, argparse, random

from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from twitter.oauth import OAuth, read_token_file
from twitter.util import printNicely
from dateutil import parser
from pyfiglet import figlet_format

from colors import *
from config import *

def asciiart():
    """
    Draw the Ascii Art
    """
    d = [red, green, yellow, blue, magenta, cyan, white]
    fi = figlet_format('Rainbow Stream', font='doom')
    print('\n'.join(
            [random.choice(d)(i) for i in fi.split('\n')]
        )
    )


def draw(t):
    """
    Draw the rainbow
    """
    # Retrieve tweet
    text = t['text']
    screen_name = t['user']['screen_name']
    name = t['user']['name']
    created_at = t['created_at']
    date = parser.parse(created_at)
    time = date.strftime('%Y/%m/%d %H:%M:%S')

    # Format info
    user = green(name) + ' ' + yellow('@' + screen_name) + ' '
    clock = magenta('['+ time + ']')
    tweet = white(text)

    # Draw rainbow
    terminalrows, terminalcolumns = os.popen('stty size', 'r').read().split()
    line1 = u"{u:>{uw}}:".format(
        u = user,
        uw = len(user) + 2,
    )
    line2 = u"{c:>{cw}}".format(
        c = clock,
        cw = len(clock) + 2,
    )
    line3 = '  ' + tweet
    line4 = '\n'

    return line1, line2, line3, line4


def parse_arguments():
    """
    Parse the arguments
    """

    parser = argparse.ArgumentParser(description=__doc__ or "")

    parser.add_argument('-to', '--timeout', help='Timeout for the stream (seconds).')
    parser.add_argument('-ht', '--heartbeat-timeout', help='Set heartbeat timeout.', default=90)
    parser.add_argument('-nb', '--no-block', action='store_true', help='Set stream to non-blocking.')
    parser.add_argument('-tt', '--track-keywords', help='Search the stream for specific text.')
    return parser.parse_args()


def main():
    args = parse_arguments()

    # The Logo
    asciiart()

    # When using twitter stream you must authorize.
    oauth_filename = os.environ.get('HOME', os.environ.get('USERPROFILE', '')) + os.sep + '.twitter_oauth'
    oauth_token, oauth_token_secret = read_token_file(oauth_filename)
    auth = OAuth(oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET)

    # These arguments are optional:
    stream_args = dict(
        timeout=args.timeout,
        block=not args.no_block,
        heartbeat_timeout=args.heartbeat_timeout)

    # Track keyword
    query_args = dict()
    if args.track_keywords:
        query_args['track'] = args.track_keywords

    # Get stream
    stream = TwitterStream(auth=auth, domain='userstream.twitter.com', **stream_args)
    tweet_iter = stream.user(**query_args)

    # Iterate over the sample stream.
    for tweet in tweet_iter:
        if tweet is None:
            printNicely("-- None --")
        elif tweet is Timeout:
            printNicely("-- Timeout --")
        elif tweet is HeartbeatTimeout:
            printNicely("-- Heartbeat Timeout --")
        elif tweet is Hangup:
            printNicely("-- Hangup --")
        elif tweet.get('text'):
            line1, line2, line3, line4 = draw(t = tweet)
            printNicely(line1)
            printNicely(line2)
            printNicely(line3)
            printNicely(line4)

if __name__ == '__main__':
    main()
