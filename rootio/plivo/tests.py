import tempfile
import unittest
from should_dsl import should
from rootio.plivo.menu import Menu

__author__ = 'kenneth'

dummy_menu = {
    'program': 1, 'station': 1,
    'actions': {
        'call_host': {'listen_to': 1, 'related_media': [], 'order': 0},
        'play_music': {'listen_to': 2, 'related_media': [], 'order': 1},
        'hang_up': {'listen_to': 9, 'order': 2}
    }
}

class MenuTransitionTest(unittest.TestCase):
    def setUp(self):
        self.menu = Menu(menu=dummy_menu)

    def test_it_runs_when_transition_occurs(self):
        self.menu.initial_state | should | be(None)
        self.menu.listen_to_choice()
        self.menu.initial_state | should | be(self.menu.states[0])


if __name__=='__main__':
    unittest.main()