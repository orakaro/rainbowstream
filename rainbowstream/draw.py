import random
import textwrap
import itertools
import requests
import locale
import arrow
import re
import os

from twitter.util import printNicely
from functools import wraps
from pyfiglet import figlet_format
from dateutil import parser
from .c_image import *
from .colors import *
from .config import *
from .py3patch import *
from .emoji import *

# Draw global variables
dg = {}


def init_cycle():
    """
    Init the cycle
    """
    colors_shuffle = [globals()[i.encode('utf8')]
                      if not str(i).isdigit()
                      else term_color(int(i))
                      for i in c['CYCLE_COLOR']]
    return itertools.cycle(colors_shuffle)


def start_cycle():
    """
    Notify from rainbow
    """
    dg['cyc'] = init_cycle()
    dg['cache'] = {}
    dg['humanize_unsupported'] = False


def order_rainbow(s):
    """
    Print a string with ordered color with each character
    """
    colors_shuffle = [globals()[i.encode('utf8')]
                      if not str(i).isdigit()
                      else term_color(int(i))
                      for i in c['CYCLE_COLOR']]
    colored = [colors_shuffle[i % 7](s[i]) for i in xrange(len(s))]
    return ''.join(colored)


def random_rainbow(s):
    """
    Print a string with random color with each character
    """
    colors_shuffle = [globals()[i.encode('utf8')]
                      if not str(i).isdigit()
                      else term_color(int(i))
                      for i in c['CYCLE_COLOR']]
    colored = [random.choice(colors_shuffle)(i) for i in s]
    return ''.join(colored)


def Memoize(func):
    """
    Memoize decorator
    """
    @wraps(func)
    def wrapper(*args):
        if args not in dg['cache']:
            dg['cache'][args] = func(*args)
        return dg['cache'][args]
    return wrapper


@Memoize
def cycle_color(s):
    """
    Cycle the colors_shuffle
    """
    return next(dg['cyc'])(s)


def ascii_art(text):
    """
    Draw the Ascii Art
    """
    fi = figlet_format(text, font='doom')
    print('\n'.join(
        [next(dg['cyc'])(i) for i in fi.split('\n')]
    ))


def check_config():
    """
    Check if config is changed
    """
    changed = False
    data = get_all_config()
    for key in c:
        if key in data:
            if data[key] != c[key]:
                changed = True
    if changed:
        reload_config()


def validate_theme(theme):
    """
    Validate a theme exists or not
    """
    # Theme changed check
    files = os.listdir(os.path.dirname(__file__) + '/colorset')
    themes = [f.split('.')[0] for f in files if f.split('.')[-1] == 'json']
    return theme in themes


def reload_theme(value, prev):
    """
    Check current theme and update if necessary
    """
    if value != prev:
        config = os.path.dirname(
            __file__) + '/colorset/' + value + '.json'
        # Load new config
        data = load_config(config)
        if data:
            for d in data:
                c[d] = data[d]
        # Restart color cycle and update config
        start_cycle()
        set_config('THEME', value)
        return value
    return prev


def color_func(func_name):
    """
    Call color function base on name
    """
    if str(func_name).isdigit():
        return term_color(int(func_name))
    return globals()[func_name]


def fallback_humanize(date, fallback_format=None, use_fallback=False):
    """
    Format date with arrow and a fallback format
    """
    # Convert to local timezone
    date = arrow.get(date).to('local')
    # Set default fallback format
    if not fallback_format:
        fallback_format = '%Y/%m/%d %H:%M:%S'
    # Determine using fallback format or not by a variable
    if use_fallback:
        return date.datetime.strftime(fallback_format)
    try:
        # Use Arrow's humanize function
        lang, encode = locale.getdefaultlocale()
        clock = date.humanize(locale=lang)
    except:
        # Notice at the 1st time only
        if not dg['humanize_unsupported']:
            dg['humanize_unsupported'] = True
            printNicely(
                light_magenta('Humanized date display method does not support your $LC_ALL.'))
        # Fallback when LC_ALL is not supported
        clock = date.datetime.strftime(fallback_format)
    return clock


