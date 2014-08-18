"""
Colorful user's timeline stream
"""
import os
import os.path
import sys
import signal
import argparse
import time
import threading
import requests
import webbrowser

from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from twitter.api import *
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.util import printNicely

from .draw import *
from .colors import *
from .config import *
from .consumer import *
from .interactive import *
from .c_image import *
from .py3patch import *

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


def init(args):
    """
    Init function
    """
    # Handle Ctrl C
    ctrl_c_handler = lambda signum, frame: quit()
    signal.signal(signal.SIGINT, ctrl_c_handler)
    # Get name
    t = Twitter(auth=authen())
    name = '@' + t.account.verify_credentials()['screen_name']
    if not get_config('PREFIX'):
        set_config('PREFIX', name)
    g['original_name'] = name[1:]
    g['decorated_name'] = lambda x: color_func(
        c['DECORATED_NAME'])('[' + x + ']: ')
    # Theme init
    files = os.listdir(os.path.dirname(__file__) + '/colorset')
    themes = [f.split('.')[0] for f in files if f.split('.')[-1] == 'json']
    g['themes'] = themes
    # Startup cmd
    g['cmd'] = ''
    # Semaphore init
    c['lock'] = False
    c['pause'] = False
    # Init tweet dict and message dict
    c['tweet_dict'] = []
    c['message_dict'] = []
    # Image on term
    c['IMAGE_ON_TERM'] = args.image_on_term
    set_config('IMAGE_ON_TERM', str(c['IMAGE_ON_TERM']))
    # Mute dict
    c['IGNORE_LIST'] += build_mute_dict()


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
            # Kill old thread
            g['stream_stop'] = True
            args.track_keywords = keyword
            # Start new thread
            th = threading.Thread(
                target=stream,
                args=(
                    c['PUBLIC_DOMAIN'],
                    args))
            th.daemon = True
            th.start()
        # Personal stream
        elif target == 'mine':
            # Kill old thread
            g['stream_stop'] = True
            # Start new thread
            th = threading.Thread(
                target=stream,
                args=(
                    c['USER_DOMAIN'],
                    args,
                    g['original_name']))
            th.daemon = True
            th.start()
        printNicely('')
        if args.filter:
            printNicely(cyan('Only: ' + str(args.filter)))
        if args.ignore:
            printNicely(red('Ignore: ' + str(args.ignore)))
        printNicely('')
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
        draw(t=tweet)
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
            draw(t=tweet)
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
        draw(t=tweet)
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
    tweet = t.statuses.show(id=tid)
    # Get formater
    formater = format_quote(tweet)
    if not formater:
        return
    # Get comment
    prefix = light_magenta('Compose your ') + light_green('#comment: ')
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
    rt_ary = t.statuses.retweets(id=tid, count=num)
    if not rt_ary:
        printNicely(magenta('This tweet has no retweet.'))
        return
    for tweet in reversed(rt_ary):
        draw(t=tweet)
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
    tid = c['tweet_dict'][id]
    t.favorites.create(_id=tid, include_entities=False)
    printNicely(green('Favorited.'))
    draw(t.statuses.show(id=tid))
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
    status = '@' + user + ' ' + str2u(status)
    t.statuses.update(status=status, in_reply_to_status_id=tid)


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
    draw(t.statuses.show(id=tid))
    printNicely('')


