import json
import re
import os
import os.path
from collections import OrderedDict

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

def load_config(filepath):
    """
    Load config from filepath
    """
    with open(filepath) as f:
        content = ''.join(f.readlines())
        match = comment_re.search(content)
        while match:
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)
    return json.loads(content, object_pairs_hook=OrderedDict)

# Config dictionary
c = {}

# Load the initial config
config = os.path.dirname(
    __file__) + '/colorset/config'
try:
    data = load_config(config)
    for d in data:
        c[d] = data[d]
except:
    pass

# Load user's config
rainbow_config = os.environ.get(
    'HOME',
    os.environ.get(
        'USERPROFILE',
        '')) + os.sep + '.rainbow_config.json'
try:
    data = load_config(rainbow_config)
    for d in data:
        c[d] = data[d]
except:
    print('It seems that ~/.rainbow_config.json has wrong format :(')

# Load default theme
theme_file = os.path.dirname(
    __file__) + '/colorset/' + c['THEME'] + '.json'
try:
    data = load_config(theme_file)
    for d in data:
        c[d] = data[d]
except:
    pass
