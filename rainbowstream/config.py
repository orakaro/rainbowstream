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

def fixup(adict, k, v):
    """
    Fix up a key in json format
    """
    for key in adict.keys():
        if key == k:
            adict[key] = v
        elif type(adict[key]) is dict:
            fixup(adict[key], k, v)


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


def get_all_config():
    """
    Get all config
    """
    path = os.environ.get(
        'HOME',
        os.environ.get(
            'USERPROFILE',
            '')) + os.sep + '.rainbow_config.json'
    return load_config(path)


def get_default_config(key):
    """
    Get default value of a config key
    """
    path = os.path.dirname(
        __file__) + '/colorset/config'
    data = load_config(path)
    return data[key]


def get_config(key):
    """
    Get current value of a config key
    """
    return c[key]


def set_config(key,value):
    """
    Set a config key with specific value
    """
    # Modify value
    if value.isdigit():
        value = int(value)
    if value.lower() == 'True':
        value = True
    elif value.lower() == 'False':
        value = False
    # Fix up
    path = os.environ.get(
        'HOME',
        os.environ.get(
            'USERPROFILE',
            '')) + os.sep + '.rainbow_config.json'
    data = load_config(path)
    fixup(data, key, value)
    # Save
    with open(path, 'w') as out:
        json.dump(data, out, indent = 4)
    os.system('chmod 777 ' + path)


def reload_config():
    """
    Reload config
    """
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