def draw(t, keyword=None, humanize=True, noti=False, fil=[], ig=[]):
    """
    Draw the rainbow
    """
    # Check config
    check_config()

    # Retrieve tweet
    tid = t['id']
    text = t['text']
    screen_name = t['user']['screen_name']
    name = t['user']['name']
    created_at = t['created_at']
    favorited = t['favorited']
    retweet_count = t['retweet_count']
    favorite_count = t['favorite_count']
    date = parser.parse(created_at)
    try:
        clock_format = c['FORMAT']['TWEET']['CLOCK_FORMAT']
    except:
        clock_format = '%Y/%m/%d %H:%M:%S'
    clock = fallback_humanize(date, clock_format, not humanize)

    # Pull extended retweet text
    try:
        text = 'RT @' + t['retweeted_status']['user']['screen_name'] + ': ' +\
            t['retweeted_status']['text']
        # Display as a notification
        target = t['retweeted_status']['user']['screen_name']
        if all([target == c['original_name'], not noti]):
            # Add to evens for 'notification' command
            t['event'] = 'retweet'
            c['events'].append(t)
            notify_retweet(t)
            return
    except:
        pass

    # Unescape HTML character
    text = unescape(text)

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
    mytweet = screen_name == c['original_name']
    screen_name = '@' + screen_name
    fil = list(set((fil or []) + c['ONLY_LIST']))
    ig = list(set((ig or []) + c['IGNORE_LIST']))
    if fil and screen_name not in fil:
        return
    if ig and screen_name in ig:
        return

    # Get rainbow id
    if tid not in c['tweet_dict']:
        c['tweet_dict'].append(tid)
        rid = len(c['tweet_dict']) - 1
    else:
        rid = c['tweet_dict'].index(tid)

    # Format info
    name = cycle_color(name)
    if mytweet:
        nick = color_func(c['TWEET']['mynick'])(screen_name)
    else:
        nick = color_func(c['TWEET']['nick'])(screen_name)
    clock = clock
    id = str(rid)
    fav = ''
    if favorited:
        fav = color_func(c['TWEET']['favorited'])(u'\u2605')

    tweet = text.split()
    # Replace url
    if expanded_url:
        for index in xrange(len(expanded_url)):
            tweet = lmap(
                lambda x: expanded_url[index]
                if x == url[index]
                else x,
                tweet)
    # Highlight RT
    tweet = lmap(
        lambda x: color_func(c['TWEET']['rt'])(x)
        if x == 'RT'
        else x,
        tweet)
    # Highlight screen_name
    tweet = lmap(lambda x: cycle_color(x) if x[0] == '@' else x, tweet)
    # Highlight link
    tweet = lmap(
        lambda x: color_func(c['TWEET']['link'])(x)
        if x.startswith('http')
        else x,
        tweet)
    # Highlight hashtag
    tweet = lmap(
        lambda x: color_func(c['TWEET']['hashtag'])(x)
        if x.startswith('#')
        else x,
        tweet)
    # Highlight my tweet
    if mytweet:
        tweet = [color_func(c['TWEET']['mytweet'])(x)
                 for x in tweet
                 if not any([
                     x == 'RT',
                     x.startswith('http'),
                     x.startswith('#')])
                 ]
    # Highlight keyword
    tweet = ' '.join(tweet)
    if keyword:
        roj = re.search(keyword, tweet, re.IGNORECASE)
        if roj:
            occur = roj.group()
            ary = tweet.split(occur)
            delimiter = color_func(c['TWEET']['keyword'])(occur)
            tweet = delimiter.join(ary)

    # Load config formater
    formater = ''
    try:
        formater = c['FORMAT']['TWEET']['DISPLAY']
        formater = name.join(formater.split('#name'))
        formater = nick.join(formater.split('#nick'))
        formater = fav.join(formater.split('#fav'))
        formater = tweet.join(formater.split('#tweet'))
        # Change clock word
        word = [wo for wo in formater.split() if '#clock' in wo][0]
        delimiter = color_func(c['TWEET']['clock'])(
            clock.join(word.split('#clock')))
        formater = delimiter.join(formater.split(word))
        # Change id word
        word = [wo for wo in formater.split() if '#id' in wo][0]
        delimiter = color_func(c['TWEET']['id'])(id.join(word.split('#id')))
        formater = delimiter.join(formater.split(word))
        # Change retweet count word
        word = [wo for wo in formater.split() if '#rt_count' in wo][0]
        delimiter = color_func(c['TWEET']['retweet_count'])(
            str(retweet_count).join(word.split('#rt_count')))
        formater = delimiter.join(formater.split(word))
        # Change favorites count word
        word = [wo for wo in formater.split() if '#fa_count' in wo][0]
        delimiter = color_func(c['TWEET']['favorite_count'])(
            str(favorite_count).join(word.split('#fa_count')))
        formater = delimiter.join(formater.split(word))
        formater = emojize(formater)
    except:
        pass

    # Add spaces in begining of line if this is inside a notification
    if noti:
        formater = '\n  '.join(formater.split('\n'))
        # Reformat
        if formater.startswith('\n'):
            formater = formater[1:]

    # Draw
    printNicely(formater)

    # Display Image
    if c['IMAGE_ON_TERM'] and media_url:
        for mu in media_url:
            try:
                response = requests.get(mu)
                image_to_display(BytesIO(response.content))
            except Exception:
                printNicely(red('Sorry, image link is broken'))


