"""
Colorful user's timeline stream
"""

from __future__ import print_function
from multiprocessing import Process

import os, os.path, argparse, sys, time

from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from twitter.api import *
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.util import printNicely
from dateutil import parser

from .colors import *
from .config import *

auth_obj = {}

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
    user = cycle_color(name) + grey(' ' + '@' + screen_name + ' ')
    clock = grey('[' + time + ']')
    tweet = text.split()
    tweet = map(lambda x: grey(x) if x == 'RT' else x, tweet)
    tweet = map(lambda x: cycle_color(x) if x[0] == '@' else x, tweet)
    tweet = map(lambda x: cyan(x) if x[0:7] == 'http://' else x, tweet)
    tweet = ' '.join(tweet)

    # Draw rainbow
    line1 = u"{u:>{uw}}:".format(
        u=user,
        uw=len(user) + 2,
    )
    line2 = u"{c:>{cw}}".format(
        c=clock,
        cw=len(clock) + 2,
    )
    line3 = '  ' + tweet
    line4 = '\n'

    return line1, line2, line3, line4


def parse_arguments():
    """
    Parse the arguments
    """

    parser = argparse.ArgumentParser(description=__doc__ or "")

    parser.add_argument(
        '-to',
        '--timeout',
        help='Timeout for the stream (seconds).')
    parser.add_argument(
        '-ht',
        '--heartbeat-timeout',
        help='Set heartbeat timeout.',
        default=90)
    parser.add_argument(
        '-nb',
        '--no-block',
        action='store_true',
        help='Set stream to non-blocking.')
    parser.add_argument(
        '-tt',
        '--track-keywords',
        help='Search the stream for specific text.')
    return parser.parse_args()


def authen():
    """
    authenticate with Twitter OAuth
    """
    # When using rainbow stream you must authorize.
    twitter_credential = os.environ.get(
        'HOME',
        os.environ.get(
            'USERPROFILE',
            '')) + os.sep + '.rainbow_oauth'
    if not os.path.exists(twitter_credential):
        oauth_dance("Rainbow Stream",
                    CONSUMER_KEY,
                    CONSUMER_SECRET,
                    twitter_credential)
    oauth_token, oauth_token_secret = read_token_file(twitter_credential)
    return OAuth(
        oauth_token,
        oauth_token_secret,
        CONSUMER_KEY,
        CONSUMER_SECRET)


def get_decorated_name():
    """
    Beginning of every line
    """
    t = Twitter(auth=authen())
    name = '@' + t.statuses.user_timeline()[-1]['user']['screen_name']
    auth_obj['decorated_name'] = grey('[') + grey(name) + grey(']: ')

def tweet(stuff):
    """
    Authen and tweet
    """
    t = Twitter(auth=authen())
    t.statuses.update(status=stuff)


def listen(stdin):
    """
    Listen to user's input
    """
    for line in iter(stdin.readline, ''):
        # Public tweet
        if line.startswith('!'):
            tweet(line[1:])
        else:
            sys.stdout.write(auth_obj['decorated_name'])
    stdin.close()


def stream():
    """
    Ouput the stream
    """
    args = parse_arguments()

    # The Logo
    ascii_art()
    print("Tip: Press ENTER and put a '!' in the beginning to start composing a new tweet")
    print('\n')
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
    stream = TwitterStream(
        auth = authen(),
        domain = 'userstream.twitter.com',
        **stream_args)
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
            line1, line2, line3, line4 = draw(t=tweet)
            printNicely(line1)
            printNicely(line2)
            printNicely(line3)
            printNicely(line4)


def fly():
    """
    Main function
    """
    get_decorated_name()
    p = Process(target = stream)
    p.start()
    listen(sys.stdin)

