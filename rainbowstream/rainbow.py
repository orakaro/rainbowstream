"""
Colorful user's timeline stream
"""
from multiprocessing import Process

import os
import os.path
import sys
import signal
import argparse
import time
import requests

from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from twitter.api import *
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.util import printNicely
from StringIO import StringIO

from .draw import *
from .colors import *
from .config import *
from .consumer import *
from .interactive import *
from .db import *
from .c_image import *

g = {}
db = RainbowDB()
cmdset = [
    'switch',
    'trend',
    'home',
    'view',
    'mentions',
    't',
    'rt',
    'allrt',
    'fav',
    'rep',
    'del',
    'ufav',
    's',
    'mes',
    'show',
    'ls',
    'inbox',
    'sent',
    'trash',
    'whois',
    'fl',
    'ufl',
    'mute',
    'unmute',
    'muting',
    'block',
    'unblock',
    'report',
    'cal',
    'theme',
    'h',
    'c',
    'q'
]


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
    parser.add_argument(
        '-fil',
        '--filter',
        help='Filter specific screen_name.')
    parser.add_argument(
        '-ig',
        '--ignore',
        help='Ignore specific screen_name.')
    parser.add_argument(
        '-iot',
        '--image-on-term',
        action='store_true',
        help='Display all image on terminal.')
    return parser.parse_args()


def authen():
    """
    Authenticate with Twitter OAuth
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
    name = '@' + t.account.verify_credentials()['screen_name']
    g['original_name'] = name[1:]
    g['decorated_name'] = color_func(c['DECORATED_NAME'])('[' + name + ']: ')
    g['ascii_art'] = True

    files = os.listdir('rainbowstream/colorset')
    themes = [f.split('.')[0] for f in files if f.split('.')[-1] == 'json']
    themes += ['user']
    g['themes'] = themes


def switch():
    """
    Switch stream
    """
    try:
        target = g['stuff'].split()[0]

        # Filter and ignore
        args = parse_arguments()
        try:
            if g['stuff'].split()[-1] == '-f':
                only = raw_input('Only nicks: ')
                ignore = raw_input('Ignore nicks: ')
                args.filter = filter(None, only.split(','))
                args.ignore = filter(None, ignore.split(','))
            elif g['stuff'].split()[-1] == '-d':
                args.filter = c['ONLY_LIST']
                args.ignore = c['IGNORE_LIST']
        except:
            printNicely(red('Sorry, wrong format.'))
            return

        # Public stream
        if target == 'public':
            keyword = g['stuff'].split()[1]
            if keyword[0] == '#':
                keyword = keyword[1:]
            # Kill old process
            os.kill(g['stream_pid'], signal.SIGKILL)
            args.track_keywords = keyword
            # Start new process
            p = Process(
                target=stream,
                args=(
                    c['PUBLIC_DOMAIN'],
                    args))
            p.start()
            g['stream_pid'] = p.pid

        # Personal stream
        elif target == 'mine':
            # Kill old process
            os.kill(g['stream_pid'], signal.SIGKILL)
            # Start new process
            p = Process(
                target=stream,
                args=(
                    c['USER_DOMAIN'],
                    args,
                    g['original_name']))
            p.start()
            g['stream_pid'] = p.pid
        printNicely('')
        if args.filter:
            printNicely(cyan('Only: ' + str(args.filter)))
        if args.ignore:
            printNicely(red('Ignore: ' + str(args.ignore)))
        printNicely('')
        g['ascii_art'] = True
    except:
        printNicely(red('Sorry I can\'t understand.'))


def trend():
    """
    Trend
    """
    t = Twitter(auth=authen())
    # Get country and town
    try:
        country = g['stuff'].split()[0]
    except:
        country = ''
    try:
        town = g['stuff'].split()[1]
    except:
        town = ''

    avail = t.trends.available()
    # World wide
    if not country:
        trends = t.trends.place(_id=1)[0]['trends']
        print_trends(trends)
    else:
        for location in avail:
            # Search for country and Town
            if town:
                if location['countryCode'] == country \
                        and location['placeType']['name'] == 'Town' \
                        and location['name'] == town:
                    trends = t.trends.place(_id=location['woeid'])[0]['trends']
                    print_trends(trends)
            # Search for country only
            else:
                if location['countryCode'] == country \
                        and location['placeType']['name'] == 'Country':
                    trends = t.trends.place(_id=location['woeid'])[0]['trends']
                    print_trends(trends)


def home():
    """
    Home
    """
    t = Twitter(auth=authen())
    num = c['HOME_TWEET_NUM']
    if g['stuff'].isdigit():
        num = int(g['stuff'])
    for tweet in reversed(t.statuses.home_timeline(count=num)):
        draw(t=tweet, iot=g['iot'])
    printNicely('')


def view():
    """
    Friend view
    """
    t = Twitter(auth=authen())
    user = g['stuff'].split()[0]
    if user[0] == '@':
        try:
            num = int(g['stuff'].split()[1])
        except:
            num = c['HOME_TWEET_NUM']
        for tweet in reversed(t.statuses.user_timeline(count=num, screen_name=user[1:])):
            draw(t=tweet, iot=g['iot'])
        printNicely('')
    else:
        printNicely(red('A name should begin with a \'@\''))


def mentions():
    """
    Mentions timeline
    """
    t = Twitter(auth=authen())
    num = c['HOME_TWEET_NUM']
    if g['stuff'].isdigit():
        num = int(g['stuff'])
    for tweet in reversed(t.statuses.mentions_timeline(count=num)):
        draw(t=tweet, iot=g['iot'])
    printNicely('')


def tweet():
    """
    Tweet
    """
    t = Twitter(auth=authen())
    t.statuses.update(status=g['stuff'])


def retweet():
    """
    ReTweet
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = db.rainbow_to_tweet_query(id)[0].tweet_id
    t.statuses.retweet(id=tid, include_entities=False, trim_user=True)