def print_threads(d):
    """
    Print threads of messages
    """
    id = 1
    rel = {}
    for partner in d:
        messages = d[partner]
        count = len(messages)
        screen_name = '@' + partner[0]
        name = partner[1]
        screen_name = color_func(c['MESSAGE']['partner'])(screen_name)
        name = cycle_color(name)
        thread_id = color_func(c['MESSAGE']['id'])('thread_id:' + str(id))
        line = ' ' * 2 + name + ' ' + screen_name + \
            ' (' + str(count) + ' message) ' + thread_id
        printNicely(line)
        rel[id] = partner
        id += 1
    dg['thread'] = d
    return rel


def print_thread(partner, me_nick, me_name):
    """
    Print a thread of messages
    """
    # Sort messages by time
    messages = dg['thread'][partner]
    messages.sort(key=lambda x: parser.parse(x['created_at']))
    # Use legacy display on non-ascii text message
    ms = [m['text'] for m in messages]
    ums = [m for m in ms if not all(ord(c) < 128 for c in m)]
    if ums:
        for m in messages:
            print_message(m)
        printNicely('')
        return
    # Print the first line
    dg['frame_margin'] = margin = 2
    partner_nick = partner[0]
    partner_name = partner[1]
    left_size = len(partner_nick) + len(partner_name) + 2
    right_size = len(me_nick) + len(me_name) + 2
    partner_nick = color_func(c['MESSAGE']['partner'])('@' + partner_nick)
    partner_name = cycle_color(partner_name)
    me_screen_name = color_func(c['MESSAGE']['me'])('@' + me_nick)
    me_name = cycle_color(me_name)
    left = ' ' * margin + partner_name + ' ' + partner_nick
    right = me_name + ' ' + me_screen_name + ' ' * margin
    h, w = os.popen('stty size', 'r').read().split()
    w = int(w)
    line = '{}{}{}'.format(
        left, ' ' * (w - left_size - right_size - 2 * margin), right)
    printNicely('')
    printNicely(line)
    printNicely('')
    # Print messages
    for m in messages:
        if m['sender_screen_name'] == me_nick:
            print_right_message(m)
        elif m['recipient_screen_name'] == me_nick:
            print_left_message(m)


def print_right_message(m):
    """
    Print a message on the right of screen
    """
    h, w = os.popen('stty size', 'r').read().split()
    w = int(w)
    frame_width = w // 3 - dg['frame_margin']
    frame_width = max(c['THREAD_MIN_WIDTH'], frame_width)
    step = frame_width - 2 * dg['frame_margin']
    slicing = textwrap.wrap(m['text'], step)
    spaces = w - frame_width - dg['frame_margin']
    dotline = ' ' * spaces + '-' * frame_width
    dotline = color_func(c['MESSAGE']['me_frame'])(dotline)
    # Draw the frame
    printNicely(dotline)
    for line in slicing:
        fill = step - len(line)
        screen_line = ' ' * spaces + '| ' + line + ' ' * fill + ' '
        if slicing[-1] == line:
            screen_line = screen_line + ' >'
        else:
            screen_line = screen_line + '|'
        screen_line = color_func(c['MESSAGE']['me_frame'])(screen_line)
        printNicely(screen_line)
    printNicely(dotline)
    # Format clock
    date = parser.parse(m['created_at'])
    date = arrow.get(date).to('local').datetime
    clock_format = '%Y/%m/%d %H:%M:%S'
    try:
        clock_format = c['FORMAT']['MESSAGE']['CLOCK_FORMAT']
    except:
        pass
    clock = date.strftime(clock_format)
    # Format id
    if m['id'] not in c['message_dict']:
        c['message_dict'].append(m['id'])
        rid = len(c['message_dict']) - 1
    else:
        rid = c['message_dict'].index(m['id'])
    id = str(rid)
    # Print meta
    formater = ''
    try:
        virtual_meta = formater = c['THREAD_META_RIGHT']
        virtual_meta = clock.join(virtual_meta.split('#clock'))
        virtual_meta = id.join(virtual_meta.split('#id'))
        # Change clock word
        word = [wo for wo in formater.split() if '#clock' in wo][0]
        delimiter = color_func(c['MESSAGE']['clock'])(
            clock.join(word.split('#clock')))
        formater = delimiter.join(formater.split(word))
        # Change id word
        word = [wo for wo in formater.split() if '#id' in wo][0]
        delimiter = color_func(c['MESSAGE']['id'])(id.join(word.split('#id')))
        formater = delimiter.join(formater.split(word))
        formater = emojize(formater)
    except Exception:
        printNicely(red('Wrong format in config.'))
        return
    meta = formater
    line = ' ' * (w - len(virtual_meta) - dg['frame_margin']) + meta
    printNicely(line)


