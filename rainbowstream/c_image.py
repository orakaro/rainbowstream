from PIL import Image
from os.path import join, dirname, getmtime, exists, expanduser
from .config import *
from .py3patch import *

import ctypes
import sys
import os


def call_c():
    """
    Call the C program for converting RGB to Ansi colors
    """
    library = expanduser('~/.image.so')
    sauce = join(dirname(__file__), 'image.c')
    if not exists(library) or getmtime(sauce) > getmtime(library):
        build = "cc -fPIC -shared -o %s %s" % (library, sauce)
        assert os.system(build + " >/dev/null 2>&1") == 0
    image_c = ctypes.cdll.LoadLibrary(library)
    image_c.init()
    return image_c.rgb_to_ansi

rgb2short = call_c()


def pixel_print(ansicolor):
    """
    Print a pixel with given Ansi color
    """
    sys.stdout.write('\033[48;5;%sm \033[0m' % (ansicolor))


def image_to_display(path, start=None, length=None):
    """
    Display an image
    """
    rows, columns = os.popen('stty size', 'r').read().split()
    if not start:
        start = c['IMAGE_SHIFT']
    if not length:
        length = int(columns) - 2 * start
    i = Image.open(path)
    i = i.convert('RGBA')
    w, h = i.size
    i.load()
    width = min(w, length)
    height = int(float(h) * (float(width) / float(w)))
    height //= 2
    i = i.resize((width, height), Image.ANTIALIAS)
    height = min(height, c['IMAGE_MAX_HEIGHT'])

    for y in xrange(height):
        sys.stdout.write(' ' * start)
        for x in xrange(width):
            p = i.getpixel((x, y))
            r, g, b = p[:3]
            pixel_print(rgb2short(r, g, b))
        sys.stdout.write('\n')


"""
For direct using purpose
"""
if __name__ == '__main__':
    image_to_display(sys.argv[1])