def allretweet():
    """
    List all retweet
    """
    t = Twitter(auth=authen())
    # Get rainbow id
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = db.rainbow_to_tweet_query(id)[0].tweet_id
    # Get display num if exist
    try:
        num = int(g['stuff'].split()[1])
    except:
        num = c['RETWEETS_SHOW_NUM']
    # Get result and display
    rt_ary = t.statuses.retweets(id=tid, count=num)
    if not rt_ary:
        printNicely(magenta('This tweet has no retweet.'))
        return
    for tweet in reversed(rt_ary):
        draw(t=tweet, iot=g['iot'])
    printNicely('')


def favorite():
    """
    Favorite
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = db.rainbow_to_tweet_query(id)[0].tweet_id
    t.favorites.create(_id=tid, include_entities=False)
    printNicely(green('Favorited.'))
    draw(t.statuses.show(id=tid), iot=g['iot'])
    printNicely('')


def reply():
    """
    Reply
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = db.rainbow_to_tweet_query(id)[0].tweet_id
    user = t.statuses.show(id=tid)['user']['screen_name']
    status = ' '.join(g['stuff'].split()[1:])
    status = '@' + user + ' ' + status.decode('utf-8')
    t.statuses.update(status=status, in_reply_to_status_id=tid)


def delete():
    """
    Delete
    """
    t = Twitter(auth=authen())
    try:
        rid = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = db.rainbow_to_tweet_query(rid)[0].tweet_id
    t.statuses.destroy(id=tid)
    printNicely(green('Okay it\'s gone.'))


