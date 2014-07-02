from .colors import *
import json
import os
import os.path

# 'search': max search record
SEARCH_MAX_RECORD = 5
# 'home': default number of home's tweets
HOME_TWEET_NUM = 5
# 'allrt': default number of retweets
RETWEETS_SHOW_NUM = 5
# 'inbox','sent': default number of direct message
MESSAGES_DISPLAY = 5
# 'trend': max trending topics
TREND_MAX = 10
# 'switch': Filter and Ignore list ex: ['@fat','@mdo']
ONLY_LIST = []
IGNORE_LIST = []

# Autocomplete history file name
HISTORY_FILENAME = 'completer.hist'

USER_DOMAIN = 'userstream.twitter.com'
PUBLIC_DOMAIN = 'stream.twitter.com'
SITE_DOMAIN = 'sitestream.twitter.com'
DOMAIN = USER_DOMAIN

# Image config
IMAGE_SHIFT = 10
IMAGE_MAX_HEIGHT = 40

# Load colorset
COLOR_SET = ['colorset.default']
modules = map(__import__, COLOR_SET)

# Load json config
rainbow_config = os.environ.get(
    'HOME', os.environ.get('USERPROFILE',''))
    + os.sep + '.rainbow_config.json'
try:
    if os.path.exists(rainbow_config):
        data = json.load(open(rainbow_config))
        for d in data:
            locals()[d] = data[d]
except:
    pass


