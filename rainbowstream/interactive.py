import readline
import rlcompleter

class RainbowCompleter(object):

    def __init__(self, options):
        """
        Init
        """
        self.options = sorted(options)
        return

    def complete(self, text, state):
        """
        Complete
        """
        response = None
        if state == 0:
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response


def init_interactive_shell(set):
    """
    Init the rainbow shell
    """
    readline.set_completer(RainbowCompleter(set).complete)
    readline.parse_and_bind('set editing-mode vi')
    readline.parse_and_bind("set input-meta on")
    readline.parse_and_bind("set convert-meta off")
    readline.parse_and_bind("set output-meta on")
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")