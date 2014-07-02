import json
import re
import os
import os.path
from twitter.util import printNicely

# Regular expression for comments
comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

def load_config(filepath):
    try:
        with open(filepath) as f:
            content = ''.join(f.readlines())
            match = comment_re.search(content)
            while match:
                content = content[:match.start()] + content[match.end():]
                match = comment_re.search(content)
        data = json.loads(content)
        for d in data:
            globals()[d] = data[d]
    except:
        pass

DOMAIN = USER_DOMAIN

# Image config
IMAGE_SHIFT = 10
IMAGE_MAX_HEIGHT = 40

# Load colorset
default_config = 'rainbowstream/colorset/default.json'
rainbow_config = os.environ.get('HOME', os.environ.get('USERPROFILE','')) + os.sep + '.rainbow_config.json'
load_config(default_config)
load_config(rainbow_config)
