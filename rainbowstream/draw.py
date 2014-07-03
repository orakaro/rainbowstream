"""
Draw
"""
import requests
import datetime
import time

from twitter.util import printNicely
from StringIO import StringIO
from dateutil import parser
from .c_image import *
from .colors import *
from .config import *
from .db import *

db = RainbowDB()
cur_theme = None

def check_theme():
    """
    Check current theme and update if necessary
    """
    exists = db.theme_query()
    themes = [t.theme_name for t in exists]
    if cur_theme != themes[0]:
        cur_theme = themes[0]
        # Determine path
        if cur_theme == 'user':
            config = os.environ.get(
                'HOME',
                os.environ.get(
                'USERPROFILE',
                '')) + os.sep + '.rainbow_config.json'
        else:
            config = 'rainbowstream/colorset/'+cur_theme+'.json'
        # Load new config
        data = load_config(config)
        if data:
            for d in data:
                c[d] = data[d]


def color_func(func_name):
    """
    Call color function base on name
    """
    pure = func_name.encode('utf8')
    if pure.startswith('RGB_') and pure[4:].isdigit():
        return RGB(int(pure[4:]))
    return globals()[pure]


def draw(t, iot=False, keyword=None, fil=[], ig=[]):
    """
    Draw the rainbow
    """

    check_theme()
    # Retrieve tweet
    tid = t['id']
    text = t['text']
    screen_name = t['user']['screen_name']
    name = t['user']['name']
    created_at = t['created_at']
    favorited = t['favorited']
    date = parser.parse(created_at)
    date = date - datetime.timedelta(seconds=time.timezone)
    clock = date.strftime('%Y/%m/%d %H:%M:%S')

    # Get expanded url
    try:
        expanded_url = []
        url = []
        urls = t['entities']['urls']
        for u in urls:
            expanded_url.append(u['expanded_url'])
            url.append(u['url'])
    except:
        expanded_url = None
        url = None

    # Get media
    try:
        media_url = []
        media = t['entities']['media']
        for m in media:
            media_url.append(m['media_url'])
    except:
        media_url = None

    # Filter and ignore
    screen_name = '@' + screen_name
    if fil and screen_name not in fil:
        return
    if ig and screen_name in ig:
        return

    # Get rainbow id
    res = db.tweet_to_rainbow_query(tid)
    if not res:
        db.tweet_store(tid)
        res = db.tweet_to_rainbow_query(tid)
    rid = res[0].rainbow_id

    # Format info
    user = cycle_color(
        name) + color_func(c['TWEET']['nick'])(' ' + screen_name + ' ')
    meta = color_func(c['TWEET']['clock'])(
        '[' + clock + '] ') + color_func(c['TWEET']['id'])('[id=' + str(rid) + '] ')
    if favorited:
        meta = meta + color_func(c['TWEET']['favorite'])(u'\u2605')
    tweet = text.split()
    # Replace url
    if expanded_url:
        for index in range(len(expanded_url)):
            tweet = map(
                lambda x: expanded_url[index] if x == url[index] else x,
                tweet)
    # Highlight RT
    tweet = map(
        lambda x: color_func(
            c['TWEET']['rt'])(x) if x == 'RT' else x,
        tweet)
    # Highlight screen_name
    tweet = map(lambda x: cycle_color(x) if x[0] == '@' else x, tweet)
    # Highlight link
    tweet = map(
        lambda x: color_func(
            c['TWEET']['link'])(x) if x[
            0:4] == 'http' else x,
        tweet)
    # Highlight search keyword
    if keyword:
        tweet = map(
            lambda x: color_func(c['TWEET']['keyword'])(x) if
            ''.join(c for c in x if c.isalnum()).lower() == keyword.lower()
            else x,
            tweet
        )
    # Recreate tweet
    tweet = ' '.join(tweet)

    # Draw rainbow
    line1 = u"{u:>{uw}}:".format(
        u=user,
        uw=len(user) + 2,
    )
    line2 = u"{c:>{cw}}".format(
        c=meta,
        cw=len(meta) + 2,
    )
    line3 = '  ' + tweet

    printNicely('')
    printNicely(line1)
    printNicely(line2)
    printNicely(line3)

    # Display Image
    if iot and media_url:
        for mu in media_url:
            response = requests.get(mu)
            image_to_display(StringIO(response.content))


