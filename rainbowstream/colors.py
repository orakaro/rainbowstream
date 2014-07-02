import random
import itertools
from functools import wraps
from pyfiglet import figlet_format


def basic_color(code):
    """
    16 colors supported
    """
    def inner(text, bold=True):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner


def RGB(code):
    """
    256 colors supported
    """
    def inner(text, bold=True):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[38;5;%sm%s\033[0m" % (c, text)
    return inner


default          = basic_color('39')
black            = basic_color('30')
red              = basic_color('31')
green            = basic_color('32')
yellow           = basic_color('33')
blue             = basic_color('34')
magenta          = basic_color('35')
cyan             = basic_color('36')
grey             = basic_color('90')
light_red        = basic_color('91')
light_green      = basic_color('92')
light_yellow     = basic_color('93')
light_blue       = basic_color('94')
light_magenta    = basic_color('95')
light_cyan       = basic_color('96')
white            = basic_color('97')

on_default       = basic_color('49')
on_black         = basic_color('40')
on_red           = basic_color('41')
on_green         = basic_color('42')
on_yellow        = basic_color('43')
on_blue          = basic_color('44')
on_magenta       = basic_color('45')
on_cyan          = basic_color('46')
on_grey          = basic_color('100')
on_light_red     = basic_color('101')
on_light_green   = basic_color('102')
on_light_yellow  = basic_color('103')
on_light_blue    = basic_color('104')
on_light_magenta = basic_color('105')
on_light_cyan    = basic_color('106')
on_white         = basic_color('107')

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
