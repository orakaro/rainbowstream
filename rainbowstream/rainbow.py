import os
import os.path
import sys
import signal
import argparse
import time
import threading
import requests
import webbrowser
import traceback
import pkg_resources
import socks
import socket
import re

from io import BytesIO
from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from twitter.api import *
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.util import printNicely

from pocket import Pocket

from .draw import *
from .colors import *
from .config import *
from .consumer import *
from .interactive import *
from .c_image import *
from .py3patch import *
from .emoji import *
from .util import *

# Global values
g = {}

# Lock for streams
StreamLock = threading.Lock()


def parse_arguments():
    """
    Parse the arguments
    """
    parser = argparse.ArgumentParser(description=__doc__ or "")
    parser.add_argument(
        '-s',
        '--stream',
        default="mine",
        help='Default stream after program start. (Default: mine)')
    parser.add_argument(
        '-to',
        '--timeout',
        help='Timeout for the stream (seconds).')
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
    parser.add_argument(
        '-24',
        '--color-24bit',
        action='store_true',
        help='Display images using 24bit color codes.')
    parser.add_argument(
        '-ph',
        '--proxy-host',
        help='Use HTTP/SOCKS proxy for network connections.')
    parser.add_argument(
        '-pp',
        '--proxy-port',
        default=8080,
        help='HTTP/SOCKS proxy port (Default: 8080).')
    parser.add_argument(
        '-pt',
        '--proxy-type',
        default='SOCKS5',
        help='Proxy type (HTTP, SOCKS4, SOCKS5; Default: SOCKS5).')
    return parser.parse_args()


def proxy_connect(args):
    """
    Connect to specified proxy
    """
    if args.proxy_host:
        # Setup proxy by monkeypatching the standard lib
        if args.proxy_type.lower() == "socks5" or not args.proxy_type:
            socks.set_default_proxy(
                socks.SOCKS5, args.proxy_host,
                int(args.proxy_port))
        elif args.proxy_type.lower() == "http":
            socks.set_default_proxy(
                socks.HTTP, args.proxy_host,
                int(args.proxy_port))
        elif args.proxy_type.lower() == "socks4":
            socks.set_default_proxy(
                socks.SOCKS4, args.proxy_host,
                int(args.proxy_port))
        else:
            printNicely(
                magenta('Sorry, wrong proxy type specified! Aborting...'))
            sys.exit()
        socket.socket = socks.socksocket


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
        oauth_dance('Rainbow Stream',
                    CONSUMER_KEY,
                    CONSUMER_SECRET,
                    twitter_credential)
    oauth_token, oauth_token_secret = read_token_file(twitter_credential)
    return OAuth(
        oauth_token,
        oauth_token_secret,
        CONSUMER_KEY,
        CONSUMER_SECRET)


def pckt_authen():
    """
    Authenticate with Pocket OAuth
    """
    pocket_credential = os.environ.get(
         'HOME',
        os.environ.get(
            'USERPROFILE',
            '')) + os.sep + '.rainbow_pckt_oauth'

    if not os.path.exists(pocket_credential):
        request_token = Pocket.get_request_token(consumer_key=PCKT_CONSUMER_KEY)
        auth_url = Pocket.get_auth_url(code=request_token, redirect_uri="/")
        webbrowser.open(auth_url)
        printNicely(green("*** Press [ENTER] after authorization ***"))
        raw_input()
        user_credentials = Pocket.get_credentials(consumer_key=PCKT_CONSUMER_KEY, code=request_token)
        access_token = user_credentials['access_token']
        f = open(pocket_credential, 'w')
        f.write(access_token)
        f.close()
    else:
        with open(pocket_credential, 'r') as f:
            access_token = str(f.readlines()[0])
            f.close()

    return Pocket(PCKT_CONSUMER_KEY, access_token)


def build_mute_dict(dict_data=False):
    """
    Build muting list
    """
    t = Twitter(auth=authen())
    # Init cursor
    next_cursor = -1
    screen_name_list = []
    name_list = []
    # Cursor loop
    while next_cursor != 0:
        list = t.mutes.users.list(
            screen_name=g['original_name'],
            cursor=next_cursor,
            skip_status=True,
            include_entities=False,
        )
        screen_name_list += ['@' + u['screen_name'] for u in list['users']]
        name_list += [u['name'] for u in list['users']]
        next_cursor = list['next_cursor']
    # Return dict or list
    if dict_data:
        return dict(zip(screen_name_list, name_list))
    else:
        return screen_name_list


def debug_option():
    """
    Save traceback when run in debug mode
    """
    if g['debug']:
        g['traceback'].append(traceback.format_exc())


def upgrade_center():
    """
    Check latest and notify to upgrade
    """
    try:
        current = pkg_resources.get_distribution('rainbowstream').version
        url = 'https://raw.githubusercontent.com/DTVD/rainbowstream/master/setup.py'
        readme = requests.get(url).text
        latest = readme.split('version = \'')[1].split('\'')[0]
        g['using_latest'] = current == latest
        if not g['using_latest']:
            notice = light_magenta('RainbowStream latest version is ')
            notice += light_green(latest)
            notice += light_magenta(' while your current version is ')
            notice += light_yellow(current) + '\n'
            notice += light_magenta('You should upgrade with ')
            notice += light_green('pip install -U rainbowstream')
        else:
            notice = light_yellow('You are running latest version (')
            notice += light_green(current)
            notice += light_yellow(')')
            notice += '\n'
        printNicely(notice)
    except:
        pass


def init(args):
    """
    Init function
    """
    # Handle Ctrl C
    ctrl_c_handler = lambda signum, frame: quit()
    signal.signal(signal.SIGINT, ctrl_c_handler)
    # Upgrade notify
    upgrade_center()
    # Get name
    t = Twitter(auth=authen())
    credential = t.account.verify_credentials()
    screen_name = '@' + credential['screen_name']
    name = credential['name']
    c['original_name'] = g['original_name'] = screen_name[1:]
    g['listname'] = g['keyword'] = ''
    g['PREFIX'] = u2str(emojize(format_prefix()))
    g['full_name'] = name
    g['decorated_name'] = lambda x: color_func(
        c['DECORATED_NAME'])('[' + x + ']: ', rl=True)
    # Theme init
    files = os.listdir(os.path.dirname(__file__) + '/colorset')
    themes = [f.split('.')[0] for f in files if f.split('.')[-1] == 'json']
    g['themes'] = themes
    g['pause'] = False
    g['message_threads'] = {}
    # Startup cmd
    g['cmd'] = ''
    # Debug option default = True
    g['debug'] = True
    g['traceback'] = []
    # Events
    c['events'] = []
    # Semaphore init
    c['lock'] = False
    # Init tweet dict and message dict
    c['tweet_dict'] = []
    c['message_dict'] = []
    # Image on term
    c['IMAGE_ON_TERM'] = args.image_on_term
    # Use 24 bit color
    c['24BIT'] = args.color_24bit
    # Check type of ONLY_LIST and IGNORE_LIST
    if not isinstance(c['ONLY_LIST'], list):
        printNicely(red('ONLY_LIST is not a valid list value.'))
        c['ONLY_LIST'] = []
    if not isinstance(c['IGNORE_LIST'], list):
        printNicely(red('IGNORE_LIST is not a valid list value.'))
        c['IGNORE_LIST'] = []
    # Mute dict
    c['IGNORE_LIST'] += build_mute_dict()
    # Pocket init
    pckt = pckt_authen() if c['POCKET_SUPPORT'] else None


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
    kwargs = {'count': num}
    kwargs = add_tweetmode_parameter(kwargs)
    for tweet in reversed(t.statuses.home_timeline(**kwargs)):
        draw(t=tweet)
    printNicely('')


