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
        os.system(build + " >/dev/null 2>&1")
    image_c = ctypes.cdll.LoadLibrary(library)
    image_c.init()
    return image_c.rgb_to_ansi

rgb2short = call_c()


def pixel_print(ansicolor):
    """
    Print a pixel with given Ansi color
    """
    sys.stdout.write('\033[48;5;%sm \033[0m' % (ansicolor))


def block_print(lower, higher):
    """
    Print two pixels arranged above each other with Ansi color.
    Abuses Unicode to print two pixels in the space of one terminal block.
    """
    sys.stdout.write('\033[38;5;%sm\033[48;5;%sm▄\033[0m' % (higher, lower))


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

    for real_y in xrange(height // 2):
        sys.stdout.write(' ' * start)
        for x in xrange(width):
            y = real_y * 2
            p0 = i.getpixel((x, y))
            p1 = i.getpixel((x, y+1))
            r0, g0, b0 = p0[:3]
            r1, g1, b1 = p1[:3]
            block_print(rgb2short(r0, g0, b0), rgb2short(r1, g1, b1))
        sys.stdout.write('\n')


"""
For direct using purpose
"""
if __name__ == '__main__':
    image_to_display(sys.argv[1])
