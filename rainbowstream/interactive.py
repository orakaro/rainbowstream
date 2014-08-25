import readline
import os.path

from .config import *


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
                self.current_candidates = sorted([c for c in self.options])
            else:
                try:
                    if begin == 0:
                        candidates = [c for c in self.options]
                    elif words[-1] in self.options[words[0]]:
                        candidates = []
                    else:
                        first = words[0]
                        candidates = self.options[first]

                    if being_completed:
                        self.current_candidates = [w for w in candidates
                                                   if w.startswith(being_completed)]
                    else:
                        self.current_candidates = candidates

                except (KeyError, IndexError):
                    self.current_candidates = []

        try:
            response = self.current_candidates[state]
        except IndexError:
            response = None
        return response


def get_history_items():
    """
    Get all history item
    """
    return [
        readline.get_history_item(i)
        for i in xrange(1, readline.get_current_history_length() + 1)
    ]


def read_history():
    """
    Read history file
    """
    try:
        readline.read_history_file(c['HISTORY_FILENAME'])
    except:
        pass


def save_history():
    """
    Save history to file
    """
    try:
        readline.write_history_file(c['HISTORY_FILENAME'])
    except:
        pass


def init_interactive_shell(d):
    """
    Init the rainbow shell
    """
    readline.set_completer(RainbowCompleter(d).complete)
    readline.parse_and_bind('set skip-completed-text on')
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