def print_left_message(m):
    """
    Print a message on the left of screen
    """
    h, w = os.popen('stty size', 'r').read().split()
    w = int(w)
    frame_width = w // 3 - dg['frame_margin']
    frame_width = max(c['THREAD_MIN_WIDTH'], frame_width)
    step = frame_width - 2 * dg['frame_margin']
    slicing = textwrap.wrap(m['text'], step)
    spaces = dg['frame_margin']
    dotline = ' ' * spaces + '-' * frame_width
    dotline = color_func(c['MESSAGE']['partner_frame'])(dotline)
    # Draw the frame
    printNicely(dotline)
    for line in slicing:
        fill = step - len(line)
        screen_line = ' ' + line + ' ' * fill + ' |'
        if slicing[-1] == line:
            screen_line = ' ' * (spaces - 1) + '< ' + screen_line
        else:
            screen_line = ' ' * spaces + '|' + screen_line
        screen_line = color_func(c['MESSAGE']['partner_frame'])(screen_line)
        printNicely(screen_line)
    printNicely(dotline)
    # Format clock
    date = parser.parse(m['created_at'])
    date = arrow.get(date).to('local').datetime
    clock_format = '%Y/%m/%d %H:%M:%S'
    try:
        clock_format = c['FORMAT']['MESSAGE']['CLOCK_FORMAT']
    except:
        pass
    clock = date.strftime(clock_format)
    # Format id
    if m['id'] not in c['message_dict']:
        c['message_dict'].append(m['id'])
        rid = len(c['message_dict']) - 1
    else:
        rid = c['message_dict'].index(m['id'])
    id = str(rid)
    # Print meta
    formater = ''
    try:
        virtual_meta = formater = c['THREAD_META_LEFT']
        virtual_meta = clock.join(virtual_meta.split('#clock'))
        virtual_meta = id.join(virtual_meta.split('#id'))
        # Change clock word
        word = [wo for wo in formater.split() if '#clock' in wo][0]
        delimiter = color_func(c['MESSAGE']['clock'])(
            clock.join(word.split('#clock')))
        formater = delimiter.join(formater.split(word))
        # Change id word
        word = [wo for wo in formater.split() if '#id' in wo][0]
        delimiter = color_func(c['MESSAGE']['id'])(id.join(word.split('#id')))
        formater = delimiter.join(formater.split(word))
        formater = emojize(formater)
    except Exception:
        printNicely(red('Wrong format in config.'))
        return
    meta = formater
    line = ' ' * dg['frame_margin'] + meta
    printNicely(line)