def notification():
    """
    Show notifications
    """
    if c['events']:
        for e in c['events']:
            print_event(e)
        printNicely('')
    else:
        printNicely(magenta('Nothing at this time.'))


def mentions():
    """
    Mentions timeline
    """
    t = Twitter(auth=authen())
    num = c['HOME_TWEET_NUM']
    if g['stuff'].isdigit():
        num = int(g['stuff'])
    kwargs = {'count': num}
    kwargs = add_tweetmode_parameter(kwargs)
    for tweet in reversed(t.statuses.mentions_timeline(**kwargs)):
        draw(t=tweet)
    printNicely('')


def whois():
    """
    Show profile of a specific user
    """
    t = Twitter(auth=authen())
    try:
        screen_name = g['stuff'].split()[0]
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    if screen_name.startswith('@'):
        try:
            user = t.users.show(
                screen_name=screen_name[1:],
                include_entities=False)
            show_profile(user)
        except:
            debug_option()
            printNicely(red('No user.'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def view():
    """
    Friend view
    """
    t = Twitter(auth=authen())
    try:
        user = g['stuff'].split()[0]
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    if user[0] == '@':
        try:
            num = int(g['stuff'].split()[1])
        except:
            num = c['HOME_TWEET_NUM']
        kwargs = {'count': num, 'screen_name': user[1:]}
        kwargs = add_tweetmode_parameter(kwargs)
        for tweet in reversed(t.statuses.user_timeline(**kwargs)):
            draw(t=tweet)
        printNicely('')
    else:
        printNicely(red('A name should begin with a \'@\''))


def view_my_tweets():
    """
    Display user's recent tweets.
    """
    t = Twitter(auth=authen())
    try:
        num = int(g['stuff'])
    except:
        num = c['HOME_TWEET_NUM']
    kwargs = {'count': num, 'screen_name': g['original_name']}
    kwargs = add_tweetmode_parameter(kwargs)
    for tweet in reversed(
            t.statuses.user_timeline(**kwargs)):
        draw(t=tweet)
    printNicely('')


def search():
    """
    Search
    """
    t = Twitter(auth=authen())
    # Setup query
    query = g['stuff'].strip()
    if not query:
        printNicely(red('Sorry I can\'t understand.'))
        return
    type = c['SEARCH_TYPE']
    if type not in ['mixed', 'recent', 'popular']:
        type = 'mixed'
    max_record = c['SEARCH_MAX_RECORD']
    count = min(max_record, 100)
    kwargs = {
        'q': query,
        'type': type,
        'count': count,
    }
    kwargs = add_tweetmode_parameter(kwargs)
    # Perform search
    rel = t.search.tweets(**kwargs)['statuses']
    # Return results
    if rel:
        printNicely('Newest tweets:')
        for i in reversed(xrange(count)):
            draw(t=rel[i], keyword=query)
        printNicely('')
    else:
        printNicely(magenta('I\'m afraid there is no result'))


def tweet():
    """
    Tweet
    """
    t = Twitter(auth=authen())
    t.statuses.update(status=g['stuff'])


def pocket():
    """
    Add new link to Pocket along with tweet id
    """
    if not c['POCKET_SUPPORT']:
        printNicely(yellow('Pocket isn\'t enabled.'))
        printNicely(yellow('You need to "config POCKET_SUPPORT = true"'))
        return

    # Get tweet infos
    p = pckt_authen()

    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
        tid = c['tweet_dict'][id]
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return

    tweet = t.statuses.show(id=tid)

    if len(tweet['entities']['urls']) > 0:
        url = tweet['entities']['urls'][0]['expanded_url']
    else:
        url = "https://twitter.com/" + \
                tweet['user']['screen_name'] + '/status/' + str(tid)

    # Add link to pocket
    try:
        p.add(title=re.sub(r'(http:\/\/\S+)', r'', tweet['text']),
            url=url,
            tweet_id=tid)
    except:
        printNicely(red('Something is wrong about your Pocket account,'+ \
                        ' please restart Rainbowstream.'))
        pocket_credential = os.environ.get(
            'HOME',
            os.environ.get(
                'USERPROFILE',
                '')) + os.sep + '.rainbow_pckt_oauth'
        if os.path.exists(pocket_credential):
            os.remove(pocket_credential)
        return

    printNicely(green('Pocketed !'))
    printNicely('')


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
    tid = c['tweet_dict'][id]
    t.statuses.retweet(id=tid, include_entities=False, trim_user=True)


def quote():
    """
    Quote a tweet
    """
    # Get tweet
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = c['tweet_dict'][id]
    kwargs = {'id': tid}
    kwargs = add_tweetmode_parameter(kwargs)
    tweet = t.statuses.show(**kwargs)
    # Get formater
    formater = format_quote(tweet)
    if not formater:
        return
    # Get comment
    prefix = light_magenta('Compose your ', rl=True) + \
        light_green('#comment: ', rl=True)
    comment = raw_input(prefix)
    if comment:
        quote = comment.join(formater.split('#comment'))
        t.statuses.update(status=quote)
    else:
        printNicely(light_magenta('No text added.'))


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
    tid = c['tweet_dict'][id]
    # Get display num if exist
    try:
        num = int(g['stuff'].split()[1])
    except:
        num = c['RETWEETS_SHOW_NUM']
    # Get result and display
    kwargs = {'id': tid, 'count': num}
    kwargs = add_tweetmode_parameter(kwargs)
    rt_ary = t.statuses.retweets(**kwargs)
    if not rt_ary:
        printNicely(magenta('This tweet has no retweet.'))
        return
    for tweet in reversed(rt_ary):
        draw(t=tweet)
    printNicely('')


def conversation():
    """
    Conversation view
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = c['tweet_dict'][id]
    kwargs = {'id': tid}
    kwargs = add_tweetmode_parameter(kwargs)
    tweet = t.statuses.show(**kwargs)
    limit = c['CONVERSATION_MAX']
    thread_ref = []
    thread_ref.append(tweet)
    prev_tid = tweet['in_reply_to_status_id']
    while prev_tid and limit:
        limit -= 1
        kwargs['id'] = prev_tid
        tweet = t.statuses.show(**kwargs)
        prev_tid = tweet['in_reply_to_status_id']
        thread_ref.append(tweet)

    for tweet in reversed(thread_ref):
        draw(t=tweet)
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
    tid = c['tweet_dict'][id]
    user = t.statuses.show(id=tid)['user']['screen_name']
    status = ' '.join(g['stuff'].split()[1:])
    # don't include own username for tweet chains
    # for details see issue https://github.com/DTVD/rainbowstream/issues/163
    if user == g['original_name']:
        status = str2u(status)
    else:
        status = '@' + user + ' ' + str2u(status)
    t.statuses.update(status=status, in_reply_to_status_id=tid)


def reply_all():
    """
    Reply to all
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = c['tweet_dict'][id]
    original_tweet = t.statuses.show(id=tid)
    text = original_tweet['text']
    nick_ary = [original_tweet['user']['screen_name']]
    for user in list(original_tweet['entities']['user_mentions']):
        if user['screen_name'] not in nick_ary \
                and user['screen_name'] != g['original_name']:
            nick_ary.append(user['screen_name'])
    status = ' '.join(g['stuff'].split()[1:])
    status = ' '.join(['@' + nick for nick in nick_ary]) + ' ' + str2u(status)
    t.statuses.update(status=status, in_reply_to_status_id=tid)


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
    tid = c['tweet_dict'][id]
    t.favorites.create(_id=tid, include_entities=False)
    printNicely(green('Favorited.'))
    kwargs = {'id': tid}
    kwargs = add_tweetmode_parameter(kwargs)
    draw(t.statuses.show(**kwargs))
    printNicely('')


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
    tid = c['tweet_dict'][id]
    t.favorites.destroy(_id=tid)
    printNicely(green('Okay it\'s unfavorited.'))
    kwargs = {'id': tid}
    kwargs = add_tweetmode_parameter(kwargs)
    draw(t.statuses.show(**kwargs))
    printNicely('')


def share():
    """
    Copy url of a tweet to clipboard
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
        tid = c['tweet_dict'][id]
    except:
        printNicely(red('Tweet id is not valid.'))
        return
    kwargs = {'id': tid}
    kwargs = add_tweetmode_parameter(kwargs)
    tweet = t.statuses.show(**kwargs)
    url = 'https://twitter.com/' + \
        tweet['user']['screen_name'] + '/status/' + str(tid)
    import platform
    if platform.system().lower() == 'darwin':
        os.system("echo '%s' | pbcopy" % url)
        printNicely(green('Copied tweet\'s url to clipboard.'))
    else:
        printNicely('Direct link: ' + yellow(url))


def delete():
    """
    Delete
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
        return
    tid = c['tweet_dict'][id]
    t.statuses.destroy(id=tid)
    printNicely(green('Okay it\'s gone.'))


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
        tid = c['tweet_dict'][id]
        tweet = t.statuses.show(id=tid)
        media = tweet['entities']['media']
        for m in media:
            res = requests.get(m['media_url'])
            img = Image.open(BytesIO(res.content))
            img.show()
    except:
        debug_option()
        printNicely(red('Sorry I can\'t show this image.'))


def urlopen():
    """
    Open url
    """
    t = Twitter(auth=authen())
    try:
        if not g['stuff'].isdigit():
            return
        tid = c['tweet_dict'][int(g['stuff'])]
        tweet = t.statuses.show(id=tid)
        urls = tweet['entities']['urls']
        if not urls:
            printNicely(light_magenta('No url here @.@!'))
            return
        else:
            for url in urls:
                expanded_url = url['expanded_url']
                webbrowser.open(expanded_url)
    except:
        debug_option()
        printNicely(red('Sorry I can\'t open url in this tweet.'))


def inbox():
    """
    Inbox threads
    """
    t = Twitter(auth=authen())
    num = c['MESSAGES_DISPLAY']
    if g['stuff'].isdigit():
        num = g['stuff']
    # Get inbox messages
    cur_page = 1
    inbox = []
    while num > 20:
        inbox = inbox + t.direct_messages(
            count=20,
            page=cur_page,
            include_entities=False,
            skip_status=False
        )
        num -= 20
        cur_page += 1
    inbox = inbox + t.direct_messages(
        count=num,
        page=cur_page,
        include_entities=False,
        skip_status=False
    )
    # Get sent messages
    num = c['MESSAGES_DISPLAY']
    if g['stuff'].isdigit():
        num = g['stuff']
    cur_page = 1
    sent = []
    while num > 20:
        sent = sent + t.direct_messages.sent(
            count=20,
            page=cur_page,
            include_entities=False,
            skip_status=False
        )
        num -= 20
        cur_page += 1
    sent = sent + t.direct_messages.sent(
        count=num,
        page=cur_page,
        include_entities=False,
        skip_status=False
    )

    d = {}
    uniq_inbox = list(set(
        [(m['sender_screen_name'], m['sender']['name']) for m in inbox]
    ))
    uniq_sent = list(set(
        [(m['recipient_screen_name'], m['recipient']['name']) for m in sent]
    ))
    for partner in uniq_inbox:
        inbox_ary = [m for m in inbox if m['sender_screen_name'] == partner[0]]
        sent_ary = [
            m for m in sent if m['recipient_screen_name'] == partner[0]]
        d[partner] = inbox_ary + sent_ary
    for partner in uniq_sent:
        if partner not in d:
            d[partner] = [
                m for m in sent if m['recipient_screen_name'] == partner[0]]
    g['message_threads'] = print_threads(d)


def thread():
    """
    View a thread of message
    """
    try:
        thread_id = int(g['stuff'])
        print_thread(
            g['message_threads'][thread_id],
            g['original_name'],
            g['full_name'])
    except Exception:
        debug_option()
        printNicely(red('No such thread.'))


def message():
    """
    Send a direct message
    """
    t = Twitter(auth=authen())
    try:
        user = g['stuff'].split()[0]
        if user[0].startswith('@'):
            content = ' '.join(g['stuff'].split()[1:])
            t.direct_messages.new(
                screen_name=user[1:],
                text=content
            )
            printNicely(green('Message sent.'))
        else:
            printNicely(red('A name should begin with a \'@\''))
    except:
        debug_option()
        printNicely(red('Sorry I can\'t understand.'))


def trash():
    """
    Remove message
    """
    t = Twitter(auth=authen())
    try:
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
    mid = c['message_dict'][id]
    t.direct_messages.destroy(id=mid)
    printNicely(green('Message deleted.'))


def ls():
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
        return
    # Init cursor
    d = {'fl': 'followers', 'fr': 'friends'}
    next_cursor = -1
    rel = {}

    printNicely('All ' + d[target] + ':')

    # Cursor loop
    number_of_users = 0
    while next_cursor != 0:

        list = getattr(t, d[target]).list(
            screen_name=name,
            cursor=next_cursor,
            skip_status=True,
            include_entities=False,
        )

        for u in list['users']:

            number_of_users += 1

            # Print out result
            printNicely(   '  '                                               \
                         + cycle_color( u['name'] )                           \
                         + color_func(c['TWEET']['nick'])(    ' @'            \
                                                           + u['screen_name'] \
                                                           + ' ' ) )

        next_cursor = list['next_cursor']

        # 300 users means 15 calls to the related API. The rate limit is 15
        # calls per 15mn periods (see Twitter documentation).
        if ( number_of_users % 300 == 0 ):
            printNicely(light_yellow( 'We reached the limit of Twitter API.' ))
            printNicely(light_yellow( 'You may need to wait about 15 minutes.' ))
            break

    printNicely('All: ' + str(number_of_users) + ' ' + d[target] + '.')

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
        try:
            rel = t.mutes.users.create(screen_name=screen_name[1:])
            if isinstance(rel, dict):
                printNicely(green(screen_name + ' is muted.'))
                c['IGNORE_LIST'] += [screen_name]
                c['IGNORE_LIST'] = list(set(c['IGNORE_LIST']))
            else:
                printNicely(red(rel))
        except:
            debug_option()
            printNicely(red('Something is wrong, can not mute now :('))
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
        try:
            rel = t.mutes.users.destroy(screen_name=screen_name[1:])
            if isinstance(rel, dict):
                printNicely(green(screen_name + ' is unmuted.'))
                c['IGNORE_LIST'].remove(screen_name)
            else:
                printNicely(red(rel))
        except:
            printNicely(red('Maybe you are not muting this person ?'))
    else:
        printNicely(red('A name should begin with a \'@\''))


def muting():
    """
    List muting user
    """
    # Get dict of muting users
    md = build_mute_dict(dict_data=True)
    printNicely('All: ' + str(len(md)) + ' people.')
    for name in md:
        user = '  ' + cycle_color(md[name])
        user += color_func(c['TWEET']['nick'])(' ' + name + ' ')
        printNicely(user)
    # Update from Twitter
    c['IGNORE_LIST'] = [n for n in md]


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


def get_slug():
    """
    Get slug
    """
    # Get list name
    list_name = raw_input(
        light_magenta('Give me the list\'s name ("@owner/list_name"): ', rl=True))
    # Get list name and owner
    try:
        owner, slug = list_name.split('/')
        if slug.startswith('@'):
            slug = slug[1:]
        return owner, slug
    except:
        printNicely(
            light_magenta('List name should follow "@owner/list_name" format.'))
        raise Exception('Wrong list name')


def check_slug(list_name):
    """
    Check slug
    """
    # Get list name and owner
    try:
        owner, slug = list_name.split('/')
        if slug.startswith('@'):
            slug = slug[1:]
        return owner, slug
    except:
        printNicely(
            light_magenta('List name should follow "@owner/list_name" format.'))
        raise Exception('Wrong list name')


def show_lists(t):
    """
    List list
    """
    rel = t.lists.list(screen_name=g['original_name'])
    if rel:
        print_list(rel)
    else:
        printNicely(light_magenta('You belong to no lists :)'))


def list_home(t):
    """
    List home
    """
    owner, slug = get_slug()
    res = t.lists.statuses(
        slug=slug,
        owner_screen_name=owner,
        count=c['LIST_MAX'],
        include_entities=False)
    for tweet in reversed(res):
        draw(t=tweet)
    printNicely('')


def list_members(t):
    """
    List members
    """
    owner, slug = get_slug()
    # Get members
    rel = {}
    next_cursor = -1
    while next_cursor != 0:
        m = t.lists.members(
            slug=slug,
            owner_screen_name=owner,
            cursor=next_cursor,
            include_entities=False)
        for u in m['users']:
            rel[u['name']] = '@' + u['screen_name']
        next_cursor = m['next_cursor']
    printNicely('All: ' + str(len(rel)) + ' members.')
    for name in rel:
        user = '  ' + cycle_color(name)
        user += color_func(c['TWEET']['nick'])(' ' + rel[name] + ' ')
        printNicely(user)


def list_subscribers(t):
    """
    List subscribers
    """
    owner, slug = get_slug()
    # Get subscribers
    rel = {}
    next_cursor = -1
    while next_cursor != 0:
        m = t.lists.subscribers(
            slug=slug,
            owner_screen_name=owner,
            cursor=next_cursor,
            include_entities=False)
        for u in m['users']:
            rel[u['name']] = '@' + u['screen_name']
        next_cursor = m['next_cursor']
    printNicely('All: ' + str(len(rel)) + ' subscribers.')
    for name in rel:
        user = '  ' + cycle_color(name)
        user += color_func(c['TWEET']['nick'])(' ' + rel[name] + ' ')
        printNicely(user)


def list_add(t):
    """
    Add specific user to a list
    """
    owner, slug = get_slug()
    # Add
    user_name = raw_input(
        light_magenta(
            'Give me name of the newbie: ',
            rl=True))
    if user_name.startswith('@'):
        user_name = user_name[1:]
    try:
        t.lists.members.create(
            slug=slug,
            owner_screen_name=owner,
            screen_name=user_name)
        printNicely(green('Added.'))
    except:
        debug_option()
        printNicely(light_magenta('I\'m sorry we can not add him/her.'))


def list_remove(t):
    """
    Remove specific user from a list
    """
    owner, slug = get_slug()
    # Remove
    user_name = raw_input(
        light_magenta(
            'Give me name of the unlucky one: ',
            rl=True))
    if user_name.startswith('@'):
        user_name = user_name[1:]
    try:
        t.lists.members.destroy(
            slug=slug,
            owner_screen_name=owner,
            screen_name=user_name)
        printNicely(green('Gone.'))
    except:
        debug_option()
        printNicely(light_magenta('I\'m sorry we can not remove him/her.'))


def list_subscribe(t):
    """
    Subscribe to a list
    """
    owner, slug = get_slug()
    # Subscribe
    try:
        t.lists.subscribers.create(
            slug=slug,
            owner_screen_name=owner)
        printNicely(green('Done.'))
    except:
        debug_option()
        printNicely(
            light_magenta('I\'m sorry you can not subscribe to this list.'))


def list_unsubscribe(t):
    """
    Unsubscribe a list
    """
    owner, slug = get_slug()
    # Subscribe
    try:
        t.lists.subscribers.destroy(
            slug=slug,
            owner_screen_name=owner)
        printNicely(green('Done.'))
    except:
        debug_option()
        printNicely(
            light_magenta('I\'m sorry you can not unsubscribe to this list.'))


def list_own(t):
    """
    List own
    """
    rel = []
    next_cursor = -1
    while next_cursor != 0:
        res = t.lists.ownerships(
            screen_name=g['original_name'],
            cursor=next_cursor)
        rel += res['lists']
        next_cursor = res['next_cursor']
    if rel:
        print_list(rel)
    else:
        printNicely(light_magenta('You own no lists :)'))


def list_new(t):
    """
    Create a new list
    """
    name = raw_input(light_magenta('New list\'s name: ', rl=True))
    mode = raw_input(
        light_magenta(
            'New list\'s mode (public/private): ',
            rl=True))
    description = raw_input(
        light_magenta(
            'New list\'s description: ',
            rl=True))
    try:
        t.lists.create(
            name=name,
            mode=mode,
            description=description)
        printNicely(green(name + ' list is created.'))
    except:
        debug_option()
        printNicely(red('Oops something is wrong with Twitter :('))


def list_update(t):
    """
    Update a list
    """
    slug = raw_input(
        light_magenta(
            'Your list that you want to update: ',
            rl=True))
    name = raw_input(
        light_magenta(
            'Update name (leave blank to unchange): ',
            rl=True))
    mode = raw_input(light_magenta('Update mode (public/private): ', rl=True))
    description = raw_input(light_magenta('Update description: ', rl=True))
    try:
        if name:
            t.lists.update(
                slug='-'.join(slug.split()),
                owner_screen_name=g['original_name'],
                name=name,
                mode=mode,
                description=description)
        else:
            t.lists.update(
                slug=slug,
                owner_screen_name=g['original_name'],
                mode=mode,
                description=description)
        printNicely(green(slug + ' list is updated.'))
    except:
        debug_option()
        printNicely(red('Oops something is wrong with Twitter :('))


def list_delete(t):
    """
    Delete a list
    """
    slug = raw_input(
        light_magenta(
            'Your list that you want to delete: ',
            rl=True))
    try:
        t.lists.destroy(
            slug='-'.join(slug.split()),
            owner_screen_name=g['original_name'])
        printNicely(green(slug + ' list is deleted.'))
    except:
        debug_option()
        printNicely(red('Oops something is wrong with Twitter :('))


def twitterlist():
    """
    Twitter's list
    """
    t = Twitter(auth=authen())
    # List all lists or base on action
    try:
        g['list_action'] = g['stuff'].split()[0]
    except:
        show_lists(t)
        return
    # Sub-function
    action_ary = {
        'home': list_home,
        'all_mem': list_members,
        'all_sub': list_subscribers,
        'add': list_add,
        'rm': list_remove,
        'sub': list_subscribe,
        'unsub': list_unsubscribe,
        'own': list_own,
        'new': list_new,
        'update': list_update,
        'del': list_delete,
    }
    try:
        return action_ary[g['list_action']](t)
    except:
        printNicely(red('Please try again.'))


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
                guide = 'To ignore an option, just hit Enter key.'
                printNicely(light_magenta(guide))
                only = raw_input('Only nicks [Ex: @xxx,@yy]: ')
                ignore = raw_input('Ignore nicks [Ex: @xxx,@yy]: ')
                args.filter = list(filter(None, only.split(',')))
                args.ignore = list(filter(None, ignore.split(',')))
        except:
            printNicely(red('Sorry, wrong format.'))
            return
        # Kill old thread
        g['stream_stop'] = True
        try:
            stuff = g['stuff'].split()[1]
        except:
            stuff = None
        # Spawn new thread
        spawn_dict = {
            'public': spawn_public_stream,
            'list': spawn_list_stream,
            'mine': spawn_personal_stream,
        }
        spawn_dict.get(target)(args, stuff)
    except:
        debug_option()
        printNicely(red('Sorry I can\'t understand.'))


def cal():
    """
    Unix's command `cal`
    """
    # Format
    rel = os.popen('cal').read().split('\n')
    month = rel.pop(0)
    date = rel.pop(0)
    show_calendar(month, date, rel)


def theme():
    """
    List and change theme
    """
    if not g['stuff']:
        # List themes
        for theme in g['themes']:
            line = light_magenta(theme)
            if c['THEME'] == theme:
                line = ' ' * 2 + light_yellow('* ') + line
            else:
                line = ' ' * 4 + line
            printNicely(line)
    else:
        # Change theme
        try:
            # Load new theme
            c['THEME'] = reload_theme(g['stuff'], c['THEME'])
            # Redefine decorated_name
            g['decorated_name'] = lambda x: color_func(
                c['DECORATED_NAME'])(
                '[' + x + ']: ')
            printNicely(green('Theme changed.'))
        except:
            printNicely(red('No such theme exists.'))


def config():
    """
    Browse and change config
    """
    all_config = get_all_config()
    g['stuff'] = g['stuff'].strip()
    # List all config
    if not g['stuff']:
        for k in all_config:
            line = ' ' * 2 + \
                green(k) + ': ' + light_yellow(str(all_config[k]))
            printNicely(line)
        guide = 'Detailed explanation can be found at ' + \
            color_func(c['TWEET']['link'])(
                'http://rainbowstream.readthedocs.org/en/latest/#config-explanation')
        printNicely(guide)
    # Print specific config
    elif len(g['stuff'].split()) == 1:
        if g['stuff'] in all_config:
            k = g['stuff']
            line = ' ' * 2 + \
                green(k) + ': ' + light_yellow(str(all_config[k]))
            printNicely(line)
        else:
            printNicely(red('No such config key.'))
    # Print specific config's default value
    elif len(g['stuff'].split()) == 2 and g['stuff'].split()[-1] == 'default':
        key = g['stuff'].split()[0]
        try:
            value = get_default_config(key)
            line = ' ' * 2 + green(key) + ': ' + light_magenta(value)
            printNicely(line)
        except:
            debug_option()
            printNicely(red('Just can not get the default.'))
    # Delete specific config key in config file
    elif len(g['stuff'].split()) == 2 and g['stuff'].split()[-1] == 'drop':
        key = g['stuff'].split()[0]
        try:
            delete_config(key)
            printNicely(green('Config key is dropped.'))
        except:
            debug_option()
            printNicely(red('Just can not drop the key.'))
    # Set specific config
    elif len(g['stuff'].split()) == 3 and g['stuff'].split()[1] == '=':
        key = g['stuff'].split()[0]
        value = g['stuff'].split()[-1]
        if key == 'THEME' and not validate_theme(value):
            printNicely(red('Invalid theme\'s value.'))
            return
        try:
            set_config(key, value)
            # Keys that needs to be apply immediately
            if key == 'THEME':
                c['THEME'] = reload_theme(value, c['THEME'])
                g['decorated_name'] = lambda x: color_func(
                    c['DECORATED_NAME'])('[' + x + ']: ')
            elif key == 'PREFIX':
                g['PREFIX'] = u2str(emojize(format_prefix(
                    listname=g['listname'],
                    keyword=g['keyword']
                )))
            reload_config()
            printNicely(green('Updated successfully.'))
        except:
            debug_option()
            printNicely(red('Just can not set the key.'))
    else:
        printNicely(light_magenta('Sorry I can\'t understand.'))


def help_discover():
    """
    Discover the world
    """
    s = ' ' * 2
    # Discover the world
    usage = '\n'
    usage += s + grey(u'\u266A' + ' Discover the world \n')
    usage += s * 2 + light_green('trend') + ' will show global trending topics. ' + \
        'You can try ' + light_green('trend US') + ' or ' + \
        light_green('trend JP Tokyo') + '.\n'
    usage += s * 2 + light_green('home') + ' will show your timeline. ' + \
        light_green('home 7') + ' will show 7 tweets.\n'
    usage += s * 2 + light_green('me') + ' will show your latest tweets. ' + \
        light_green('me 2') + ' will show your last 2 tweets.\n'
    usage += s * 2 + \
        light_green('notification') + ' will show your recent notification.\n'
    usage += s * 2 + light_green('mentions') + ' will show mentions timeline. ' + \
        light_green('mentions 7') + ' will show 7 mention tweets.\n'
    usage += s * 2 + light_green('whois @mdo') + ' will show profile  of ' + \
        magenta('@mdo') + '.\n'
    usage += s * 2 + light_green('view @mdo') + \
        ' will show ' + magenta('@mdo') + '\'s home.\n'
    usage += s * 2 + light_green('s AKB48') + ' will search for "' + \
        light_yellow('AKB48') + '" and return 5 newest tweet. ' + \
        'Search can be performed with or without hashtag.\n'
    printNicely(usage)


def help_tweets():
    """
    Tweets
    """
    s = ' ' * 2
    # Tweet
    usage = '\n'
    usage += s + grey(u'\u266A' + ' Tweets \n')
    usage += s * 2 + light_green('t oops ') + \
        'will tweet "' + light_yellow('oops') + '" immediately.\n'
    usage += s * 2 + \
        light_green('rt 12 ') + ' will retweet to tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('quote 12 ') + ' will quote the tweet with ' + \
        light_yellow('[id=12]') + '. If no extra text is added, ' + \
        'the quote will be canceled.\n'
    usage += s * 2 + \
        light_green('allrt 12 20 ') + ' will list 20 newest retweet of the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + light_green('conversation 12') + ' will show the chain of ' + \
        'replies prior to the tweet with ' + light_yellow('[id=12]') + '.\n'
    usage += s * 2 + light_green('rep 12 oops') + ' will reply "' + \
        light_yellow('oops') + '" to the owner of the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + light_green('repall 12 oops') + ' will reply "' + \
        light_yellow('oops') + '" to all people in the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('fav 12 ') + ' will favorite the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('ufav 12 ') + ' will unfavorite tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('share 12 ') + ' will get the direct link of the tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + \
        light_green('del 12 ') + ' will delete tweet with ' + \
        light_yellow('[id=12]') + '.\n'
    usage += s * 2 + light_green('show image 12') + ' will show image in tweet with ' + \
        light_yellow('[id=12]') + ' in your OS\'s image viewer.\n'
    usage += s * 2 + light_green('open 12') + ' will open url in tweet with ' + \
        light_yellow('[id=12]') + ' in your OS\'s default browser.\n'
    usage += s * 2 + light_green('pt 12') + '  will add tweet with ' + \
        light_yellow('[id=12]') + ' in your Pocket list.\n'
    printNicely(usage)


def help_messages():
    """
    Messages
    """
    s = ' ' * 2
    # Direct message
    usage = '\n'
    usage += s + grey(u'\u266A' + ' Direct messages \n')
    usage += s * 2 + light_green('inbox') + ' will show inbox messages. ' + \
        light_green('inbox 7') + ' will show newest 7 messages.\n'
    usage += s * 2 + light_green('thread 2') + ' will show full thread with ' + \
        light_yellow('[thread_id=2]') + '.\n'
    usage += s * 2 + light_green('mes @dtvd88 hi') + ' will send a "hi" messege to ' + \
        magenta('@dtvd88') + '.\n'
    usage += s * 2 + light_green('trash 5') + ' will remove message with ' + \
        light_yellow('[message_id=5]') + '.\n'
    printNicely(usage)


def help_friends_and_followers():
    """
    Friends and Followers
    """
    s = ' ' * 2
    # Follower and following
    usage = '\n'
    usage += s + grey(u'\u266A' + ' Friends and followers \n')
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
    printNicely(usage)


def help_list():
    """
    Lists
    """
    s = ' ' * 2
    # Twitter list
    usage = '\n'
    usage += s + grey(u'\u266A' + ' Twitter list\n')
    usage += s * 2 + light_green('list') + \
        ' will show all lists you are belong to.\n'
    usage += s * 2 + light_green('list home') + \
        ' will show timeline of list. You will be asked for list\'s name.\n'
    usage += s * 2 + light_green('list all_mem') + \
        ' will show list\'s all members.\n'
    usage += s * 2 + light_green('list all_sub') + \
        ' will show list\'s all subscribers.\n'
    usage += s * 2 + light_green('list add') + \
        ' will add specific person to a list owned by you.' + \
        ' You will be asked for list\'s name and person\'s name.\n'
    usage += s * 2 + light_green('list rm') + \
        ' will remove specific person from a list owned by you.' + \
        ' You will be asked for list\'s name and person\'s name.\n'
    usage += s * 2 + light_green('list sub') + \
        ' will subscribe you to a specific list.\n'
    usage += s * 2 + light_green('list unsub') + \
        ' will unsubscribe you from a specific list.\n'
    usage += s * 2 + light_green('list own') + \
        ' will show all list owned by you.\n'
    usage += s * 2 + light_green('list new') + \
        ' will create a new list.\n'
    usage += s * 2 + light_green('list update') + \
        ' will update a list owned by you.\n'
    usage += s * 2 + light_green('list del') + \
        ' will delete a list owned by you.\n'
    printNicely(usage)


def help_stream():
    """
    Stream switch
    """
    s = ' ' * 2
    # Switch
    usage = '\n'
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
    usage += s * 2 + light_green('switch list') + \
        ' will switch to a Twitter list\'s stream. You will be asked for list name\n'
    printNicely(usage)


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
    usage += s + 'In addition, following commands are available right now:\n'
    # Twitter help section
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Twitter help\n')
    usage += s * 2 + light_green('h discover') + \
        ' will show help for discover commands.\n'
    usage += s * 2 + light_green('h tweets') + \
        ' will show help for tweets commands.\n'
    usage += s * 2 + light_green('h messages') + \
        ' will show help for messages commands.\n'
    usage += s * 2 + light_green('h friends_and_followers') + \
        ' will show help for friends and followers commands.\n'
    usage += s * 2 + light_green('h list') + \
        ' will show help for list commands.\n'
    usage += s * 2 + light_green('h stream') + \
        ' will show help for stream commands.\n'
    # Smart shell
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Smart shell\n')
    usage += s * 2 + light_green('111111 * 9 / 7') + ' or any math expression ' + \
        'will be evaluate by Python interpreter.\n'
    usage += s * 2 + 'Even ' + light_green('cal') + ' will show the calendar' + \
        ' for current month.\n'
    # Config
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Config \n')
    usage += s * 2 + light_green('theme') + ' will list available theme. ' + \
        light_green('theme monokai') + ' will apply ' + light_yellow('monokai') + \
        ' theme immediately.\n'
    usage += s * 2 + light_green('config') + ' will list all config.\n'
    usage += s * 3 + \
        light_green('config ASCII_ART') + ' will output current value of ' +\
        light_yellow('ASCII_ART') + ' config key.\n'
    usage += s * 3 + \
        light_green('config TREND_MAX default') + ' will output default value of ' + \
        light_yellow('TREND_MAX') + ' config key.\n'
    usage += s * 3 + \
        light_green('config CUSTOM_CONFIG drop') + ' will drop ' + \
        light_yellow('CUSTOM_CONFIG') + ' config key.\n'
    usage += s * 3 + \
        light_green('config IMAGE_ON_TERM = true') + ' will set value of ' + \
        light_yellow('IMAGE_ON_TERM') + ' config key to ' + \
        light_yellow('True') + '.\n'
    # Screening
    usage += '\n'
    usage += s + grey(u'\u266A' + ' Screening \n')
    usage += s * 2 + light_green('h') + ' will show this help again.\n'
    usage += s * 2 + light_green('p') + ' will pause the stream.\n'
    usage += s * 2 + light_green('r') + ' will unpause the stream.\n'
    usage += s * 2 + light_green('c') + ' will clear the screen.\n'
    usage += s * 2 + light_green('v') + ' will show version info.\n'
    usage += s * 2 + light_green('q') + ' will quit.\n'
    # End
    usage += '\n'
    usage += s + '-' * (int(w) - 4) + '\n'
    usage += s + 'Have fun and hang tight! \n'
    # Show help
    d = {
        'discover': help_discover,
        'tweets': help_tweets,
        'messages': help_messages,
        'friends_and_followers': help_friends_and_followers,
        'list': help_list,
        'stream': help_stream,
    }
    if g['stuff']:
        d.get(
            g['stuff'].strip(),
            lambda: printNicely(red('No such command.'))
        )()
    else:
        printNicely(usage)


def pause():
    """
    Pause stream display
    """
    g['pause'] = True
    printNicely(green('Stream is paused'))


def replay():
    """
    Replay stream
    """
    g['pause'] = False
    printNicely(green('Stream is running back now'))


def clear():
    """
    Clear screen
    """
    os.system('clear')


def quit():
    """
    Exit all
    """
    try:
        save_history()
        printNicely(green('See you next time :)'))
    except:
        pass
    sys.exit()


def reset():
    """
    Reset prefix of line
    """
    if g['reset']:
        if c.get('USER_JSON_ERROR'):
            printNicely(red('Your ~/.rainbow_config.json is messed up:'))
            printNicely(red('>>> ' + c['USER_JSON_ERROR']))
            printNicely('')
        printNicely(magenta('Need tips ? Type "h" and hit Enter key!'))
    g['reset'] = False
    try:
        printNicely(str(eval(g['cmd'])))
    except Exception:
        pass


# Command set
cmdset = [
    'switch',
    'trend',
    'home',
    'notification',
    'view',
    'mentions',
    't',
    'rt',
    'quote',
    'me',
    'allrt',
    'conversation',
    'fav',
    'rep',
    'repall',
    'del',
    'ufav',
    'share',
    's',
    'mes',
    'show',
    'open',
    'ls',
    'inbox',
    'thread',
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
    'list',
    'cal',
    'config',
    'theme',
    'h',
    'p',
    'r',
    'c',
    'v',
    'q',
    'pt',
]

# Handle function set
funcset = [
    switch,
    trend,
    home,
    notification,
    view,
    mentions,
    tweet,
    retweet,
    quote,
    view_my_tweets,
    allretweet,
    conversation,
    favorite,
    reply,
    reply_all,
    delete,
    unfavorite,
    share,
    search,
    message,
    show,
    urlopen,
    ls,
    inbox,
    thread,
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
    twitterlist,
    cal,
    config,
    theme,
    help,
    pause,
    replay,
    clear,
    upgrade_center,
    quit,
    pocket,
]


def process(cmd):
    """
    Process switch
    """
    return dict(zip(cmdset, funcset)).get(cmd, reset)


def listen():
    """
    Listen to user's input
    """
    d = dict(zip(
        cmdset,
        [
            ['public', 'mine', 'list'],  # switch
            [],  # trend
            [],  # home
            [],  # notification
            ['@'],  # view
            [],  # mentions
            [],  # tweet
            [],  # retweet
            [],  # quote
            [],  # view_my_tweets
            [],  # allretweet
            [],  # conversation
            [],  # favorite
            [],  # reply
            [],  # reply_all
            [],  # delete
            [],  # unfavorite
            [],  # url
            ['#'],  # search
            ['@'],  # message
            ['image'],  # show image
            [''],  # open url
            ['fl', 'fr'],  # list
            [],  # inbox
            [i for i in g['message_threads']],  # sent
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
            [
                'home',
                'all_mem',
                'all_sub',
                'add',
                'rm',
                'sub',
                'unsub',
                'own',
                'new',
                'update',
                'del'
            ],  # list
            [],  # cal
            [key for key in dict(get_all_config())],  # config
            g['themes'],  # theme
            [
                'discover',
                'tweets',
                'messages',
                'friends_and_followers',
                'list',
                'stream'
            ],  # help
            [],  # pause
            [],  # reconnect
            [],  # clear
            [],  # version
            [],  # quit
            [],  # pocket
        ]
    ))
    init_interactive_shell(d)
    read_history()
    reset()
    while True:
        try:
            # raw_input
            if g['prefix']:
                # Only use PREFIX as a string with raw_input
                line = raw_input(g['decorated_name'](g['PREFIX']))
            else:
                line = raw_input()
            # Save cmd to compare with readline buffer
            g['cmd'] = line.strip()
            # Get short cmd to pass to handle function
            try:
                cmd = line.split()[0]
            except:
                cmd = ''
            # Lock the semaphore
            c['lock'] = True
            # Save cmd to global variable and call process
            g['stuff'] = ' '.join(line.split()[1:])
            # Check tweet length
            # Process the command
            process(cmd)()
            # Not re-display
            if cmd in ['switch', 't', 'rt', 'rep']:
                g['prefix'] = False
            else:
                g['prefix'] = True
        except EOFError:
            printNicely('')
        except TwitterHTTPError as e:
            detail_twitter_error(e)
        except Exception:
            debug_option()
            printNicely(red('OMG something is wrong with Twitter API right now.'))
        finally:
            # Release the semaphore lock
            c['lock'] = False


def reconn_notice():
    """
    Notice when Hangup or Timeout
    """
    guide = light_magenta('You can use ') + \
        light_green('switch') + \
        light_magenta(' command to return to your stream.\n')
    guide += light_magenta('Type ') + \
        light_green('h stream') + \
        light_magenta(' for more details.')
    printNicely(guide)
    sys.stdout.write(g['decorated_name'](g['PREFIX']))
    sys.stdout.flush()


def stream(domain, args, name='Rainbow Stream'):
    """
    Track the stream
    """
    # The Logo
    art_dict = {
        c['USER_DOMAIN']: name,
        c['PUBLIC_DOMAIN']: args.track_keywords or 'Global',
        c['SITE_DOMAIN']: name,
    }
    if c['ASCII_ART']:
        ascii_art(art_dict.get(domain, name))
    # These arguments are optional:
    stream_args = dict(
        timeout=0.5,  # To check g['stream_stop'] after each 0.5 s
        block=True,
        heartbeat_timeout=c['HEARTBEAT_TIMEOUT'] * 60)
    # Track keyword
    query_args = dict()
    if args.track_keywords:
        query_args['track'] = args.track_keywords
    # Get stream
    stream = TwitterStream(
        auth=authen(),
        domain=domain,
        **stream_args)
    try:
        if domain == c['USER_DOMAIN']:
            tweet_iter = stream.user(**query_args)
        elif domain == c['SITE_DOMAIN']:
            tweet_iter = stream.site(**query_args)
        else:
            if args.track_keywords:
                tweet_iter = stream.statuses.filter(**query_args)
            else:
                tweet_iter = stream.statuses.sample()
        # Block new stream until other one exits
        StreamLock.acquire()
        g['stream_stop'] = False
        last_tweet_time = time.time()
        for tweet in tweet_iter:
            if tweet is None:
                printNicely('-- None --')
            elif tweet is Timeout:
                # Because the stream check for each 0.3s
                # so we shouldn't output anything here
                if(g['stream_stop']):
                    StreamLock.release()
                    break
            elif tweet is HeartbeatTimeout:
                printNicely('-- Heartbeat Timeout --')
                reconn_notice()
                StreamLock.release()
                break
            elif tweet is Hangup:
                printNicely('-- Hangup --')
                reconn_notice()
                StreamLock.release()
                break
            elif tweet.get('text'):
                # Slow down the stream by STREAM_DELAY config key
                if time.time() - last_tweet_time < c['STREAM_DELAY']:
                    continue
                last_tweet_time = time.time()
                # Check the semaphore pause and lock (stream process only)
                if g['pause']:
                    continue
                while c['lock']:
                    time.sleep(0.5)
                # Draw the tweet
                draw(
                    t=tweet,
                    keyword=args.track_keywords,
                    humanize=False,
                    fil=args.filter,
                    ig=args.ignore,
                )
                # Current readline buffer
                current_buffer = readline.get_line_buffer().strip()
                # There is an unexpected behaviour in MacOSX readline + Python 2:
                # after completely delete a word after typing it,
                # somehow readline buffer still contains
                # the 1st character of that word
                if current_buffer and g['cmd'] != current_buffer:
                    sys.stdout.write(
                        g['decorated_name'](g['PREFIX']) + current_buffer)
                    sys.stdout.flush()
                elif not c['HIDE_PROMPT']:
                    sys.stdout.write(g['decorated_name'](g['PREFIX']))
                    sys.stdout.flush()
            elif tweet.get('direct_message'):
                # Check the semaphore pause and lock (stream process only)
                if g['pause']:
                    continue
                while c['lock']:
                    time.sleep(0.5)
                print_message(tweet['direct_message'])
            elif tweet.get('event'):
                c['events'].append(tweet)
                print_event(tweet)
    except TwitterHTTPError as e:
        printNicely('')
        printNicely(
            magenta('We have connection problem with twitter stream API right now :('))
        detail_twitter_error(e)
        sys.stdout.write(g['decorated_name'](g['PREFIX']))
        sys.stdout.flush()
    except (URLError):
        printNicely(
            magenta('There seems to be a connection problem.'))
        save_history()
        sys.exit()


def spawn_public_stream(args, keyword=None):
    """
    Spawn a new public stream
    """
    # Only set keyword if specified
    if keyword:
        if keyword[0] == '#':
            keyword = keyword[1:]
        args.track_keywords = keyword
        g['keyword'] = keyword
    else:
        g['keyword'] = 'Global'
    g['PREFIX'] = u2str(emojize(format_prefix(keyword=g['keyword'])))
    g['listname'] = ''
    # Start new thread
    th = threading.Thread(
        target=stream,
        args=(
            c['PUBLIC_DOMAIN'],
            args))
    th.daemon = True
    th.start()


def spawn_list_stream(args, stuff=None):
    """
    Spawn a new list stream
    """
    try:
        owner, slug = check_slug(stuff)
    except:
        owner, slug = get_slug()

    # Force python 2 not redraw readline buffer
    listname = '/'.join([owner, slug])
    # Set the listname variable
    # and reset tracked keyword
    g['listname'] = listname
    g['keyword'] = ''
    g['PREFIX'] = g['cmd'] = u2str(emojize(format_prefix(
        listname=g['listname']
    )))
    printNicely(light_yellow('getting list members ...'))
    # Get members
    t = Twitter(auth=authen())
    members = []
    next_cursor = -1
    while next_cursor != 0:
        m = t.lists.members(
            slug=slug,
            owner_screen_name=owner,
            cursor=next_cursor,
            include_entities=False)
        for u in m['users']:
            members.append('@' + u['screen_name'])
        next_cursor = m['next_cursor']
    printNicely(light_yellow('... done.'))
    # Build thread filter array
    args.filter = members
    # Start new thread
    th = threading.Thread(
        target=stream,
        args=(
            c['USER_DOMAIN'],
            args,
            slug))
    th.daemon = True
    th.start()
    printNicely('')
    if args.filter:
        printNicely(cyan('Include: ' + str(len(args.filter)) + ' people.'))
    if args.ignore:
        printNicely(red('Ignore: ' + str(len(args.ignore)) + ' people.'))
    printNicely('')


def spawn_personal_stream(args, stuff=None):
    """
    Spawn a new personal stream
    """
    # Reset the tracked keyword and listname
    g['keyword'] = g['listname'] = ''
    # Reset prefix
    g['PREFIX'] = u2str(emojize(format_prefix()))
    # Start new thread
    th = threading.Thread(
        target=stream,
        args=(
            c['USER_DOMAIN'],
            args,
            g['original_name']))
    th.daemon = True
    th.start()


def fly():
    """
    Main function
    """
    # Initial
    args = parse_arguments()
    try:
        proxy_connect(args)
        init(args)
    # Twitter API connection problem
    except TwitterHTTPError as e:
        printNicely('')
        printNicely(
            magenta('We have connection problem with twitter REST API right now :('))
        detail_twitter_error(e)
        save_history()
        sys.exit()
    # Proxy connection problem
    except (socks.ProxyConnectionError, URLError):
        printNicely(
            magenta('There seems to be a connection problem.'))
        printNicely(
            magenta('You might want to check your proxy settings (host, port and type)!'))
        save_history()
        sys.exit()

    # Spawn stream thread
    target = args.stream.split()[0]
    if target == 'mine':
        spawn_personal_stream(args)
    else:
        try:
            stuff = args.stream.split()[1]
        except:
            stuff = None
        spawn_dict = {
            'public': spawn_public_stream,
            'list': spawn_list_stream,
        }
        spawn_dict.get(target)(args, stuff)

    # Start listen process
    time.sleep(0.5)
    g['reset'] = True
    g['prefix'] = True
    listen()
