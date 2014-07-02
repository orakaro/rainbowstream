import random
import itertools
from functools import wraps
from termcolor import *
from pyfiglet import figlet_format

def color_code(code):
    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner

default          = color_code('39')
black            = color_code('30')
red              = color_code('31')
green            = color_code('32')
yellow           = color_code('33')
blue             = color_code('34')
magenta          = color_code('35')
cyan             = color_code('36')
grey             = color_code('90')
light_red        = color_code('91')
light_green      = color_code('92')
light_yellow     = color_code('103')
light_blue       = color_code('104')
light_magenta    = color_code('105')
light_cyan       = color_code('106')
white            = color_code('107')

on_default       = color_code('49')
on_black         = color_code('40')
on_red           = color_code('41')
on_green         = color_code('42')
on_yellow        = color_code('43')
on_blue          = color_code('44')
on_magenta       = color_code('45')
on_cyan          = color_code('46')
on_grey          = color_code('100')
on_light_red     = color_code('101')
on_light_green   = color_code('102')
on_light_yellow  = color_code('103')
on_light_blue    = color_code('104')
on_light_magenta = color_code('105')
on_light_cyan    = color_code('106')
on_white         = color_code('107')

colors_shuffle = [
    grey,
    light_red,
    light_green,
    light_yellow,
    light_blue,
    light_magenta,
    light_cyan]
background_shuffle = [
    on_grey,
    on_light_red,
    on_light_green,
    on_light_yellow,
    on_light_blue,
    on_light_magenta,
    on_light_cyan]
cyc = itertools.cycle(colors_shuffle[1:])


def order_rainbow(s):
    """
    Print a string with ordered color with each character
    """
    c = [colors_shuffle[i % 7](s[i]) for i in xrange(len(s))]
    return reduce(lambda x, y: x + y, c)


def random_rainbow(s):
    """
    Print a string with random color with each character
    """
    c = [random.choice(colors_shuffle)(i) for i in s]
    return reduce(lambda x, y: x + y, c)


def Memoize(func):
    """
    Memoize decorator
    """
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


@Memoize
def cycle_color(s):
    """
    Cycle the colors_shuffle
    """
    return next(cyc)(s)


def ascii_art(text):
    """
    Draw the Ascii Art
    """
    fi = figlet_format(text, font='doom')
    print('\n'.join(
        [next(cyc)(i) for i in fi.split('\n')]
    )
    )