def search():
    """
    Search
    """
    t = Twitter(auth=authen())
    g['stuff'] = g['stuff'].strip()
    rel = t.search.tweets(q=g['stuff'])['statuses']
    if rel:
        printNicely('Newest tweets:')
        for i in reversed(xrange(c['SEARCH_MAX_RECORD'])):
            draw(t=rel[i],
                 keyword=g['stuff'])
        printNicely('')
    else:
        printNicely(magenta('I\'m afraid there is no result'))


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
        tid = c['tweet_dict'][id]
        tweet = t.statuses.show(id=tid)
        media = tweet['entities']['media']
        for m in media:
            res = requests.get(m['media_url'])
            img = Image.open(BytesIO(res.content))
            img.show()
    except:
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
        link_ary = [
            u for u in tweet['text'].split() if u.startswith('http://')]
        if not link_ary:
            printNicely(light_magenta('No url here @.@!'))
            return
        for link in link_ary:
            webbrowser.open(link)
    except:
        printNicely(red('Sorry I can\'t open url in this tweet.'))


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
    printNicely('All: ' + str(len(rel)) + ' ' + d[target] + '.')
    for name in rel:
        user = '  ' + cycle_color(name)
        user += color_func(c['TWEET']['nick'])(' ' + rel[name] + ' ')
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
        id = int(g['stuff'].split()[0])
    except:
        printNicely(red('Sorry I can\'t understand.'))
    mid = c['message_dict'][id]
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
            show_profile(user)
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
        try:
            rel = t.mutes.users.create(screen_name=screen_name[1:])
            if isinstance(rel, dict):
                printNicely(green(screen_name + ' is muted.'))
                c['IGNORE_LIST'] += [unc(screen_name)]
                c['IGNORE_LIST'] = list(set(c['IGNORE_LIST']))
            else:
                printNicely(red(rel))
        except:
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
    Get Slug Decorator
    """
    # Get list name
    list_name = raw_input(light_magenta('Give me the list\'s name: '))
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
    for tweet in res:
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
    user_name = raw_input(light_magenta('Give me name of the newbie: '))
    if user_name.startswith('@'):
        user_name = user_name[1:]
    try:
        t.lists.members.create(
            slug=slug,
            owner_screen_name=owner,
            screen_name=user_name)
        printNicely(green('Added.'))
    except:
        printNicely(light_magenta('I\'m sorry we can not add him/her.'))


def list_remove(t):
    """
    Remove specific user from a list
    """
    owner, slug = get_slug()
    # Remove
    user_name = raw_input(light_magenta('Give me name of the unlucky one: '))
    if user_name.startswith('@'):
        user_name = user_name[1:]
    try:
        t.lists.members.destroy(
            slug=slug,
            owner_screen_name=owner,
            screen_name=user_name)
        printNicely(green('Gone.'))
    except:
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
    name = raw_input(light_magenta('New list\'s name: '))
    mode = raw_input(light_magenta('New list\'s mode (public/private): '))
    description = raw_input(light_magenta('New list\'s description: '))
    try:
        t.lists.create(
            name=name,
            mode=mode,
            description=description)
        printNicely(green(name + ' list is created.'))
    except:
        printNicely(red('Oops something is wrong with Twitter :('))


def list_update(t):
    """
    Update a list
    """
    slug = raw_input(light_magenta('Your list that you want to update: '))
    name = raw_input(light_magenta('Update name (leave blank to unchange): '))
    mode = raw_input(light_magenta('Update mode (public/private): '))
    description = raw_input(light_magenta('Update description: '))
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
        printNicely(red('Oops something is wrong with Twitter :('))


def list_delete(t):
    """
    Delete a list
    """
    slug = raw_input(light_magenta('Your list that you want to update: '))
    try:
        t.lists.destroy(
            slug='-'.join(slug.split()),
            owner_screen_name=g['original_name'])
        printNicely(green(slug + ' list is deleted.'))
    except:
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


def cal():
    """
    Unix's command `cal`
    """
    # Format
    rel = os.popen('cal').read().split('\n')
    month = rel.pop(0)
    date = rel.pop(0)
    show_calendar(month, date, rel)


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
        except Exception as e:
            printNicely(red(e))
    # Delete specific config key in config file
    elif len(g['stuff'].split()) == 2 and g['stuff'].split()[-1] == 'drop':
        key = g['stuff'].split()[0]
        try:
            delete_config(key)
            printNicely(green('Config key is dropped.'))
        except Exception as e:
            printNicely(red(e))
    # Set specific config
    elif len(g['stuff'].split()) == 3 and g['stuff'].split()[1] == '=':
        key = g['stuff'].split()[0]
        value = g['stuff'].split()[-1]
        if key == 'THEME' and not validate_theme(value):
            printNicely(red('Invalid theme\'s value.'))
            return
        try:
            set_config(key, value)
            # Apply theme immediately
            if key == 'THEME':
                c['THEME'] = reload_theme(value, c['THEME'])
                g['decorated_name'] = lambda x: color_func(
                    c['DECORATED_NAME'])('[' + x + ']: ')
            reload_config()
            printNicely(green('Updated successfully.'))
        except Exception as e:
            printNicely(red(e))
    else:
        printNicely(light_magenta('Sorry I can\'s understand.'))


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
    usage += s * 2 + light_green('open 12') + ' will open url in tweet with ' + \
        light_yellow('[id=12]') + ' in your OS\'s default browser.\n'
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
    usage += s * 2 + light_green('sent') + ' will show sent messages. ' + \
        light_green('sent 7') + ' will show newest 7 messages.\n'
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
    usage += s * 2 + light_green('switch mine -d') + \
        ' will use the config\'s ONLY_LIST and IGNORE_LIST.\n'
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
    usage += s + 'In addtion, following commands are available right now:\n'
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
    c['pause'] = True
    printNicely(green('Stream is paused'))


def replay():
    """
    Replay stream
    """
    c['pause'] = False
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
    'view',
    'mentions',
    't',
    'rt',
    'quote',
    'allrt',
    'fav',
    'rep',
    'del',
    'ufav',
    's',
    'mes',
    'show',
    'open',
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
    'list',
    'cal',
    'config',
    'theme',
    'h',
    'p',
    'r',
    'c',
    'q'
]

# Handle function set
funcset = [
    switch,
    trend,
    home,
    view,
    mentions,
    tweet,
    retweet,
    quote,
    allretweet,
    favorite,
    reply,
    delete,
    unfavorite,
    search,
    message,
    show,
    urlopen,
    ls,
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
    twitterlist,
    cal,
    config,
    theme,
    help,
    pause,
    replay,
    clear,
    quit
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
            ['public', 'mine'],  # switch
            [],  # trend
            [],  # home
            ['@'],  # view
            [],  # mentions
            [],  # tweet
            [],  # retweet
            [],  # quote
            [],  # allretweet
            [],  # favorite
            [],  # reply
            [],  # delete
            [],  # unfavorite
            ['#'],  # search
            ['@'],  # message
            ['image'],  # show image
            [''],  # open url
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
            [],  # quit
        ]
    ))
    init_interactive_shell(d)
    read_history()
    reset()
    while True:
        # raw_input
        if g['prefix']:
            line = raw_input(g['decorated_name'](c['PREFIX']))
        else:
            line = raw_input()
        # Save cmd to compare with readline buffer
        g['cmd'] = line.strip()
        # Get short cmd to pass to handle function
        try:
            cmd = line.split()[0]
        except:
            cmd = ''
        try:
            # Lock the semaphore
            c['lock'] = True
            # Save cmd to global variable and call process
            g['stuff'] = ' '.join(line.split()[1:])
            # Process the command
            process(cmd)()
            # Not re-display
            if cmd in ['switch', 't', 'rt', 'rep']:
                g['prefix'] = False
            else:
                g['prefix'] = True
            # Release the semaphore lock
            c['lock'] = False
        except Exception:
            printNicely(red('OMG something is wrong with Twitter right now.'))


def stream(domain, args, name='Rainbow Stream'):
    """
    Track the stream
    """
    # The Logo
    art_dict = {
        c['USER_DOMAIN']: name,
        c['PUBLIC_DOMAIN']: args.track_keywords,
        c['SITE_DOMAIN']: name,
    }
    if c['ASCII_ART']:
        ascii_art(art_dict[domain])
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
        for tweet in tweet_iter:
            if tweet is None:
                printNicely("-- None --")
            elif tweet is Timeout:
                if(g['stream_stop']):
                    StreamLock.release()
                    break
            elif tweet is HeartbeatTimeout:
                printNicely("-- Heartbeat Timeout --")
                guide = light_magenta("You can use ") + \
                    light_green("switch") + \
                    light_magenta(" command to return to your stream.\n")
                guide += light_magenta("Type ") + \
                    light_green("h stream") + \
                    light_magenta(" for more details.")
                printNicely(guide)
                sys.stdout.write(g['decorated_name'](c['PREFIX']))
                sys.stdout.flush()
                StreamLock.release()
                break
            elif tweet is Hangup:
                printNicely("-- Hangup --")
            elif tweet.get('text'):
                draw(
                    t=tweet,
                    keyword=args.track_keywords,
                    check_semaphore=True,
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
                        g['decorated_name'](c['PREFIX']) + str2u(current_buffer))
                    sys.stdout.flush()
                elif not c['HIDE_PROMPT']:
                    sys.stdout.write(g['decorated_name'](c['PREFIX']))
                    sys.stdout.flush()
            elif tweet.get('direct_message'):
                print_message(tweet['direct_message'], check_semaphore=True)
    except TwitterHTTPError:
        printNicely('')
        printNicely(
            magenta("We have maximum connection problem with twitter'stream API right now :("))


def fly():
    """
    Main function
    """
    # Initial
    args = parse_arguments()
    try:
        init(args)
    except TwitterHTTPError:
        printNicely('')
        printNicely(
            magenta("We have connection problem with twitter'stream API right now :("))
        printNicely(magenta("Let's try again later."))
        save_history()
        sys.exit()
    # Spawn stream thread
    th = threading.Thread(
        target=stream,
        args=(
            c['USER_DOMAIN'],
            args,
            g['original_name']))
    th.daemon = True
    th.start()
    # Start listen process
    time.sleep(0.5)
    g['reset'] = True
    g['prefix'] = True
    listen()
