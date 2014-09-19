def basic_color(code):
    """
    16 colors supported
    """
    def inner(text, rl=False):
        """
        Every raw_input with color sequences should be called with
        rl=True to avoid readline messed up the length calculation
        """
        c = code
        if rl:
            return "\001\033[%sm\002%s\001\033[0m\002" % (c, text)
        else:
            return "\033[%sm%s\033[0m" % (c, text)
    return inner


def term_color(code):
    """
    256 colors supported
    """
    def inner(text, rl=False):
        """
        Every raw_input with color sequences should be called with
        rl=True to avoid readline messed up the length calculation
        """
        c = code
        if rl:
            return "\001\033[38;5;%sm\002%s\001\033[0m\002" % (c, text)
        else:
            return "\033[38;5;%sm%s\033[0m" % (c, text)
    return inner


"""
16 basic colors
"""
default = basic_color('39')
black = basic_color('30')
red = basic_color('31')
green = basic_color('32')
yellow = basic_color('33')
blue = basic_color('34')
magenta = basic_color('35')
cyan = basic_color('36')
grey = basic_color('90')
light_red = basic_color('91')
light_green = basic_color('92')
light_yellow = basic_color('93')
light_blue = basic_color('94')
light_magenta = basic_color('95')
light_cyan = basic_color('96')
white = basic_color('97')

"""
16 basic colors on background
"""
on_default = basic_color('49')
on_black = basic_color('40')
on_red = basic_color('41')
on_green = basic_color('42')
on_yellow = basic_color('43')
on_blue = basic_color('44')
on_magenta = basic_color('45')
on_cyan = basic_color('46')
on_grey = basic_color('100')
on_light_red = basic_color('101')
on_light_green = basic_color('102')
on_light_yellow = basic_color('103')
on_light_blue = basic_color('104')
on_light_magenta = basic_color('105')
on_light_cyan = basic_color('106')
on_white = basic_color('107')
