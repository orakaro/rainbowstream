import json
import re
import os
import os.path
from collections import OrderedDict

# Regular expression for comments in config file
comment_re = re.compile(
    '(^)[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

# Config dictionary
c = {}


def fixup(adict, k, v):
    """
    Fix up a key in json format
    """
    for key in adict.keys():
        if key == k:
            adict[key] = v
        elif isinstance(adict[key], dict):
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
    try:
        path = os.path.expanduser("~") + os.sep + '.rainbow_config.json'
        data = load_config(path)
        # Hard to set from prompt
        data.pop('ONLY_LIST', None)
        data.pop('IGNORE_LIST', None)
        data.pop('FORMAT', None)
        data.pop('QUOTE_FORMAT', None)
        data.pop('NOTIFY_FORMAT', None)
        return data
    except:
        return []


def get_default_config(key):
    """
    Get default value of a config key
    """
    try:
        path = os.path.dirname(__file__) + '/colorset/config'
        data = load_config(path)
        return data[key]
    except:
        raise Exception('This config key does not exist in default.')


def get_config(key):
    """
    Get current value of a config key
    """
    return c[key]


def set_config(key, value):
    """
    Set a config key with specific value
    """
    # Modify value
    if value.isdigit():
        value = int(value)
    elif value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    # Update global config
    c[key] = value
    # Load current user config
    path = os.path.expanduser("~") + os.sep + '.rainbow_config.json'
    data = {}
    try:
        data = load_config(path)
    except:
        return
    # Update config file
    if key in data:
        fixup(data, key, value)
    else:
        data[key] = value
    # Save
    with open(path, 'w') as out:
        json.dump(data, out, indent=4)
    os.system('chmod 777 ' + path)


def delete_config(key):
    """
    Delete a config key
    """
    path = os.path.expanduser("~") + os.sep + '.rainbow_config.json'
    try:
        data = load_config(path)
    except:
        raise Exception('Config file is messed up.')
    # Drop key
    if key in data and key in c:
        data.pop(key)
        c.pop(key)
        try:
            data[key] = c[key] = get_default_config(key)
        except:
            pass
    else:
        raise Exception('No such config key.')
    # Save
    with open(path, 'w') as out:
        json.dump(data, out, indent=4)
    os.system('chmod 777 ' + path)


def reload_config():
    """
    Reload config
    """
    try:
        rainbow_config = os.path.expanduser("~") + \
            os.sep + '.rainbow_config.json'
        data = load_config(rainbow_config)
        for d in data:
            c[d] = data[d]
    except:
        raise Exception('Can not reload config file with wrong format.')


def init_config():
    """
    Init configuration
    """
    # Load the initial config
    config = os.path.dirname(__file__) + \
        '/colorset/config'
    try:
        data = load_config(config)
        for d in data:
            c[d] = data[d]
    except:
        pass
    # Load user's config
    rainbow_config = os.path.expanduser("~") + os.sep + '.rainbow_config.json'
    try:
        data = load_config(rainbow_config)
        for d in data:
            c[d] = data[d]
    except (IOError, ValueError) as e:
        c['USER_JSON_ERROR'] = str(e)
    # Load default theme
    theme_file = os.path.dirname(__file__) + \
        '/colorset/' + c['THEME'] + '.json'
    try:
        data = load_config(theme_file)
        for d in data:
            c[d] = data[d]
    except:
        pass


# Init config
init_config()
