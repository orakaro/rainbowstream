import readline


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
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