def print_message(m):
    """
    Print direct message
    """
    sender_screen_name = '@' + m['sender_screen_name']
    sender_name = m['sender']['name']
    text = m['text']
    recipient_screen_name = '@' + m['recipient_screen_name']
    recipient_name = m['recipient']['name']
    mid = m['id']
    date = parser.parse(m['created_at'])
    date = date - datetime.timedelta(seconds=time.timezone)
    clock = date.strftime('%Y/%m/%d %H:%M:%S')

    # Get rainbow id
    res = db.message_to_rainbow_query(mid)
    if not res:
        db.message_store(mid)
        res = db.message_to_rainbow_query(mid)
    rid = res[0].rainbow_id

    # Draw
    sender = cycle_color(
        sender_name) + color_func(c['MESSAGE']['sender'])(' ' + sender_screen_name + ' ')
    recipient = cycle_color(recipient_name) + color_func(
        c['MESSAGE']['recipient'])(
        ' ' + recipient_screen_name + ' ')
    user = sender + color_func(c['MESSAGE']['to'])(' >>> ') + recipient
    meta = color_func(
        c['MESSAGE']['clock'])(
        '[' + clock + ']') + color_func(
            c['MESSAGE']['id'])(
                ' [message_id=' + str(rid) + '] ')
    text = ''.join(map(lambda x: x + '  ' if x == '\n' else x, text))

    line1 = u"{u:>{uw}}:".format(
        u=user,
        uw=len(user) + 2,
    )
    line2 = u"{c:>{cw}}".format(
        c=meta,
        cw=len(meta) + 2,
    )

    line3 = '  ' + text

    printNicely('')
    printNicely(line1)
    printNicely(line2)
    printNicely(line3)


def show_profile(u, iot=False):
    """
    Show a profile
    """
    # Retrieve info
    name = u['name']
    screen_name = u['screen_name']
    description = u['description']
    profile_image_url = u['profile_image_url']
    location = u['location']
    url = u['url']
    created_at = u['created_at']
    statuses_count = u['statuses_count']
    friends_count = u['friends_count']
    followers_count = u['followers_count']

    # Create content
    statuses_count = color_func(
        c['PROFILE']['statuses_count'])(
        str(statuses_count) +
        ' tweets')
    friends_count = color_func(
        c['PROFILE']['friends_count'])(
        str(friends_count) +
        ' following')
    followers_count = color_func(
        c['PROFILE']['followers_count'])(
        str(followers_count) +
        ' followers')
    count = statuses_count + '  ' + friends_count + '  ' + followers_count
    user = cycle_color(
        name) + color_func(c['PROFILE']['nick'])(' @' + screen_name + ' : ') + count
    profile_image_raw_url = 'Profile photo: ' + \
        color_func(c['PROFILE']['profile_image_url'])(profile_image_url)
    description = ''.join(
        map(lambda x: x + ' ' * 4 if x == '\n' else x, description))
    description = color_func(c['PROFILE']['description'])(description)
    location = 'Location : ' + color_func(c['PROFILE']['location'])(location)
    url = 'URL : ' + (color_func(c['PROFILE']['url'])(url) if url else '')
    date = parser.parse(created_at)
    date = date - datetime.timedelta(seconds=time.timezone)
    clock = date.strftime('%Y/%m/%d %H:%M:%S')
    clock = 'Join at ' + color_func(c['PROFILE']['clock'])(clock)

    # Format
    line1 = u"{u:>{uw}}".format(
        u=user,
        uw=len(user) + 2,
    )
    line2 = u"{p:>{pw}}".format(
        p=profile_image_raw_url,
        pw=len(profile_image_raw_url) + 4,
    )
    line3 = u"{d:>{dw}}".format(
        d=description,
        dw=len(description) + 4,
    )
    line4 = u"{l:>{lw}}".format(
        l=location,
        lw=len(location) + 4,
    )
    line5 = u"{u:>{uw}}".format(
        u=url,
        uw=len(url) + 4,
    )
    line6 = u"{c:>{cw}}".format(
        c=clock,
        cw=len(clock) + 4,
    )

    # Display
    printNicely('')
    printNicely(line1)
    if iot:
        response = requests.get(profile_image_url)
        image_to_display(StringIO(response.content), 2, 20)
    else:
        printNicely(line2)
    for line in [line3, line4, line5, line6]:
        printNicely(line)
    printNicely('')


def print_trends(trends):
    """
    Display topics
    """
    for topic in trends[:c['TREND_MAX']]:
        name = topic['name']
        url = topic['url']
        line = cycle_color(name) + ': ' + color_func(c['TREND']['url'])(url)
        printNicely(line)
    printNicely('')