def unfavorite():
    """
    Unfavorite
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = db.rainbow_to_tweet_query(id)[0].tweet_id
    t.favorites.destroy(_id=tid)
    printNicely(green('Okay it\'s unfavorited.'))
    draw(t.statuses.show(id=tid), iot=g['iot'])
    printNicely('')


def search():
    """
    Search
    """
    t = Twitter(auth=authen())
    if g['stuff'].startswith('#'):
        rel = t.search.tweets(q=g['stuff'])['statuses']
        if rel:
            printNicely('Newest tweets:')
            for i in reversed(xrange(c['SEARCH_MAX_RECORD'])):
                draw(t=rel[i],
                     iot=g['iot'],
                     keyword=g['stuff'].strip()[1:])
            printNicely('')
        else:
            printNicely(magenta('I\'m afraid there is no result'))
    else:
        printNicely(red('A keyword should be a hashtag (like \'#AKB48\')'))


def message():
    """
    Send a direct message
    """
    t = Twitter(auth=authen())
    user = g['stuff'].split()[0]
    if user[0].startswith('@'):
        try:
            content = g['stuff'].split()[1]
        except:
            printNicely(red('Sorry I can\'t understand.'))
        t.direct_messages.new(
            screen_name=user[1:],
            text=content
        )
        printNicely(green('Message sent.'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def show():
    """
    Show image
    """
    t = Twitter(auth=authen())
    try:
        target = g['stuff'].split()[0]
        if target != 'image':
            return
        id = int(g['stuff'].split()[1])
        tid = db.rainbow_to_tweet_query(id)[0].tweet_id
        tweet = t.statuses.show(id=tid)
        media = tweet['entities']['media']
        for m in media:
            res = requests.get(m['media_url'])
            img = Image.open(StringIO(res.content))
            img.show()
    except:
        printNicely(red('Sorry I can\'t show this image.'))


def list():
    """
    List friends for followers
    """
    t = Twitter(auth=authen())
    # Get name
    try:
        name = g['stuff'].split()[1]
        if name.startswith('@'):
            name = name[1:]
        else:
            printNicely(red('A name should begin with a \'@\''))
            raise Exception('Invalid name')
    except:
        name = g['original_name']
    # Get list followers or friends
    try:
        target = g['stuff'].split()[0]
    except:
        printNicely(red('Omg some syntax is wrong.'))
    # Init cursor
    d = {'fl': 'followers', 'fr': 'friends'}
    next_cursor = -1
    rel = {}
    # Cursor loop
    while next_cursor != 0:
        list = getattr(t, d[target]).list(
            screen_name=name,
            cursor=next_cursor,
            skip_status=True,
            include_entities=False,
        )
        for u in list['users']:
            rel[u['name']] = '@' + u['screen_name']
        next_cursor = list['next_cursor']
    # Print out result
    printNicely('All: ' + str(len(rel)) + ' people.')
    for name in rel:
        user = '  ' + cycle_color(name) + grey(' ' + rel[name] + ' ')
        printNicely(user)


def inbox():
    """
    Inbox direct messages
    """
    t = Twitter(auth=authen())
    num = c['MESSAGES_DISPLAY']
    rel = []
    if g['stuff'].isdigit():
        num = g['stuff']
    cur_page = 1
    # Max message per page is 20 so we have to loop
    while num > 20:
        rel = rel + t.direct_messages(
            count=20,
            page=cur_page,
            include_entities=False,
            skip_status=False
        )
        num -= 20
        cur_page += 1
    rel = rel + t.direct_messages(
        count=num,
        page=cur_page,
        include_entities=False,
        skip_status=False
    )
    # Display
    printNicely('Inbox: newest ' + str(len(rel)) + ' messages.')
    for m in reversed(rel):
        print_message(m)
    printNicely('')


def sent():
    """
    Sent direct messages
    """
    t = Twitter(auth=authen())
    num = c['MESSAGES_DISPLAY']
    rel = []
    if g['stuff'].isdigit():
        num = int(g['stuff'])
    cur_page = 1
    # Max message per page is 20 so we have to loop
    while num > 20:
        rel = rel + t.direct_messages.sent(
            count=20,
            page=cur_page,
            include_entities=False,
            skip_status=False
        )
        num -= 20
        cur_page += 1
    rel = rel + t.direct_messages.sent(
        count=num,
        page=cur_page,
        include_entities=False,
        skip_status=False
    )
    # Display
    printNicely('Sent: newest ' + str(len(rel)) + ' messages.')
    for m in reversed(rel):
        print_message(m)
    printNicely('')


def trash():
    """
    Remove message
    """
    t = Twitter(auth=authen())
    try:
        rid = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
    mid = db.rainbow_to_message_query(rid)[0].message_id
    t.direct_messages.destroy(id=mid)
    printNicely(green('Message deleted.'))


def whois():
    """
    Show profile of a specific user
    """
    t = Twitter(auth=authen())
    screen_name = g['stuff'].split()[0]
    if screen_name.startswith('@'):
        try:
            user = t.users.show(
                screen_name=screen_name[1:],
                include_entities=False)
            show_profile(user, g['iot'])
        except:
            printNicely(red('Omg no user.'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def follow():
    """
    Follow a user
    """
    t = Twitter(auth=authen())
    screen_name = g['stuff'].split()[0]
    if screen_name.startswith('@'):
        t.friendships.create(screen_name=screen_name[1:], follow=True)
        printNicely(green('You are following ' + screen_name + ' now!'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def unfollow():
    """
    Unfollow a user
    """
    t = Twitter(auth=authen())
    screen_name = g['stuff'].split()[0]
    if screen_name.startswith('@'):
        t.friendships.destroy(
            screen_name=screen_name[1:],
            include_entities=False)
        printNicely(green('Unfollow ' + screen_name + ' success!'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def mute():
    """
    Mute a user
    """
    t = Twitter(auth=authen())
    try:
        screen_name = g['stuff'].split()[0]
    except:
        printNicely(red('A name should be specified. '))
        return
    if screen_name.startswith('@'):
        rel = t.mutes.users.create(screen_name=screen_name[1:])
        if isinstance(rel, dict):
            printNicely(green(screen_name + ' is muted.'))
        else:
            printNicely(red(rel))
    else:
        printNicely(red('A name should begin with a \'@\''))


def unmute():
    """
    Unmute a user
    """
    t = Twitter(auth=authen())
    try:
        screen_name = g['stuff'].split()[0]
    except:
        printNicely(red('A name should be specified. '))
        return
    if screen_name.startswith('@'):
        rel = t.mutes.users.destroy(screen_name=screen_name[1:])
        if isinstance(rel, dict):
            printNicely(green(screen_name + ' is unmuted.'))
        else:
            printNicely(red(rel))
    else:
        printNicely(red('A name should begin with a \'@\''))


def muting():
    """
    List muting user
    """
    t = Twitter(auth=authen())
    # Init cursor
    next_cursor = -1
    rel = {}
    # Cursor loop
    while next_cursor != 0:
        list = t.mutes.users.list(
            screen_name=g['original_name'],
            cursor=next_cursor,
            skip_status=True,
            include_entities=False,
        )
        for u in list['users']:
            rel[u['name']] = '@' + u['screen_name']
        next_cursor = list['next_cursor']
    # Print out result
    printNicely('All: ' + str(len(rel)) + ' people.')
    for name in rel:
        user = '  ' + cycle_color(name) + grey(' ' + rel[name] + ' ')
        printNicely(user)


def block():
    """
    Block a user
    """
    t = Twitter(auth=authen())
    screen_name = g['stuff'].split()[0]
    if screen_name.startswith('@'):
        t.blocks.create(
            screen_name=screen_name[1:],
            include_entities=False,
            skip_status=True)
        printNicely(green('You blocked ' + screen_name + '.'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def unblock():
    """
    Unblock a user
    """
    t = Twitter(auth=authen())
    screen_name = g['stuff'].split()[0]
    if screen_name.startswith('@'):
        t.blocks.destroy(
            screen_name=screen_name[1:],
            include_entities=False,
            skip_status=True)
        printNicely(green('Unblock ' + screen_name + ' success!'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def report():
    """
    Report a user as a spam account
    """
    t = Twitter(auth=authen())
    screen_name = g['stuff'].split()[0]
    if screen_name.startswith('@'):
        t.users.report_spam(
            screen_name=screen_name[1:])
        printNicely(green('You reported ' + screen_name + '.'))
    else:
        printNicely(red('Sorry I can\'t understand.'))


def cal():
    """
    Unix's command `cal`
    """
    # Format
    rel = os.popen('cal').read().split('\n')
    month = rel.pop(0)
    month = random_rainbow(month)
    date = rel.pop(0)
    date = ' '.join([cycle_color(i) for i in date.split(' ')])
    today = str(int(os.popen('date +\'%d\'').read().strip()))
    # Display
    printNicely(month)
    printNicely(date)
    for line in rel:
        ary = line.split(' ')
        ary = map(lambda x: on_grey(x) if x == today else grey(x), ary)
        printNicely(' '.join(ary))


def theme():
    """
    List and change theme
    """
    if not g['stuff']:
        # List themes
        line = ' ' * 2 + light_yellow('* ')
        for theme in g['themes']:
            # Detect custom config
            if theme == 'user':
                line += light_magenta('custom')
                exists = db.theme_query()
                themes = [t.theme_name for t in exists]
                if themes[0] == 'user':
                    line += light_magenta(' (applied)')
                else:
                    line += light_magenta(' (not specified)')
            else:
                line += light_magenta(theme)
            printNicely(line)
    else:
        # Change theme
        try:
            # Load new config
            new_config = 'rainbowstream/colorset/' + g['stuff'] + '.json'
            new_config = load_config(new_config)
            if new_config
                for nc in new_config:
                    c[nc] = new_config[nc]
            # Update db
            theme_update(g['stuff'])
            g['decorated_name'] = color_func(
                c['DECORATED_NAME'])(
                '[@' + g['original_name'] + ']: ')
            printNicely(green('Theme changed.'))
        except:
            printNicely(red('Sorry, config file is broken!'))


def help():
    """
    Help
    """
    s = ' ' * 2
    h, w = os.popen('stty size', 'r').read().split()

    # Start
    usage = '\n'
    usage += s + 'Hi boss! I\'m ready to serve you right now!\n'
    usage += s + '-' * (int(w) - 4) + '\n'
    usage += s + 'You are ' + \
        light_yellow('already') + ' on your personal stream.\n'
    usage += s + 'Any update from Twitter will show up ' + \
        light_yellow('immediately') + '.\n'
    usage += s + 'In addtion, following commands are available right now:\n'

    # Discover the world
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Discover the world \n')
    usage += s * 2 + light_green('trend') + ' will show global trending topics. ' + \
        'You can try ' + light_green('trend US') + ' or ' + \
        light_green('trend JP Tokyo') + '.\n'
    usage += s * 2 + light_green('home') + ' will show your timeline. ' + \
        light_green('home 7') + ' will show 7 tweets.\n'
    usage += s * 2 + light_green('mentions') + ' will show mentions timeline. ' + \
        light_green('mentions 7') + ' will show 7 mention tweets.\n'
    usage += s * 2 + light_green('whois @mdo') + ' will show profile  of ' + \
        magenta('@mdo') + '.\n'
    usage += s * 2 + light_green('view @mdo') + \
        ' will show ' + magenta('@mdo') + '\'s home.\n'
    usage += s * 2 + light_green('s #AKB48') + ' will search for "' + \
        light_yellow('AKB48') + '" and return 5 newest tweet.\n'

    # Tweet
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Tweets \n')
    usage += s * 2 + light_green('t oops ') + \
        'will tweet "' + light_yellow('oops') + '" immediately.\n'
    usage += s * 2 + \
        light_green('rt 12 ') + ' will retweet to tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('allrt 12 20 ') + ' will list 20 newest retweet of the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + light_green('rep 12 oops') + ' will reply "' + \
        light_yellow('oops') + '" to tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('fav 12 ') + ' will favorite the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('ufav 12 ') + ' will unfavorite tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('del 12 ') + ' will delete tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + light_green('show image 12') + ' will show image in tweet with ' + \
        light_yellow('[id=12]') + ' in your OS\'s image viewer.\n'

    # Direct message
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Direct messages \n')
    usage += s * 2 + light_green('inbox') + ' will show inbox messages. ' + \
        light_green('inbox 7') + ' will show newest 7 messages.\n'
    usage += s * 2 + light_green('sent') + ' will show sent messages. ' + \
        light_green('sent 7') + ' will show newest 7 messages.\n'
    usage += s * 2 + light_green('mes @dtvd88 hi') + ' will send a "hi" messege to ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('trash 5') + ' will remove message with ' + \
        light_yellow('[message_id=5]') + '.\n'

    # Follower and following
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Fiends and followers \n')
    usage += s * 2 + \
        light_green('ls fl') + \
        ' will list all followers (people who are following you).\n'
    usage += s * 2 + \
        light_green('ls fr') + \
        ' will list all friends (people who you are following).\n'
    usage += s * 2 + light_green('fl @dtvd88') + ' will follow ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('ufl @dtvd88') + ' will unfollow ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('mute @dtvd88') + ' will mute ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('unmute @dtvd88') + ' will unmute ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('muting') + ' will list muting users.\n'
    usage += s * 2 + light_green('block @dtvd88') + ' will block ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('unblock @dtvd88') + ' will unblock ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('report @dtvd88') + ' will report ' + \
        magenta('@dtvd88') + ' as a spam account.\n'

    # Switch
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Switching streams \n')
    usage += s * 2 + light_green('switch public #AKB') + \
        ' will switch to public stream and follow "' + \
        light_yellow('AKB') + '" keyword.\n'
    usage += s * 2 + light_green('switch mine') + \
        ' will switch to your personal stream.\n'
    usage += s * 2 + light_green('switch mine -f ') + \
        ' will prompt to enter the filter.\n'
    usage += s * 3 + light_yellow('Only nicks') + \
        ' filter will decide nicks will be INCLUDE ONLY.\n'
    usage += s * 3 + light_yellow('Ignore nicks') + \
        ' filter will decide nicks will be EXCLUDE.\n'
    usage += s * 2 + light_green('switch mine -d') + \
        ' will use the config\'s ONLY_LIST and IGNORE_LIST.\n'

    # Smart shell
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Smart shell\n')
    usage += s * 2 + light_green('111111 * 9 / 7') + ' or any math expression ' + \
        'will be evaluate by Python interpreter.\n'
    usage += s * 2 + 'Even ' + light_green('cal') + ' will show the calendar' + \
        ' for current month.\n'

    # Screening
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Screening \n')
    usage += s * 2 + light_green('theme') + ' will list available theme.' + \
        light_green('theme monokai') + ' will apply ' + light_yellow('monokai') + \
        ' theme immediately.\n'
    usage += s * 2 + light_green('h') + ' will show this help again.\n'
    usage += s * 2 + light_green('c') + ' will clear the screen.\n'
    usage += s * 2 + light_green('q') + ' will quit.\n'

    # End
    usage += '\n'
    usage += s + '-' * (int(w) - 4) + '\n'
    usage += s + 'Have fun and hang tight! \n'
    printNicely(usage)


def clear():
    """
    Clear screen
    """
    os.system('clear')


def quit():
    """
    Exit all
    """
    save_history()
    os.system('rm -rf rainbow.db')
    os.kill(g['stream_pid'], signal.SIGKILL)
    sys.exit()


def reset():
    """
    Reset prefix of line
    """
    if g['reset']:
        printNicely(magenta('Need tips ? Type "h" and hit Enter key!'))
    g['reset'] = False
    try:
        printNicely(eval(g['cmd']))
    except:
        pass


def process(cmd):
    """
    Process switch
    """
    return dict(zip(
        cmdset,
        [
            switch,
            trend,
            home,
            view,
            mentions,
            tweet,
            retweet,
            allretweet,
            favorite,
            reply,
            delete,
            unfavorite,
            search,
            message,
            show,
            list,
            inbox,
            sent,
            trash,
            whois,
            follow,
            unfollow,
            mute,
            unmute,
            muting,
            block,
            unblock,
            report,
            cal,
            theme,
            help,
            clear,
            quit
        ]
    )).get(cmd, reset)


def listen():
    """
    Listen to user's input
    """
    d = dict(zip(
        cmdset,
        [
            ['public', 'mine'],  # switch
            [],  # trend
            [],  # home
            ['@'],  # view
            [],  # mentions
            [],  # tweet
            [],  # retweet
            [],  # allretweet
            [],  # favorite
            [],  # reply
            [],  # delete
            [],  # unfavorite
            ['#'],  # search
            ['@'],  # message
            ['image'],  # show image
            ['fl', 'fr'],  # list
            [],  # inbox
            [],  # sent
            [],  # trash
            ['@'],  # whois
            ['@'],  # follow
            ['@'],  # unfollow
            ['@'],  # mute
            ['@'],  # unmute
            ['@'],  # muting
            ['@'],  # block
            ['@'],  # unblock
            ['@'],  # report
            [],  # cal
            g['themes'],  # theme
            [],  # help
            [],  # clear
            [],  # quit
        ]
    ))
    init_interactive_shell(d)
    read_history()
    reset()
    while True:
        if g['prefix']:
            line = raw_input(g['decorated_name'])
        else:
            line = raw_input()
        try:
            cmd = line.split()[0]
        except:
            cmd = ''
        g['cmd'] = cmd
        # Save cmd to global variable and call process
        try:
            g['stuff'] = ' '.join(line.split()[1:])
            process(cmd)()
        except Exception as e:
            print e
            printNicely(red('OMG something is wrong with Twitter right now.'))
        # Not redisplay prefix
        if cmd in ['switch', 't', 'rt', 'rep']:
            g['prefix'] = False
        else:
            g['prefix'] = True


def stream(domain, args, name='Rainbow Stream'):
    """
    Track the stream
    """

    # The Logo
    art_dict = {
        c['USER_DOMAIN']: name,
        c['PUBLIC_DOMAIN']: args.track_keywords,
        c['SITE_DOMAIN']: 'Site Stream',
    }
    if g['ascii_art']:
        ascii_art(art_dict[domain])

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
        auth=authen(),
        domain=domain,
        **stream_args)

    if domain == c['USER_DOMAIN']:
        tweet_iter = stream.user(**query_args)
    elif domain == c['SITE_DOMAIN']:
        tweet_iter = stream.site(**query_args)
    else:
        if args.track_keywords:
            tweet_iter = stream.statuses.filter(**query_args)
        else:
            tweet_iter = stream.statuses.sample()

    # Iterate over the stream.
    try:
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
                draw(
                    t=tweet,
                    iot=args.image_on_term,
                    keyword=args.track_keywords,
                    fil=args.filter,
                    ig=args.ignore,
                )
    except:
        printNicely(
            magenta("I'm afraid we have problem with twitter'S maximum connection."))
        printNicely(magenta("Let's try again later."))


def fly():
    """
    Main function
    """
    # Spawn stream process
    args = parse_arguments()
    get_decorated_name()
    p = Process(
        target=stream,
        args=(
            c['USER_DOMAIN'],
            args,
            g['original_name']))
    p.start()

    # Start listen process
    time.sleep(0.5)
    g['reset'] = True
    g['prefix'] = True
    g['stream_pid'] = p.pid
    g['iot'] = args.image_on_term
    listen()