def print_message(m):
    """
    Print direct message
    """
    # Retrieve message
    sender_screen_name = '@' + m['sender_screen_name']
    sender_name = m['sender']['name']
    text = unescape(m['text'])
    recipient_screen_name = '@' + m['recipient_screen_name']
    recipient_name = m['recipient']['name']
    mid = m['id']
    date = parser.parse(m['created_at'])
    date = arrow.get(date).to('local').datetime
    clock_format = '%Y/%m/%d %H:%M:%S'
    try:
        clock_format = c['FORMAT']['MESSAGE']['CLOCK_FORMAT']
    except:
        pass
    clock = date.strftime(clock_format)

    # Get rainbow id
    if mid not in c['message_dict']:
        c['message_dict'].append(mid)
        rid = len(c['message_dict']) - 1
    else:
        rid = c['message_dict'].index(mid)

    # Draw
    sender_name = cycle_color(sender_name)
    sender_nick = color_func(c['MESSAGE']['sender'])(sender_screen_name)
    recipient_name = cycle_color(recipient_name)
    recipient_nick = color_func(
        c['MESSAGE']['recipient'])(recipient_screen_name)
    to = color_func(c['MESSAGE']['to'])('>>>')
    clock = clock
    id = str(rid)

    text = ''.join(lmap(lambda x: x + '  ' if x == '\n' else x, text))

    # Load config formater
    try:
        formater = c['FORMAT']['MESSAGE']['DISPLAY']
        formater = sender_name.join(formater.split("#sender_name"))
        formater = sender_nick.join(formater.split("#sender_nick"))
        formater = to.join(formater.split("#to"))
        formater = recipient_name.join(formater.split("#recipient_name"))
        formater = recipient_nick.join(formater.split("#recipient_nick"))
        formater = text.join(formater.split("#message"))
        # Change clock word
        word = [wo for wo in formater.split() if '#clock' in wo][0]
        delimiter = color_func(c['MESSAGE']['clock'])(
            clock.join(word.split('#clock')))
        formater = delimiter.join(formater.split(word))
        # Change id word
        word = [wo for wo in formater.split() if '#id' in wo][0]
        delimiter = color_func(c['MESSAGE']['id'])(id.join(word.split('#id')))
        formater = delimiter.join(formater.split(word))
        formater = emojize(formater)
    except:
        printNicely(red('Wrong format in config.'))
        return

    # Draw
    printNicely(formater)


def notify_retweet(t):
    """
    Notify a retweet
    """
    source = t['user']
    created_at = t['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'retweeted your tweet')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    draw(t=t['retweeted_status'], noti=True)


def notify_favorite(e):
    """
    Notify a favorite event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    target_object = e['target_object']
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'favorited your tweet')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    draw(t=target_object, noti=True)


def notify_unfavorite(e):
    """
    Notify a unfavorite event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    target_object = e['target_object']
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'unfavorited your tweet')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    draw(t=target_object, noti=True)


def notify_follow(e):
    """
    Notify a follow event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'followed you')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)


def notify_list_member_added(e):
    """
    Notify a list_member_added event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    target_object = [e['target_object']]  # list of Twitter list
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'added you to a list')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    print_list(target_object, noti=True)


def notify_list_member_removed(e):
    """
    Notify a list_member_removed event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    target_object = [e['target_object']]  # list of Twitter list
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'removed you from a list')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    print_list(target_object, noti=True)


def notify_list_user_subscribed(e):
    """
    Notify a list_user_subscribed event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    target_object = [e['target_object']]  # list of Twitter list
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'subscribed to your list')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    print_list(target_object, noti=True)


def notify_list_user_unsubscribed(e):
    """
    Notify a list_user_unsubscribed event
    """
    # Retrieve info
    target = e['target']
    if target['screen_name'] != c['original_name']:
        return
    source = e['source']
    target_object = [e['target_object']]  # list of Twitter list
    created_at = e['created_at']
    # Format
    source_user = cycle_color(source['name']) + \
        color_func(c['NOTIFICATION']['source_nick'])(
        ' @' + source['screen_name'])
    notify = color_func(c['NOTIFICATION']['notify'])(
        'unsubscribed from your list')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
    clock = color_func(c['NOTIFICATION']['clock'])(clock)
    meta = c['NOTIFY_FORMAT']
    meta = source_user.join(meta.split('#source_user'))
    meta = notify.join(meta.split('#notify'))
    meta = clock.join(meta.split('#clock'))
    meta = emojize(meta)
    # Output
    printNicely('')
    printNicely(meta)
    print_list(target_object, noti=True)


def print_event(e):
    """
    Notify an event
    """
    event_dict = {
        'retweet': notify_retweet,
        'favorite': notify_favorite,
        'unfavorite': notify_unfavorite,
        'follow': notify_follow,
        'list_member_added': notify_list_member_added,
        'list_member_removed': notify_list_member_removed,
        'list_user_subscribed': notify_list_user_subscribed,
        'list_user_unsubscribed': notify_list_user_unsubscribed,
    }
    event_dict.get(e['event'], lambda *args: None)(e)


