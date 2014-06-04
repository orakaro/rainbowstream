import readline
import rlcompleter

class RainbowCompleter(object):

    def __init__(self, options):
        """
        Init
        """
        self.options = options
        self.current_candidates = []
        return

    def complete(self, text, state):
        """
        Complete
        """
        response = None
        if state == 0:
            origline = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()
            being_completed = origline[begin:end]
            words = origline.split()

            if not words:
                self.current_candidates = sorted(self.options.keys())
            else:
                try:
                    if begin == 0:
                        candidates = self.options.keys()
                    else:
                        first = words[0]
                        candidates = self.options[first]

                    if being_completed:
                        self.current_candidates = [ w for w in candidates
                                                    if w.startswith(being_completed) ]
                    else:
                        self.current_candidates = candidates

                except (KeyError, IndexError), err:
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        return response


def init_interactive_shell(d):
    """
    Init the rainbow shell
    """
    readline.set_completer(RainbowCompleter(d).complete)
    readline.parse_and_bind('set editing-mode vi')
    readline.parse_and_bind("set input-meta on")
    readline.parse_and_bind("set convert-meta off")
    readline.parse_and_bind("set output-meta on")
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

