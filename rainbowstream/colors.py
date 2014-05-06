import random, itertools
from functools import wraps
from termcolor import *
from pyfiglet import figlet_format

grey    = lambda x: colored(x, 'grey', attrs=['bold'])
red     = lambda x: colored(x, 'red', attrs=['bold'])
green   = lambda x: colored(x, 'green', attrs=['bold'])
yellow  = lambda x: colored(x, 'yellow', attrs=['bold'])
blue    = lambda x: colored(x, 'blue', attrs=['bold'])
magenta = lambda x: colored(x, 'magenta', attrs=['bold'])
cyan    = lambda x: colored(x, 'cyan', attrs=['bold'])
white   = lambda x: colored(x, 'white', attrs=['bold'])

on_grey    = lambda x: colored(x, 'white', 'on_grey', attrs=['bold'])
on_red     = lambda x: colored(x, 'white', 'on_red', attrs=['bold'])
on_green   = lambda x: colored(x, 'white', 'on_green', attrs=['bold'])
on_yellow  = lambda x: colored(x, 'white', 'on_yellow', attrs=['bold'])
on_blue    = lambda x: colored(x, 'white', 'on_blue', attrs=['bold'])
on_magenta = lambda x: colored(x, 'white', 'on_magenta', attrs=['bold'])
on_cyan    = lambda x: colored(x, 'white', 'on_cyan', attrs=['bold'])
on_white   = lambda x: colored(x, 'white', 'on_white', attrs=['bold'])

colors_shufle = [grey, red, green, yellow, blue, magenta, cyan]
background_shufle = [on_grey, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan]
cyc = itertools.cycle(colors_shufle[1:])


def order_rainbow(s):
    """
    Print a string with ordered color with each character
    """
    c = [colors_shufle[i%7](s[i]) for i in xrange(len(s))]
    return reduce(lambda x,y: x+y, c)

def random_rainbow(s):
    """
    Print a string with random color with each character
    """
    c = [random.choice(colors_shufle)(i) for i in s]
    return reduce(lambda x,y: x+y, c)

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
    Cycle the colors_shufle
    """
    return next(cyc)(s)

def ascii_art():
    """
    Draw the Ascii Art
    """
    fi = figlet_format('Rainbow Stream', font='doom')
    print('\n'.join(
            [next(cyc)(i) for i in fi.split('\n')]
        )
    )