def show_profile(u):
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
        lmap(lambda x: x + ' ' * 4 if x == '\n' else x, description))
    description = color_func(c['PROFILE']['description'])(description)
    location = 'Location : ' + color_func(c['PROFILE']['location'])(location)
    url = 'URL : ' + (color_func(c['PROFILE']['url'])(url) if url else '')
    date = parser.parse(created_at)
    clock = fallback_humanize(date)
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
    if c['IMAGE_ON_TERM']:
        try:
            response = requests.get(profile_image_url)
            image_to_display(BytesIO(response.content))
        except:
            pass
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


def print_list(group, noti=False):
    """
    Display a list
    """
    for grp in group:
        # Format
        name = grp['full_name']
        name = color_func(c['GROUP']['name'])(name + ' : ')
        member = str(grp['member_count'])
        member = color_func(c['GROUP']['member'])(member + ' member')
        subscriber = str(grp['subscriber_count'])
        subscriber = color_func(
            c['GROUP']['subscriber'])(
            subscriber +
            ' subscriber')
        description = grp['description'].strip()
        description = color_func(c['GROUP']['description'])(description)
        mode = grp['mode']
        mode = color_func(c['GROUP']['mode'])('Type: ' + mode)
        created_at = grp['created_at']
        date = parser.parse(created_at)
        clock = fallback_humanize(date)
        clock = 'Created at ' + color_func(c['GROUP']['clock'])(clock)

        prefix = ' ' * 2
        # Add spaces in begining of line if this is inside a notification
        if noti:
            prefix = ' ' * 2 + prefix
        # Create lines
        line1 = prefix + name + member + '  ' + subscriber
        line2 = prefix + ' ' * 2 + description
        line3 = prefix + ' ' * 2 + mode
        line4 = prefix + ' ' * 2 + clock

        # Display
        printNicely('')
        printNicely(line1)
        printNicely(line2)
        printNicely(line3)
        printNicely(line4)

    if not noti:
        printNicely('')


def show_calendar(month, date, rel):
    """
    Show the calendar in rainbow mode
    """
    month = random_rainbow(month)
    date = ' '.join([cycle_color(i) for i in date.split(' ')])
    today = str(int(os.popen('date +\'%d\'').read().strip()))
    # Display
    printNicely(month)
    printNicely(date)
    for line in rel:
        ary = line.split(' ')
        ary = lmap(
            lambda x: color_func(c['CAL']['today'])(x)
            if x == today
            else color_func(c['CAL']['days'])(x),
            ary)
        printNicely(' '.join(ary))


def format_quote(tweet):
    """
    Quoting format
    """
    # Retrieve info
    screen_name = '@' + tweet['user']['screen_name']
    text = tweet['text']
    # Validate quote format
    if '#owner' not in c['QUOTE_FORMAT']:
        printNicely(light_magenta('Quote should contains #owner'))
        return False
    if '#comment' not in c['QUOTE_FORMAT']:
        printNicely(light_magenta('Quote format should have #comment'))
        return False
    # Build formater
    formater = ''
    try:
        formater = c['QUOTE_FORMAT']
        formater = screen_name.join(formater.split('#owner'))
        formater = text.join(formater.split('#tweet'))
        formater = u2str(formater)
        formater = emojize(formater)
    except:
        pass
    # Highlight like a tweet
    notice = formater.split()
    notice = lmap(
        lambda x: light_green(x)
        if x == '#comment'
        else x,
        notice)
    notice = lmap(
        lambda x: color_func(c['TWEET']['rt'])(x)
        if x == 'RT'
        else x,
        notice)
    notice = lmap(lambda x: cycle_color(x) if x[0] == '@' else x, notice)
    notice = lmap(
        lambda x: color_func(c['TWEET']['link'])(x)
        if x[0:4] == 'http'
        else x,
        notice)
    notice = lmap(
        lambda x: color_func(c['TWEET']['hashtag'])(x)
        if x.startswith('#')
        else x,
        notice)
    notice = ' '.join(notice)
    # Notice
    notice = light_magenta('Quoting: "') + notice + light_magenta('"')
    printNicely(notice)
    return formater


# Start the color cycle
start_cycle()
